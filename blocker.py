"""
blocker.py
==========
Logica di blocco di FocusBlock:
 - gestione della configurazione persistente (config.json)
 - calcolo della fascia oraria di blocco attiva
 - chiamate alle API REST di AdGuard Home per:
     * blocco/sblocco domini (filtering user rules)
     * blocco/sblocco dispositivi (access list)
 - discovery dei dispositivi in rete tramite la ARP table del Pi

Tutto il modulo NON solleva eccezioni verso l'esterno per le operazioni di
rete: ritorna sempre tuple (ok: bool, messaggio: str) cosicché la UI possa
mostrare messaggi di errore chiari (AdGuard non raggiungibile, ecc.).
"""

import os
import re
import json
import time
import uuid
import socket
import threading
import datetime
import subprocess
from urllib.parse import urlparse

import requests

# --------------------------------------------------------------------------
# Percorsi e costanti
# --------------------------------------------------------------------------

# La cartella del modulo: funziona sia in sviluppo sia su /home/pi/focusblock
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

# Lock per evitare letture/scritture concorrenti su config.json
# (lo scheduler in background e le richieste Flask girano in thread diversi)
_config_lock = threading.RLock()

# Timeout di default per le chiamate ad AdGuard (secondi)
_AG_TIMEOUT = 6

# Configurazione di default: usata come base e per il merge con il file.
DEFAULT_CONFIG = {
    "adguard": {
        "url": "http://192.168.1.200:3000",
        "username": "",
        "password": "",
    },
    "session_minutes": 30,   # durata accesso dashboard dopo quiz superato
    "unlock_minutes": 30,    # durata sblocco temporaneo siti dopo quiz superato
    "quiz": {
        # Numero di domande pescate: pensato per coprire 10-20 minuti di
        # risposta effettiva. Nessun timer (il quiz si può lasciare aperto).
        "num_questions": 20,
        "pass_threshold": 70,  # soglia di superamento in percentuale
    },
    # Lista dei siti gestiti da FocusBlock: [{"domain": "...", "ip": "..."}]
    "blocked_sites": [],
    # IP dei dispositivi gestiti: bloccati su AdGuard solo durante la fascia
    "blocked_devices": [],
    # Timestamp epoch fino al quale i siti restano sbloccati temporaneamente
    "unlock_until": 0,
    # Secret key Flask generata in fase di installazione
    "secret_key": "",
}


# --------------------------------------------------------------------------
# Gestione configurazione
# --------------------------------------------------------------------------

def _deep_merge(base, override):
    """Merge ricorsivo: i valori di `override` vincono, ma le chiavi mancanti
    vengono prese da `base`. Necessario per mantenere i default sui dict
    annidati (adguard, schedule, quiz)."""
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def load_config():
    """Carica config.json applicando i default. Non solleva mai eccezioni:
    se il file è assente o corrotto ritorna la configurazione di default."""
    with _config_lock:
        data = {}
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (ValueError, OSError):
                # File corrotto o illeggibile: ripartiamo dai default
                data = {}
        cfg = _deep_merge(DEFAULT_CONFIG, data)
        _migrate_schedules(cfg)
        return cfg


def _new_id():
    """Identificativo breve per una voce di pianificazione."""
    return uuid.uuid4().hex[:8]


def _migrate_schedules(cfg):
    """Garantisce la presenza di `cfg['schedules']` (lista di pianificazioni).

    - Se esiste già `schedules`, la mantiene (rimuovendo il vecchio `schedule`).
    - Se esiste solo il vecchio `schedule` singolo, lo converte in una voce
      settimanale.
    - Se non c'è nulla, crea una pianificazione settimanale di default
      (Lun-Ven 14:00-18:00, disattivata)."""
    if isinstance(cfg.get("schedules"), list):
        cfg.pop("schedule", None)
        return

    legacy = cfg.get("schedule")
    if legacy:
        cfg["schedules"] = [{
            "id": _new_id(),
            "type": "weekly",
            "enabled": legacy.get("enabled", True),
            "days": legacy.get("days", [0, 1, 2, 3, 4]),
            "start": legacy.get("start", "14:00"),
            "end": legacy.get("end", "18:00"),
        }]
    else:
        cfg["schedules"] = [{
            "id": _new_id(),
            "type": "weekly",
            "enabled": False,
            "days": [0, 1, 2, 3, 4],
            "start": "14:00",
            "end": "18:00",
        }]
    cfg.pop("schedule", None)


def save_config(cfg):
    """Salva la configurazione completa su config.json in modo atomico."""
    with _config_lock:
        tmp_path = CONFIG_PATH + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, CONFIG_PATH)


# --------------------------------------------------------------------------
# Logica della fascia oraria
# --------------------------------------------------------------------------

def _parse_hhmm(value, default):
    """Converte 'HH:MM' in datetime.time, con fallback in caso di errore."""
    try:
        hh, mm = value.split(":")
        return datetime.time(int(hh), int(mm))
    except (ValueError, AttributeError):
        return default


def _in_window(current, start, end):
    """True se `current` (time) è nella finestra [start, end). Gestisce anche
    le finestre che attraversano la mezzanotte (end <= start)."""
    if start <= end:
        return start <= current < end
    return current >= start or current < end


def entry_applies_on_day(entry, now):
    """True se la voce di pianificazione si applica al giorno di `now`
    (a prescindere dall'orario)."""
    if entry.get("type") == "once":
        return entry.get("date") == now.strftime("%Y-%m-%d")
    # weekly
    return now.weekday() in entry.get("days", [])


def entry_active_now(entry, now):
    """True se la voce di pianificazione è attiva nell'istante `now`."""
    if not entry_applies_on_day(entry, now):
        return False
    start = _parse_hhmm(entry.get("start"), datetime.time(0, 0))
    end = _parse_hhmm(entry.get("end"), datetime.time(23, 59))
    return _in_window(now.time(), start, end)


def is_blocking_active(cfg=None, now=None):
    """Ritorna True se almeno una pianificazione abilitata è attiva ora."""
    cfg = cfg or load_config()
    now = now or datetime.datetime.now()
    for entry in cfg.get("schedules", []):
        if not entry.get("enabled", True):
            continue
        if entry_active_now(entry, now):
            return True
    return False


# Etichette giorni per la descrizione testuale delle pianificazioni
_GIORNI_BREVI = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]


def describe_entry(entry):
    """Descrizione testuale leggibile di una pianificazione (per la UI)."""
    times = f"{entry.get('start', '?')}–{entry.get('end', '?')}"
    if entry.get("type") == "once":
        try:
            d = datetime.datetime.strptime(entry["date"], "%Y-%m-%d")
            return f"{d.strftime('%d/%m/%Y')} · {times}"
        except (ValueError, KeyError, TypeError):
            return f"{entry.get('date', '?')} · {times}"
    days = sorted(entry.get("days", []))
    if days == [0, 1, 2, 3, 4]:
        gg = "Lun–Ven"
    elif days == [0, 1, 2, 3, 4, 5, 6]:
        gg = "Tutti i giorni"
    elif days == [5, 6]:
        gg = "Weekend"
    elif days:
        gg = ", ".join(_GIORNI_BREVI[i] for i in days)
    else:
        gg = "nessun giorno"
    return f"{gg} · {times}"


def _valid_hhmm(value):
    """True se `value` è un orario 'HH:MM' valido."""
    try:
        hh, mm = value.split(":")
        return 0 <= int(hh) <= 23 and 0 <= int(mm) <= 59
    except (ValueError, AttributeError):
        return False


def _valid_date(value):
    """True se `value` è una data 'YYYY-MM-DD' valida."""
    try:
        datetime.datetime.strptime(value, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def add_schedule_entry(entry):
    """Valida e aggiunge una pianificazione. Ritorna (ok, messaggio)."""
    if not _valid_hhmm(entry.get("start")) or not _valid_hhmm(entry.get("end")):
        return False, "Orari non validi (usa HH:MM)."
    if entry.get("start") == entry.get("end"):
        return False, "Inizio e fine non possono coincidere."

    if entry.get("type") == "once":
        if not _valid_date(entry.get("date")):
            return False, "Data non valida."
    elif entry.get("type") == "weekly":
        if not entry.get("days"):
            return False, "Seleziona almeno un giorno."
    else:
        return False, "Tipo di pianificazione non valido."

    entry["id"] = _new_id()
    entry.setdefault("enabled", True)

    cfg = load_config()
    cfg.setdefault("schedules", []).append(entry)
    save_config(cfg)
    apply_blocking_state(cfg)
    return True, "Pianificazione aggiunta."


def remove_schedule_entry(entry_id):
    """Rimuove una pianificazione per id. Ritorna (ok, messaggio)."""
    cfg = load_config()
    current = cfg.get("schedules", [])
    new = [e for e in current if e.get("id") != entry_id]
    if len(new) == len(current):
        return False, "Pianificazione non trovata."
    cfg["schedules"] = new
    save_config(cfg)
    apply_blocking_state(cfg)
    return True, "Pianificazione rimossa."


def set_schedule_entry_enabled(entry_id, enabled):
    """Attiva/disattiva una pianificazione per id. Ritorna (ok, messaggio)."""
    cfg = load_config()
    found = False
    for e in cfg.get("schedules", []):
        if e.get("id") == entry_id:
            e["enabled"] = bool(enabled)
            found = True
            break
    if not found:
        return False, "Pianificazione non trovata."
    save_config(cfg)
    apply_blocking_state(cfg)
    return True, ("Pianificazione attivata." if enabled else "Pianificazione disattivata.")


def prune_expired_schedules(cfg):
    """Rimuove le pianificazioni 'once' con data passata. Ritorna True se ha
    modificato la lista."""
    today = datetime.date.today().strftime("%Y-%m-%d")
    current = cfg.get("schedules", [])
    kept = [e for e in current
            if not (e.get("type") == "once" and e.get("date") and e["date"] < today)]
    if len(kept) != len(current):
        cfg["schedules"] = kept
        return True
    return False


def list_schedules(cfg=None):
    """Ritorna le pianificazioni con una descrizione leggibile pronta per la UI."""
    cfg = cfg or load_config()
    out = []
    for e in cfg.get("schedules", []):
        item = dict(e)
        item["description"] = describe_entry(e)
        out.append(item)
    return out


def is_temporarily_unlocked(cfg=None, now_ts=None):
    """True se è in corso uno sblocco temporaneo (dopo quiz superato)."""
    cfg = cfg or load_config()
    now_ts = now_ts or time.time()
    return now_ts < float(cfg.get("unlock_until", 0) or 0)


# --------------------------------------------------------------------------
# Helper per le API di AdGuard Home
# --------------------------------------------------------------------------

def _ag_base(cfg=None):
    """Ritorna (url_base, (user, password)) per le chiamate ad AdGuard."""
    cfg = cfg or load_config()
    ag = cfg.get("adguard", {})
    url = (ag.get("url") or "http://192.168.1.200:3000").rstrip("/")
    auth = (ag.get("username", ""), ag.get("password", ""))
    return url, auth


def _ag_get(path, cfg=None):
    """GET verso AdGuard, ritorna il JSON. Solleva eccezione in caso di errore
    (gestita dai chiamanti di livello superiore)."""
    base, auth = _ag_base(cfg)
    resp = requests.get(base + path, auth=auth, timeout=_AG_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def _ag_post(path, payload, cfg=None):
    """POST JSON verso AdGuard. Solleva eccezione in caso di errore."""
    base, auth = _ag_base(cfg)
    resp = requests.post(base + path, json=payload, auth=auth, timeout=_AG_TIMEOUT)
    resp.raise_for_status()
    return resp


def test_adguard(cfg=None):
    """Verifica la raggiungibilità e le credenziali di AdGuard.
    Ritorna (ok, messaggio)."""
    try:
        _ag_get("/control/status", cfg)
        return True, "AdGuard raggiungibile"
    except requests.exceptions.RequestException as exc:
        return False, _ag_error_message(exc)


def _ag_error_message(exc):
    """Traduce un'eccezione requests in un messaggio leggibile in italiano."""
    if isinstance(exc, requests.exceptions.ConnectionError):
        return "AdGuard Home non raggiungibile (connessione rifiutata)."
    if isinstance(exc, requests.exceptions.Timeout):
        return "AdGuard Home non risponde (timeout)."
    if isinstance(exc, requests.exceptions.HTTPError):
        code = exc.response.status_code if exc.response is not None else "?"
        if code in (401, 403):
            return "Credenziali AdGuard Home non valide (autenticazione fallita)."
        return f"AdGuard Home ha risposto con errore HTTP {code}."
    return f"Errore di comunicazione con AdGuard Home: {exc}"


# --------------------------------------------------------------------------
# Gestione domini bloccati (filtering user rules)
# --------------------------------------------------------------------------

def clean_domain(raw):
    """Normalizza l'input dell'utente in un dominio pulito.
    Rimuove schema, path, eventuale 'www.' e spazi."""
    if not raw:
        return ""
    raw = raw.strip().lower()
    # Se contiene uno schema, usiamo urlparse per estrarre l'host
    if "://" in raw:
        raw = urlparse(raw).netloc or urlparse(raw).path
    # Rimuove eventuale path residuo e porta
    raw = raw.split("/")[0].split(":")[0].strip()
    if raw.startswith("www."):
        raw = raw[4:]
    return raw


def resolve_ip(domain):
    """Risolve l'IP di un dominio via DNS. Ritorna l'IP o None se fallisce."""
    try:
        return socket.gethostbyname(domain)
    except (socket.gaierror, socket.error):
        return None


def _managed_rule(domain):
    """Regola AdGuard che blocca un dominio (e relativi sottodomini)."""
    return f"||{domain}^"


def _sync_adguard_rules(domains, enabled, cfg=None):
    """Sincronizza le regole gestite da FocusBlock su AdGuard.

    Le regole 'gestite' sono esattamente `||dominio^` per ogni dominio in
    `domains`. Vengono prima rimosse tutte le regole gestite presenti e, se
    `enabled` è True, riaggiunte. Le eventuali altre regole utente di AdGuard
    NON vengono toccate.

    Ritorna (ok, messaggio)."""
    cfg = cfg or load_config()
    try:
        status = _ag_get("/control/filtering/status", cfg)
    except requests.exceptions.RequestException as exc:
        return False, _ag_error_message(exc)

    current_rules = status.get("user_rules", []) or []
    managed = {_managed_rule(d) for d in domains}

    # Rimuoviamo tutte le nostre regole gestite dall'elenco corrente
    new_rules = [r for r in current_rules if r.strip() not in managed]

    if enabled:
        # Le riaggiungiamo in fondo (ordinate per stabilità)
        new_rules.extend(sorted(managed))

    # Aggiorniamo solo se c'è una differenza effettiva
    if new_rules != current_rules:
        try:
            _ag_post("/control/filtering/set_rules", {"rules": new_rules}, cfg)
        except requests.exceptions.RequestException as exc:
            return False, _ag_error_message(exc)

    return True, "Regole sincronizzate"


def apply_blocking_state(cfg=None):
    """Applica lo stato di blocco corrente su AdGuard in base a:
     - fascia oraria attiva
     - eventuale sblocco temporaneo in corso

    Sincronizza sia i domini bloccati sia i dispositivi gestiti: entrambi
    vengono attivati su AdGuard solo durante la fascia oraria (e disattivati
    fuori orario o durante lo sblocco temporaneo post-quiz).

    Chiamata sia dallo scheduler (ogni minuto) sia dopo modifiche puntuali.
    Ritorna (ok, messaggio, should_block)."""
    cfg = cfg or load_config()

    # Pulizia delle pianificazioni "once" ormai scadute
    if prune_expired_schedules(cfg):
        save_config(cfg)

    should_block = is_blocking_active(cfg) and not is_temporarily_unlocked(cfg)

    # Domini
    domains = [s.get("domain") for s in cfg.get("blocked_sites", []) if s.get("domain")]
    ok_sites, msg_sites = _sync_adguard_rules(domains, should_block, cfg)

    # Dispositivi (seguono la stessa fascia oraria dei siti)
    device_ips = [ip for ip in cfg.get("blocked_devices", []) if ip]
    ok_dev, msg_dev = _sync_adguard_devices(device_ips, should_block, cfg)

    ok = ok_sites and ok_dev
    msg = msg_sites if not ok_sites else (msg_dev if not ok_dev else "Stato applicato")
    return ok, msg, should_block


def add_blocked_site(raw_domain):
    """Aggiunge un dominio alla blocklist gestita. Risolve l'IP via DNS
    (a scopo informativo) e applica subito lo stato di blocco.
    Ritorna (ok, messaggio)."""
    domain = clean_domain(raw_domain)
    if not domain or "." not in domain:
        return False, "Dominio non valido."

    cfg = load_config()
    existing = {s.get("domain") for s in cfg.get("blocked_sites", [])}
    if domain in existing:
        return False, f"Il dominio '{domain}' è già in lista."

    ip = resolve_ip(domain)
    cfg.setdefault("blocked_sites", []).append({
        "domain": domain,
        "ip": ip or "non risolto",
    })
    save_config(cfg)

    # Applica subito lo stato (la regola verrà attivata solo se la fascia è attiva)
    ok, msg, _ = apply_blocking_state(cfg)
    if not ok:
        # Il dominio è salvato in config ma AdGuard non è raggiungibile
        return False, f"Dominio salvato, ma AdGuard non aggiornato: {msg}"

    if ip:
        return True, f"Dominio '{domain}' aggiunto (IP risolto: {ip})."
    return True, f"Dominio '{domain}' aggiunto (IP non risolto, blocco per nome attivo)."


def remove_blocked_site(domain):
    """Rimuove un dominio dalla blocklist gestita. Ritorna (ok, messaggio)."""
    domain = clean_domain(domain)
    cfg = load_config()
    sites = cfg.get("blocked_sites", [])
    new_sites = [s for s in sites if s.get("domain") != domain]
    if len(new_sites) == len(sites):
        return False, f"Il dominio '{domain}' non è in lista."

    cfg["blocked_sites"] = new_sites
    save_config(cfg)

    # Rimuoviamo esplicitamente la regola da AdGuard: il dominio non è più
    # gestito, quindi la sincronizzazione periodica non lo toccherebbe più.
    rule = _managed_rule(domain)
    try:
        status = _ag_get("/control/filtering/status", cfg)
        rules = status.get("user_rules", []) or []
        if any(r.strip() == rule for r in rules):
            _ag_post("/control/filtering/set_rules",
                     {"rules": [r for r in rules if r.strip() != rule]}, cfg)
    except requests.exceptions.RequestException as exc:
        return False, f"Dominio rimosso da FocusBlock, ma AdGuard non aggiornato: {_ag_error_message(exc)}"

    return True, f"Dominio '{domain}' rimosso."


def list_blocked_sites(cfg=None):
    """Ritorna la lista dei siti gestiti (dalla config, fonte di verità)."""
    cfg = cfg or load_config()
    return cfg.get("blocked_sites", [])


# --------------------------------------------------------------------------
# Gestione dispositivi (access list di AdGuard)
# --------------------------------------------------------------------------

def get_access_list(cfg=None):
    """Recupera l'access list di AdGuard. Ritorna (ok, dict|messaggio)."""
    try:
        data = _ag_get("/control/access/list", cfg)
        # Garantiamo la presenza di tutte le chiavi
        data.setdefault("allowed_clients", [])
        data.setdefault("disallowed_clients", [])
        data.setdefault("blocked_hosts", [])
        return True, data
    except requests.exceptions.RequestException as exc:
        return False, _ag_error_message(exc)


def _set_access_list(data, cfg=None):
    """Imposta l'access list completa su AdGuard."""
    payload = {
        "allowed_clients": data.get("allowed_clients", []),
        "disallowed_clients": data.get("disallowed_clients", []),
        "blocked_hosts": data.get("blocked_hosts", []),
    }
    _ag_post("/control/access/set", payload, cfg)


def _sync_adguard_devices(device_ips, enabled, cfg=None):
    """Sincronizza i dispositivi gestiti da FocusBlock nella disallowed_clients
    di AdGuard. Gestisce SOLO gli IP indicati: vengono prima rimossi e, se
    `enabled` è True, riaggiunti. Eventuali altri IP bloccati esternamente
    NON vengono toccati. Ritorna (ok, messaggio)."""
    cfg = cfg or load_config()
    ok, data = get_access_list(cfg)
    if not ok:
        return False, data  # data contiene il messaggio d'errore

    managed = set(device_ips)
    current = list(data.get("disallowed_clients", []))

    # Togliamo i nostri IP gestiti dall'elenco corrente
    new_list = [c for c in current if c not in managed]
    if enabled:
        new_list.extend(sorted(managed))

    if new_list != current:
        data["disallowed_clients"] = new_list
        try:
            _set_access_list(data, cfg)
        except requests.exceptions.RequestException as exc:
            return False, _ag_error_message(exc)

    return True, "Dispositivi sincronizzati"


def manage_device(ip):
    """Aggiunge un dispositivo alla lista gestita (verrà bloccato durante la
    fascia oraria) e applica subito lo stato. Ritorna (ok, messaggio)."""
    ip = (ip or "").strip()
    if not _is_valid_ip(ip):
        return False, "Indirizzo IP non valido."

    cfg = load_config()
    lst = cfg.setdefault("blocked_devices", [])
    if ip in lst:
        return False, f"Il dispositivo {ip} è già gestito."
    lst.append(ip)
    save_config(cfg)

    ok, msg, blocking = apply_blocking_state(cfg)
    if not ok:
        return False, f"Dispositivo salvato, ma AdGuard non aggiornato: {msg}"
    if blocking:
        return True, f"Dispositivo {ip} bloccato (fascia oraria attiva ora)."
    return True, f"Dispositivo {ip} aggiunto: verrà bloccato durante la fascia oraria."


def unmanage_device(ip):
    """Rimuove un dispositivo dalla lista gestita (e lo sblocca subito su
    AdGuard se era bloccato). Ritorna (ok, messaggio)."""
    ip = (ip or "").strip()
    cfg = load_config()
    lst = cfg.get("blocked_devices", [])
    if ip not in lst:
        return False, f"Il dispositivo {ip} non è gestito."
    cfg["blocked_devices"] = [x for x in lst if x != ip]
    save_config(cfg)

    # Togliamo esplicitamente l'IP da AdGuard: non essendo più gestito, la
    # sincronizzazione periodica non lo rimuoverebbe.
    ok, data = get_access_list(cfg)
    if not ok:
        return False, f"Dispositivo rimosso dalla gestione, ma AdGuard non raggiungibile: {data}"
    if ip in data.get("disallowed_clients", []):
        data["disallowed_clients"] = [c for c in data["disallowed_clients"] if c != ip]
        try:
            _set_access_list(data, cfg)
        except requests.exceptions.RequestException as exc:
            return False, f"Dispositivo rimosso dalla gestione, ma AdGuard non aggiornato: {_ag_error_message(exc)}"

    return True, f"Dispositivo {ip} non più gestito (sbloccato)."


def list_managed_devices(cfg=None):
    """Ritorna la lista degli IP dei dispositivi gestiti (dalla config)."""
    cfg = cfg or load_config()
    return cfg.get("blocked_devices", [])


def _is_valid_ip(ip):
    """Validazione basilare di un indirizzo IPv4."""
    try:
        socket.inet_aton(ip)
        return ip.count(".") == 3
    except (socket.error, AttributeError):
        return False


# --------------------------------------------------------------------------
# Discovery dispositivi via ARP
# --------------------------------------------------------------------------

# Esempio riga `arp -a`:  hostname (192.168.1.1) at aa:bb:cc:dd:ee:ff [ether] on eth0
_ARP_RE = re.compile(r"^(\S+)\s+\(([\d.]+)\)\s+at\s+([0-9a-fA-F:]+|<incomplete>)")


def get_arp_devices():
    """Legge la ARP table del Pi e ritorna la lista dei dispositivi noti.
    Ritorna (ok, lista|messaggio). Ogni dispositivo: {name, ip, mac}."""
    try:
        out = subprocess.check_output(
            ["arp", "-a"], text=True, timeout=5, stderr=subprocess.DEVNULL
        )
    except FileNotFoundError:
        return False, "Comando 'arp' non disponibile sul sistema."
    except subprocess.SubprocessError:
        return False, "Impossibile leggere la ARP table."

    devices = []
    seen = set()
    for line in out.splitlines():
        match = _ARP_RE.match(line.strip())
        if not match:
            continue
        host, ip, mac = match.groups()
        if mac == "<incomplete>":
            continue  # voce ARP non risolta, la saltiamo
        if ip in seen:
            continue
        seen.add(ip)
        name = ip if host in ("?", "") else host
        devices.append({"name": name, "ip": ip, "mac": mac})

    devices.sort(key=ip_sort_key)
    return True, devices


def ip_sort_key(device_or_ip):
    """Chiave di ordinamento per IPv4. Accetta un dict {'ip':...} o una stringa.
    Gli IP non validi finiscono in fondo."""
    ip = device_or_ip["ip"] if isinstance(device_or_ip, dict) else device_or_ip
    try:
        return tuple(int(x) for x in ip.split("."))
    except (ValueError, AttributeError):
        return (999, 999, 999, 999)


def get_adguard_client_names(cfg=None):
    """Mappa IP -> nome usando i client noti ad AdGuard Home.

    AdGuard ricava i nomi dei dispositivi via rDNS/DHCP (auto_clients) e li
    espone insieme ai client configurati manualmente. È una fonte di nomi
    molto migliore della ARP table (che spesso riporta solo '?').

    Ritorna un dict {ip: nome}. In caso di errore ritorna {} (best effort)."""
    try:
        data = _ag_get("/control/clients", cfg)
    except requests.exceptions.RequestException:
        return {}

    names = {}
    # Client rilevati automaticamente (rDNS, DHCP, WHOIS)
    for c in data.get("auto_clients") or []:
        ip = c.get("ip")
        name = (c.get("name") or "").strip()
        if ip and name and name != ip:
            names[ip] = name

    # Client configurati manualmente: 'ids' può contenere IP/MAC/CIDR
    for c in data.get("clients") or []:
        name = (c.get("name") or "").strip()
        if not name:
            continue
        for ident in c.get("ids", []) or []:
            if _is_valid_ip(ident):
                names.setdefault(ident, name)

    return names

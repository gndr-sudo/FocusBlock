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
    "schedule": {
        "enabled": True,
        "start": "14:00",
        "end": "18:00",
        # Giorni della settimana attivi: 0 = Lunedì ... 6 = Domenica
        "days": [0, 1, 2, 3, 4],
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
        return _deep_merge(DEFAULT_CONFIG, data)


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


def is_blocking_active(cfg=None, now=None):
    """Ritorna True se l'orario attuale rientra nella fascia di blocco
    configurata e nel giorno della settimana selezionato."""
    cfg = cfg or load_config()
    sch = cfg.get("schedule", {})

    if not sch.get("enabled", True):
        return False

    now = now or datetime.datetime.now()

    # Giorno della settimana (0 = Lunedì)
    if now.weekday() not in sch.get("days", []):
        return False

    start = _parse_hhmm(sch.get("start"), datetime.time(14, 0))
    end = _parse_hhmm(sch.get("end"), datetime.time(18, 0))
    current = now.time()

    if start <= end:
        # Fascia normale nello stesso giorno (es. 14:00 -> 18:00)
        return start <= current < end
    # Fascia che attraversa la mezzanotte (es. 22:00 -> 06:00)
    return current >= start or current < end


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

    Chiamata sia dallo scheduler (ogni minuto) sia dopo modifiche puntuali.
    Ritorna (ok, messaggio, should_block)."""
    cfg = cfg or load_config()
    should_block = is_blocking_active(cfg) and not is_temporarily_unlocked(cfg)
    domains = [s.get("domain") for s in cfg.get("blocked_sites", []) if s.get("domain")]
    ok, msg = _sync_adguard_rules(domains, should_block, cfg)
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

    ok, msg, _ = apply_blocking_state(cfg)
    if not ok:
        return False, f"Dominio rimosso da FocusBlock, ma AdGuard non aggiornato: {msg}"
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


def is_device_blocked(ip, cfg=None):
    """Ritorna True se l'IP è nella lista disallowed_clients di AdGuard."""
    ok, data = get_access_list(cfg)
    if not ok:
        return False
    return ip in data.get("disallowed_clients", [])


def set_device_blocked(ip, blocked):
    """Blocca (blocked=True) o sblocca (blocked=False) un dispositivo
    aggiungendolo/togliendolo da disallowed_clients. Ritorna (ok, messaggio)."""
    ip = (ip or "").strip()
    if not _is_valid_ip(ip):
        return False, "Indirizzo IP non valido."

    ok, data = get_access_list()
    if not ok:
        return False, data  # data contiene il messaggio d'errore

    disallowed = list(data.get("disallowed_clients", []))

    if blocked:
        if ip in disallowed:
            return True, f"Il dispositivo {ip} è già bloccato."
        disallowed.append(ip)
    else:
        if ip not in disallowed:
            return True, f"Il dispositivo {ip} è già sbloccato."
        disallowed = [c for c in disallowed if c != ip]

    data["disallowed_clients"] = disallowed
    try:
        _set_access_list(data)
    except requests.exceptions.RequestException as exc:
        return False, _ag_error_message(exc)

    azione = "bloccato" if blocked else "sbloccato"
    return True, f"Dispositivo {ip} {azione}."


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

    devices.sort(key=lambda d: tuple(int(x) for x in d["ip"].split(".")))
    return True, devices

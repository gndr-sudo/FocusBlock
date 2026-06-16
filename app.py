"""
app.py
======
Applicazione Flask principale di FocusBlock (porta 5000).

Sezioni:
  1. Login via Quiz       -> /quiz
  2. Gestione siti        -> /sites
  3. Gestione dispositivi -> /devices
  4. Orari di blocco      -> /schedule

Logica di accesso:
  - Fuori dalla fascia di blocco  -> accesso diretto alla dashboard.
  - Dentro la fascia di blocco    -> serve superare il quiz (>=70%).
       Quiz superato -> accesso dashboard per N minuti + sblocco siti per N minuti.

Lo scheduler (APScheduler) riallinea lo stato di blocco su AdGuard ogni minuto.
"""

import os
import time
import random
import secrets
import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify,
)
from apscheduler.schedulers.background import BackgroundScheduler

import blocker
import questions

app = Flask(__name__)


# --------------------------------------------------------------------------
# Secret key di sessione
# --------------------------------------------------------------------------

def _init_secret_key():
    """Carica la secret key da config.json; se assente la genera e la salva.
    In condizioni normali viene generata dallo script di installazione."""
    cfg = blocker.load_config()
    key = cfg.get("secret_key")
    if not key:
        key = secrets.token_hex(32)
        cfg["secret_key"] = key
        blocker.save_config(cfg)
    return key


app.secret_key = _init_secret_key()


# --------------------------------------------------------------------------
# Parsing domande del quiz
# --------------------------------------------------------------------------

def parse_questions(raw):
    """Converte il testo nel formato Q/A/W (blocchi separati da '---') in una
    lista di dizionari: {question, correct, wrong: [...]}.

    Formato atteso di ogni blocco:
        Q: Testo della domanda?
        A: Risposta corretta
        W: Risposta errata 1
        W: Risposta errata 2
        W: Risposta errata 3
    """
    result = []
    if not raw:
        return result

    for block in raw.split("---"):
        q = None
        correct = None
        wrong = []
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("Q:"):
                q = line[2:].strip()
            elif line.startswith("A:"):
                correct = line[2:].strip()
            elif line.startswith("W:"):
                wrong.append(line[2:].strip())
        # Una domanda è valida se ha testo, risposta corretta e almeno 1 errata
        if q and correct and wrong:
            result.append({"question": q, "correct": correct, "wrong": wrong})
    return result


def get_all_questions():
    """Ritorna tutte le domande disponibili leggendo questions.RAW_QUESTIONS."""
    raw = getattr(questions, "RAW_QUESTIONS", "") or ""
    return parse_questions(raw)


# --------------------------------------------------------------------------
# Controllo accesso
# --------------------------------------------------------------------------

def has_valid_session():
    """True se l'utente ha una sessione di accesso ancora valida."""
    return time.time() < float(session.get("auth_until", 0) or 0)


def access_required(view):
    """Decoratore: consente l'accesso se la fascia di blocco NON è attiva,
    oppure se l'utente ha superato il quiz (sessione valida). Altrimenti
    reindirizza al quiz."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not blocker.is_blocking_active():
            return view(*args, **kwargs)
        if has_valid_session():
            return view(*args, **kwargs)
        return redirect(url_for("quiz"))
    return wrapped


# --------------------------------------------------------------------------
# Contesto comune ai template
# --------------------------------------------------------------------------

GIORNI = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]


def status_info():
    """Costruisce il dizionario di stato mostrato nella dashboard."""
    cfg = blocker.load_config()
    now = datetime.datetime.now()
    active = blocker.is_blocking_active(cfg, now)
    unlocked = blocker.is_temporarily_unlocked(cfg)

    # Minuti residui di sblocco temporaneo
    unlock_left = 0
    if unlocked:
        unlock_left = max(0, int((float(cfg.get("unlock_until", 0)) - time.time()) // 60) + 1)

    # Minuti residui di sessione dashboard
    session_left = 0
    if has_valid_session():
        session_left = max(0, int((float(session.get("auth_until", 0)) - time.time()) // 60) + 1)

    ag_ok, ag_msg = blocker.test_adguard(cfg)

    return {
        "active": active,
        "blocking_now": active and not unlocked,
        "unlocked": unlocked,
        "unlock_left": unlock_left,
        "session_left": session_left,
        "schedule": cfg.get("schedule", {}),
        "giorni": GIORNI,
        "blocked_count": len(cfg.get("blocked_sites", [])),
        "adguard_ok": ag_ok,
        "adguard_msg": ag_msg,
        "now": now.strftime("%H:%M"),
    }


@app.context_processor
def inject_globals():
    """Variabili disponibili in tutti i template."""
    return {
        "blocking_active": blocker.is_blocking_active(),
        "has_session": has_valid_session(),
    }


# --------------------------------------------------------------------------
# Rotte: Dashboard
# --------------------------------------------------------------------------

@app.route("/")
@access_required
def dashboard():
    return render_template("dashboard.html", status=status_info())


# --------------------------------------------------------------------------
# Rotte: Quiz / Login
# --------------------------------------------------------------------------

@app.route("/quiz", methods=["GET"])
def quiz():
    # Se la fascia non è attiva il quiz non serve: vai alla dashboard
    if not blocker.is_blocking_active():
        return redirect(url_for("dashboard"))
    # Se hai già una sessione valida, niente quiz
    if has_valid_session():
        return redirect(url_for("dashboard"))

    cfg = blocker.load_config()
    all_q = get_all_questions()

    # Nessuna domanda configurata: non possiamo bloccare fuori l'utente.
    # Mostriamo un avviso e consentiamo l'accesso manuale.
    if not all_q:
        return render_template("quiz.html", no_questions=True, quiz_cfg=cfg["quiz"])

    quiz_cfg = cfg.get("quiz", {})
    num = min(int(quiz_cfg.get("num_questions", 20)), len(all_q))
    selected = random.sample(all_q, num)

    # Per ogni domanda costruiamo 4 opzioni (1 corretta + fino a 3 errate) mischiate
    rendered = []
    correct_indices = []
    for q in selected:
        wrongs = list(q["wrong"])
        random.shuffle(wrongs)
        options = [q["correct"]] + wrongs[:3]
        random.shuffle(options)
        correct_indices.append(options.index(q["correct"]))
        rendered.append({"question": q["question"], "options": options})

    # In sessione salviamo solo le info necessarie alla correzione (compatto).
    # Nessun timer: il quiz si può lasciare aperto, conta solo la preparazione.
    session["quiz"] = {
        "correct": correct_indices,
        "count": len(rendered),
    }

    return render_template(
        "quiz.html",
        no_questions=False,
        questions=rendered,
        threshold=int(quiz_cfg.get("pass_threshold", 70)),
    )


@app.route("/quiz", methods=["POST"])
def quiz_submit():
    if not blocker.is_blocking_active():
        return redirect(url_for("dashboard"))

    cfg = blocker.load_config()

    # Caso "nessuna domanda": accesso manuale consentito
    all_q = get_all_questions()
    if not all_q:
        return _grant_access(cfg, motivo="nessuna domanda configurata")

    quiz_state = session.get("quiz")
    if not quiz_state:
        flash("Sessione quiz scaduta, riprova.", "warning")
        return redirect(url_for("quiz"))

    quiz_cfg = cfg.get("quiz", {})

    # Nessun limite di tempo: si procede direttamente alla correzione
    correct_indices = quiz_state.get("correct", [])
    count = quiz_state.get("count", 0)
    score = 0
    for i in range(count):
        try:
            given = int(request.form.get(f"q{i}", "-1"))
        except ValueError:
            given = -1
        if i < len(correct_indices) and given == correct_indices[i]:
            score += 1

    pct = (score / count * 100) if count else 0
    threshold = int(quiz_cfg.get("pass_threshold", 70))

    session.pop("quiz", None)

    if pct >= threshold:
        return _grant_access(cfg, score=score, count=count, pct=pct)

    flash(
        f"Quiz non superato: {score}/{count} ({pct:.0f}%). "
        f"Serve almeno il {threshold}%. Riprova.",
        "danger",
    )
    return redirect(url_for("quiz"))


def _grant_access(cfg, score=None, count=None, pct=None, motivo=None):
    """Concede l'accesso: imposta la sessione e lo sblocco temporaneo,
    poi applica subito lo stato su AdGuard."""
    now = time.time()
    session_minutes = int(cfg.get("session_minutes", 30))
    unlock_minutes = int(cfg.get("unlock_minutes", 30))

    # Sessione dashboard
    session["auth_until"] = now + session_minutes * 60
    session.permanent = False

    # Sblocco temporaneo siti
    cfg["unlock_until"] = now + unlock_minutes * 60
    blocker.save_config(cfg)

    # Applica subito lo stato (rimuove le regole di blocco da AdGuard)
    ok, msg, _ = blocker.apply_blocking_state(cfg)

    if motivo:
        flash(f"Accesso consentito ({motivo}). Siti sbloccati per {unlock_minutes} min.", "warning")
    else:
        flash(
            f"Quiz superato! {score}/{count} ({pct:.0f}%). "
            f"Dashboard e siti sbloccati per {unlock_minutes} minuti.",
            "success",
        )
    if not ok:
        flash(f"Attenzione: AdGuard non aggiornato ({msg}).", "warning")

    return redirect(url_for("dashboard"))


# --------------------------------------------------------------------------
# Rotte: Gestione siti
# --------------------------------------------------------------------------

@app.route("/sites")
@access_required
def sites():
    cfg = blocker.load_config()
    ag_ok, ag_msg = blocker.test_adguard(cfg)
    return render_template(
        "sites.html",
        sites=blocker.list_blocked_sites(cfg),
        adguard_ok=ag_ok,
        adguard_msg=ag_msg,
    )


@app.route("/sites/add", methods=["POST"])
@access_required
def sites_add():
    domain = request.form.get("domain", "")
    ok, msg = blocker.add_blocked_site(domain)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("sites"))


@app.route("/sites/remove", methods=["POST"])
@access_required
def sites_remove():
    domain = request.form.get("domain", "")
    ok, msg = blocker.remove_blocked_site(domain)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("sites"))


# --------------------------------------------------------------------------
# Rotte: Gestione dispositivi
# --------------------------------------------------------------------------

@app.route("/devices")
@access_required
def devices():
    cfg = blocker.load_config()
    arp_ok, arp_data = blocker.get_arp_devices()
    ag_ok, ag_msg = blocker.test_adguard(cfg)

    # Dispositivi gestiti (verranno bloccati durante la fascia oraria)
    managed = set(blocker.list_managed_devices(cfg))
    # È in corso il blocco effettivo adesso?
    blocking_now = blocker.is_blocking_active(cfg) and not blocker.is_temporarily_unlocked(cfg)

    device_list = []
    if arp_ok:
        for dev in arp_data:
            dev = dict(dev)
            dev["managed"] = dev["ip"] in managed
            device_list.append(dev)

    # IP gestiti non presenti nella ARP table (li mostriamo comunque)
    arp_ips = {d["ip"] for d in device_list}
    for ip in managed:
        if ip not in arp_ips:
            device_list.append({"name": ip, "ip": ip, "mac": "-", "managed": True})

    return render_template(
        "devices.html",
        devices=device_list,
        arp_ok=arp_ok,
        arp_msg=arp_data if not arp_ok else "",
        adguard_ok=ag_ok,
        adguard_msg=ag_msg if not ag_ok else "",
        blocking_now=blocking_now,
    )


@app.route("/devices/toggle", methods=["POST"])
@access_required
def devices_toggle():
    ip = request.form.get("ip", "").strip()
    # Se è già gestito lo rimuoviamo, altrimenti lo aggiungiamo alla gestione
    currently_managed = request.form.get("managed", "0") == "1"
    if currently_managed:
        ok, msg = blocker.unmanage_device(ip)
    else:
        ok, msg = blocker.manage_device(ip)
    flash(msg, "success" if ok else "danger")
    return redirect(url_for("devices"))


# --------------------------------------------------------------------------
# Rotte: Orari di blocco
# --------------------------------------------------------------------------

@app.route("/schedule")
@access_required
def schedule():
    cfg = blocker.load_config()
    return render_template(
        "schedule.html",
        schedule=cfg.get("schedule", {}),
        quiz_cfg=cfg.get("quiz", {}),
        session_minutes=cfg.get("session_minutes", 30),
        unlock_minutes=cfg.get("unlock_minutes", 30),
        giorni=GIORNI,
    )


@app.route("/schedule/save", methods=["POST"])
@access_required
def schedule_save():
    cfg = blocker.load_config()
    sch = cfg.setdefault("schedule", {})

    sch["enabled"] = request.form.get("enabled") == "on"
    sch["start"] = request.form.get("start", "14:00")
    sch["end"] = request.form.get("end", "18:00")

    # Giorni selezionati (checkbox day0..day6)
    days = []
    for i in range(7):
        if request.form.get(f"day{i}") == "on":
            days.append(i)
    sch["days"] = days

    # Parametri quiz e durate (con validazione minima). Nessun timer: il numero
    # di domande è pensato per coprire 10-20 minuti di risposta effettiva.
    quiz_cfg = cfg.setdefault("quiz", {})
    quiz_cfg["num_questions"] = _to_int(request.form.get("num_questions"), 20, 1, 180)
    quiz_cfg["pass_threshold"] = _to_int(request.form.get("pass_threshold"), 70, 1, 100)
    cfg["session_minutes"] = _to_int(request.form.get("session_minutes"), 30, 1, 1440)
    cfg["unlock_minutes"] = _to_int(request.form.get("unlock_minutes"), 30, 1, 1440)

    blocker.save_config(cfg)

    # Riapplichiamo subito lo stato secondo i nuovi orari
    ok, msg, _ = blocker.apply_blocking_state(cfg)
    if ok:
        flash("Orari e impostazioni salvati.", "success")
    else:
        flash(f"Impostazioni salvate, ma AdGuard non aggiornato: {msg}", "warning")
    return redirect(url_for("schedule"))


def _to_int(value, default, lo, hi):
    """Converte in int con clamp tra lo e hi; default se non valido."""
    try:
        v = int(value)
    except (TypeError, ValueError):
        return default
    return max(lo, min(hi, v))


# --------------------------------------------------------------------------
# Logout
# --------------------------------------------------------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("Sessione terminata.", "info")
    return redirect(url_for("dashboard"))


# --------------------------------------------------------------------------
# Endpoint di stato (utile per debug / health check)
# --------------------------------------------------------------------------

@app.route("/api/status")
def api_status():
    cfg = blocker.load_config()
    ag_ok, ag_msg = blocker.test_adguard(cfg)
    return jsonify({
        "blocking_active": blocker.is_blocking_active(cfg),
        "temporarily_unlocked": blocker.is_temporarily_unlocked(cfg),
        "adguard_ok": ag_ok,
        "adguard_msg": ag_msg,
        "blocked_sites": len(cfg.get("blocked_sites", [])),
    })


# --------------------------------------------------------------------------
# Scheduler in background
# --------------------------------------------------------------------------

def _scheduled_apply():
    """Job periodico: riallinea lo stato di blocco su AdGuard."""
    try:
        blocker.apply_blocking_state()
    except Exception as exc:  # noqa: BLE001 - non vogliamo che il job muoia
        app.logger.warning("apply_blocking_state fallito: %s", exc)


def start_scheduler():
    """Avvia lo scheduler che ogni minuto riapplica lo stato di blocco."""
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(_scheduled_apply, "interval", seconds=60, id="apply_blocking",
                      max_instances=1, coalesce=True)
    scheduler.start()
    # Applichiamo subito lo stato all'avvio
    _scheduled_apply()
    return scheduler


# Avviamo lo scheduler una sola volta (evitiamo il doppio avvio del reloader)
if not app.debug or os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    _scheduler = start_scheduler()


if __name__ == "__main__":
    # Reloader disattivato: lo scheduler deve girare in un solo processo
    app.run(host="0.0.0.0", port=5000, use_reloader=False)

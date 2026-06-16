#!/usr/bin/env bash
#
# install.sh - Installazione completa di FocusBlock
#
# Uso:
#   cd /home/pi/focusblock && chmod +x install.sh && sudo ./install.sh
#
set -euo pipefail

# --------------------------------------------------------------------------
# Variabili e controlli iniziali
# --------------------------------------------------------------------------

# Cartella in cui si trova questo script (deve essere /home/pi/focusblock)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="${SCRIPT_DIR}/config.json"
SERVICE_FILE="${SCRIPT_DIR}/focusblock.service"
SERVICE_DEST="/etc/systemd/system/focusblock.service"

# Utente proprietario (l'utente normale, non root)
TARGET_USER="pi"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()  { echo -e "${GREEN}[*]${NC} $1"; }
warn()  { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[x]${NC} $1" >&2; }

# Deve girare come root (per pip di sistema e systemd)
if [[ "${EUID}" -ne 0 ]]; then
  error "Questo script va eseguito con sudo: sudo ./install.sh"
  exit 1
fi

info "Installazione di FocusBlock in ${SCRIPT_DIR}"

# --------------------------------------------------------------------------
# 1. Installazione dipendenze Python
# --------------------------------------------------------------------------

# Su Raspberry Pi OS / Debian 'pip' può non essere nel PATH: usiamo
# 'python3 -m pip' e, se il modulo pip manca, lo installiamo via apt.
if python3 -m pip --version >/dev/null 2>&1; then
  PIP="python3 -m pip"
elif command -v pip3 >/dev/null 2>&1; then
  PIP="pip3"
else
  warn "pip non trovato: installo python3-pip via apt..."
  apt-get update
  apt-get install -y python3-pip
  PIP="python3 -m pip"
fi

info "Installazione dipendenze Python (flask, apscheduler, requests)..."
${PIP} install --break-system-packages flask apscheduler requests

# --------------------------------------------------------------------------
# 2. Credenziali AdGuard Home + secret key
# --------------------------------------------------------------------------

echo
info "Configurazione AdGuard Home"
read -rp "  URL AdGuard Home [http://192.168.1.200:3000]: " AG_URL
AG_URL="${AG_URL:-http://192.168.1.200:3000}"

read -rp "  Username AdGuard Home: " AG_USER
read -rsp "  Password AdGuard Home: " AG_PASS
echo

# Generazione secret key casuale per le sessioni Flask
SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"

info "Salvataggio configurazione in ${CONFIG_FILE}..."

# Aggiorniamo config.json preservando eventuali valori esistenti (merge in Python)
AG_URL="${AG_URL}" AG_USER="${AG_USER}" AG_PASS="${AG_PASS}" SECRET_KEY="${SECRET_KEY}" \
CONFIG_FILE="${CONFIG_FILE}" python3 <<'PYEOF'
import json, os

config_file = os.environ["CONFIG_FILE"]

# Configurazione di default (coerente con blocker.DEFAULT_CONFIG)
default = {
    "adguard": {"url": "http://192.168.1.200:3000", "username": "", "password": ""},
    "schedule": {"enabled": True, "start": "14:00", "end": "18:00", "days": [0, 1, 2, 3, 4]},
    "session_minutes": 30,
    "unlock_minutes": 30,
    "quiz": {"num_questions": 20, "pass_threshold": 70},
    "blocked_sites": [],
    "blocked_devices": [],
    "unlock_until": 0,
    "secret_key": "",
}

# Carichiamo l'eventuale config esistente per non perdere orari/siti
existing = {}
if os.path.exists(config_file):
    try:
        with open(config_file, encoding="utf-8") as f:
            existing = json.load(f)
    except Exception:
        existing = {}

cfg = default.copy()
cfg.update({k: v for k, v in existing.items() if k in cfg})
# Manteniamo i sottodizionari esistenti dove presenti
for key in ("adguard", "schedule", "quiz"):
    merged = dict(default[key])
    merged.update(existing.get(key, {}))
    cfg[key] = merged

# Applichiamo i valori inseriti dall'utente
cfg["adguard"]["url"] = os.environ["AG_URL"]
cfg["adguard"]["username"] = os.environ["AG_USER"]
cfg["adguard"]["password"] = os.environ["AG_PASS"]
cfg["secret_key"] = os.environ["SECRET_KEY"]

with open(config_file, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)

print("config.json aggiornato.")
PYEOF

# Permessi: il file contiene credenziali, restringiamo l'accesso
chown "${TARGET_USER}:${TARGET_USER}" "${CONFIG_FILE}"
chmod 600 "${CONFIG_FILE}"

# I file del progetto devono appartenere all'utente che esegue il servizio
chown -R "${TARGET_USER}:${TARGET_USER}" "${SCRIPT_DIR}"

# --------------------------------------------------------------------------
# 3. Installazione del servizio systemd
# --------------------------------------------------------------------------

info "Installazione del servizio systemd..."
if [[ ! -f "${SERVICE_FILE}" ]]; then
  error "File ${SERVICE_FILE} non trovato."
  exit 1
fi
cp "${SERVICE_FILE}" "${SERVICE_DEST}"

# --------------------------------------------------------------------------
# 4. Abilitazione e avvio del servizio
# --------------------------------------------------------------------------

info "Abilitazione e avvio del servizio focusblock..."
systemctl daemon-reload
systemctl enable focusblock
systemctl restart focusblock

# Piccola attesa e verifica stato
sleep 2
if systemctl is-active --quiet focusblock; then
  info "Servizio focusblock attivo."
else
  warn "Il servizio non risulta attivo. Controlla con: journalctl -u focusblock -e"
fi

# --------------------------------------------------------------------------
# 5. Messaggio finale
# --------------------------------------------------------------------------

echo
echo -e "${GREEN}=======================================================${NC}"
echo -e "${GREEN} FocusBlock attivo su http://192.168.1.200:5000${NC}"
echo -e "${GREEN}=======================================================${NC}"

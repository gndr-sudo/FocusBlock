# FocusBlock

Sistema per bloccare i siti distraenti negli orari di studio, con sblocco
tramite quiz. Composto da un backend Python (servizio systemd) e una dashboard
web Flask (porta 5000). Il blocco dei domini e dei dispositivi avviene tramite
le API REST di **AdGuard Home**, che funge da DNS server per tutta la LAN.

## Logica di accesso

- **Fuori dalla fascia di blocco** → accesso diretto alla dashboard, nessun quiz.
- **Dentro la fascia di blocco** → per accedere bisogna superare il quiz (≥70%).
  Se superato → accesso dashboard per 30 min + sblocco temporaneo siti per 30 min.
- Il blocco dei siti è attivo **solo** durante la fascia oraria configurata.

## Struttura

```
focusblock/
├── app.py              # Flask app principale + scheduler
├── blocker.py          # logica orari + API AdGuard + ARP
├── questions.py        # domande quiz (placeholder, formato Q/A/W)
├── config.json         # orari, credenziali AdGuard, impostazioni
├── templates/          # UI Bootstrap 5
├── focusblock.service  # unit systemd
└── install.sh          # installazione completa
```

## Installazione (su Raspberry Pi)

```bash
cd /home/pi/focusblock && chmod +x install.sh && sudo ./install.sh
```

Lo script installa le dipendenze pip, chiede le credenziali di AdGuard Home,
genera la secret key di sessione, installa e avvia il servizio systemd.

Al termine: **FocusBlock attivo su http://192.168.1.200:5000**

## Domande del quiz

Le domande vanno inserite in `questions.py`, nella stringa `RAW_QUESTIONS`,
nel formato (blocchi separati da `---`):

```
Q: Testo della domanda?
A: Risposta corretta
W: Risposta errata 1
W: Risposta errata 2
W: Risposta errata 3
---
```

Il parsing è automatico. Finché non ci sono domande, durante la fascia di
blocco la dashboard mostra un avviso e consente l'accesso manuale.

Il quiz **non ha timer** (un countdown sarebbe aggirabile lasciando la pagina
aperta): a ogni accesso vengono estratte casualmente `num_questions` domande
(default **20**, regolabile dalla pagina *Orari*), un numero pensato per
coprire circa **10-20 minuti** di risposta effettiva. Soglia di superamento 70%.

## Meccanismo di blocco

- **Siti**: regole utente AdGuard `||dominio^` aggiunte/rimosse via
  `/control/filtering/set_rules`. Attive solo nella fascia oraria.
- **Dispositivi**: gli IP gestiti vengono aggiunti/rimossi da
  `disallowed_clients` via `/control/access/set` **solo durante la fascia
  oraria** (come i siti); fuori orario e durante lo sblocco temporaneo
  post-quiz vengono sbloccati. Bloccato = il dispositivo non può usare il
  DNS di AdGuard.
- **Discovery dispositivi**: lettura della ARP table (`arp -a`).

## Note

- Gli errori (AdGuard non raggiungibile, ARP vuoto, credenziali errate) sono
  gestiti e mostrati con messaggi chiari nella UI.
- Lo scheduler (APScheduler) riallinea lo stato di blocco su AdGuard ogni minuto.
```

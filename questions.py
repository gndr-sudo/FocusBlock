"""
questions.py
============
Domande del quiz di FocusBlock.

Formato (blocchi separati da '---'):

    Q: Testo della domanda?
    A: Risposta corretta
    W: Risposta errata 1
    W: Risposta errata 2
    W: Risposta errata 3
    ---

Il parsing avviene automaticamente in app.py (funzione parse_questions):
la risposta in 'A:' è quella corretta, le 'W:' sono i distrattori. Le opzioni
vengono mescolate casualmente ad ogni quiz.
"""

RAW_QUESTIONS = """
Q: Cos'è una VPN?
A: Una tecnologia che crea una connessione sicura su una rete pubblica come se i dispositivi fossero sulla stessa LAN
W: Un protocollo di routing che ottimizza i percorsi su Internet
W: Un sistema di autenticazione centralizzato per reti aziendali
W: Un firewall software che filtra il traffico in entrata e uscita
---
Q: Qual è l'obiettivo fondamentale di una VPN?
A: Estendere reti private mediante connessioni remote sicure su infrastrutture pubbliche
W: Aumentare la velocità di connessione riducendo i percorsi di rete
W: Sostituire il firewall perimetrale con un sistema più moderno
W: Fornire indirizzi IP pubblici ai dispositivi della rete interna
---
Q: Cosa si intende per tunneling in una VPN?
A: La creazione di un canale logico sicuro in cui i pacchetti originali vengono incapsulati in nuovi pacchetti IP
W: La compressione dei dati prima della trasmissione su Internet
W: Il reindirizzamento del traffico attraverso server proxy intermedi
W: La segmentazione dei pacchetti in frammenti più piccoli per la trasmissione
---
Q: Quali tre proprietà garantisce il tunneling VPN?
A: Riservatezza, autenticazione e integrità
W: Velocità, disponibilità e scalabilità
W: Compressione, routing e NAT
W: Anonimato, ridondanza e bilanciamento del carico
---
Q: In una VPN Host-to-Net, cosa è necessario sul dispositivo client?
A: Un software client VPN installato sul dispositivo
W: Un indirizzo IP pubblico statico assegnato al client
W: Un server RADIUS locale sulla stessa rete del client
W: Una scheda di rete dedicata esclusivamente alla VPN
---
Q: In una VPN Host-to-Net, cosa si trova dall'altra parte della connessione?
A: Un Network Access Server o VPN Gateway che accetta le connessioni in ingresso
W: Un altro client VPN configurato in modalità server
W: Un server DNS dedicato alla risoluzione dei nomi interni
W: Un proxy HTTP che intermedia il traffico web
---
Q: Qual è la caratteristica principale di una VPN Site-to-Site?
A: È trasparente agli utenti finali — il traffico viene cifrato automaticamente dai gateway senza software sui client
W: Richiede che ogni utente configuri manualmente il client VPN
W: Funziona solo con protocollo IPsec in transport mode
W: Viene stabilita solo su richiesta degli utenti, non è permanente
---
Q: Qual è lo scopo principale di una Personal VPN come NordVPN?
A: Anonimizzare l'IP dell'utente e proteggere il traffico su reti WiFi pubbliche non sicure
W: Collegare due sedi aziendali in modo permanente e sicuro
W: Fornire accesso remoto alle risorse della LAN aziendale
W: Sostituire il firewall perimetrale aziendale
---
Q: Cosa distingue una Secure VPN da una Trusted VPN?
A: La Secure VPN usa crittografia propria indipendente dal provider, la Trusted VPN si affida alla sicurezza del provider
W: La Secure VPN è più lenta perché cifra ogni singolo bit del traffico
W: La Trusted VPN usa sempre IPsec mentre la Secure VPN usa SSL/TLS
W: La Secure VPN richiede hardware dedicato mentre la Trusted VPN è solo software
---
Q: Qual è il punto debole principale di una Trusted VPN?
A: Se il provider viene compromesso il traffico è esposto, perché la sicurezza dipende dalla fiducia nel provider
W: Non supporta la cifratura dei dati rendendo il traffico leggibile
W: È limitata a connessioni di breve durata non adatte per uso aziendale
W: Richiede un numero elevato di certificati digitali difficili da gestire
---
Q: In quale modalità IPsec viene cifrato solo il payload lasciando l'header IP originale intatto?
A: Transport mode
W: Tunnel mode
W: Bridge mode
W: Gateway mode
---
Q: In quale modalità IPsec viene cifrato l'intero pacchetto IP originale incluso l'header?
A: Tunnel mode
W: Transport mode
W: Encapsulation mode
W: Secure mode
---
Q: Quale sotto-protocollo di IPsec fornisce solo autenticazione e integrità senza cifratura?
A: AH (Authentication Header)
W: ESP (Encapsulating Security Payload)
W: IKE (Internet Key Exchange)
W: SA (Security Association)
---
Q: Quale sotto-protocollo di IPsec fornisce cifratura, autenticazione e integrità?
A: ESP (Encapsulating Security Payload)
W: AH (Authentication Header)
W: IKE (Internet Key Exchange)
W: GRE (Generic Routing Encapsulation)
---
Q: Come viene gestito lo scambio di chiavi in IPsec?
A: Tramite IKE (Internet Key Exchange)
W: Tramite AH (Authentication Header)
W: Tramite ESP in modalità key-exchange
W: Tramite un server RADIUS dedicato
---
Q: Perché SSL/TLS è vantaggioso rispetto a IPsec per attraversare firewall e NAT?
A: Usa la porta 443 (HTTPS) che è quasi sempre aperta nei firewall
W: Non richiede handshake iniziale riducendo la latenza
W: Funziona a layer 2 quindi non è influenzato dal NAT
W: Usa porte dinamiche che i firewall non possono bloccare
---
Q: Quale protocollo VPN ha un codice di circa 4000 righe rendendolo più facile da auditare?
A: WireGuard
W: OpenVPN
W: IPsec
W: L2TP/IPsec
---
Q: Perché PPTP è considerato insicuro e non dovrebbe essere usato?
A: Usa cifratura debole con MS-CHAPv2 che ha vulnerabilità note e le chiavi possono essere recuperate
W: Non supporta la cifratura del traffico lasciandolo in chiaro
W: Opera solo su connessioni fisiche non supportando Internet
W: È incompatibile con i sistemi operativi moderni
---
Q: Perché L2TP viene quasi sempre usato insieme a IPsec?
A: Perché L2TP da solo non cifra il traffico, si occupa solo del tunneling
W: Perché L2TP non supporta IPv4 senza l'aiuto di IPsec
W: Perché IPsec fornisce la compressione necessaria per L2TP
W: Perché L2TP opera a layer 3 e ha bisogno di IPsec per layer 2
---
Q: Quali sono le tre caratteristiche fondamentali che deve avere un firewall?
A: Tutto il traffico passa per lui, solo il traffico autorizzato lo attraversa, il firewall stesso è hardened
W: Deve filtrare a layer 7, avere due interfacce di rete, loggare tutto il traffico
W: Deve usare NAT, essere trasparente agli utenti, aggiornarsi automaticamente
W: Deve bloccare solo il traffico in entrata, usare whitelist, avere un IDS integrato
---
Q: Cosa filtra un ingress firewall?
A: Il traffico in entrata nella rete protetta proveniente dall'esterno
W: Il traffico in uscita dalla rete protetta verso l'esterno
W: Solo il traffico proveniente da indirizzi IP nella blacklist
W: Il traffico tra i diversi segmenti della rete interna
---
Q: A cosa serve un egress firewall?
A: Filtra il traffico in uscita impedendo ad esempio che malware comunichi con server esterni
W: Filtra il traffico in entrata proteggendo dai tentativi di intrusione
W: Gestisce l'autenticazione degli utenti che accedono alla rete
W: Bilancia il carico tra più connessioni Internet
---
Q: Cosa analizza un firewall Packet Filtering?
A: Gli header dei pacchetti IP — indirizzi sorgente/destinazione, porte, protocollo
W: Il contenuto completo del payload applicativo
W: Le sessioni TCP e il loro stato corrente
W: I certificati SSL dei server di destinazione
---
Q: Come vengono applicate le regole in una ACL firewall?
A: In sequenza dalla prima all'ultima — appena un pacchetto corrisponde a una regola si applica quell'azione
W: In parallelo su tutti i core del processore del firewall
W: Prima le regole di blocco poi quelle di permesso
W: In ordine inverso dalla più specifica alla più generica
---
Q: Cosa significa OPEN SECURITY POLICY in un firewall?
A: L'ACL contiene una blacklist di divieti e tutto il resto del traffico è permesso per default
W: L'ACL contiene una whitelist di permessi e tutto il resto è bloccato per default
W: Il firewall permette tutto il traffico senza nessuna regola di blocco
W: Le regole vengono applicate solo durante l'orario lavorativo
---
Q: Perché l'ordine delle regole in un'ACL è fondamentale?
A: Perché appena un pacchetto corrisponde a una regola le successive non vengono controllate
W: Perché le regole più in basso hanno priorità maggiore
W: Perché il firewall applica tutte le regole e usa quella più restrittiva
W: Perché le regole vengono rivalutate ogni volta che cambia lo stato della rete
---
Q: Cosa fa l'azione REJECT a differenza di DROP?
A: REJECT blocca il pacchetto E notifica il mittente con un messaggio ICMP, DROP lo scarta silenziosamente
W: REJECT è più veloce perché non genera log, DROP genera un log per ogni pacchetto
W: REJECT permette al mittente di ritentare, DROP chiude definitivamente la connessione
W: Non c'è differenza pratica tra REJECT e DROP
---
Q: Perché DROP è preferito a REJECT in contesti di sicurezza?
A: Perché non rivela all'attaccante informazioni sull'esistenza del firewall o dei servizi protetti
W: Perché è più veloce da processare riducendo il carico sul firewall
W: Perché genera meno traffico di rete non inviando notifiche ICMP
W: Perché è l'unica azione supportata da tutti i tipi di firewall
---
Q: Cosa fa un Application Proxy a differenza di un Packet Filter?
A: Crea due connessioni separate e opera a layer 7 comprendendo i protocolli applicativi
W: Filtra solo gli header IP senza mai guardare il contenuto applicativo
W: Tiene traccia dello stato delle connessioni TCP nella state table
W: Blocca il traffico basandosi solo sugli indirizzi IP sorgente
---
Q: Qual è lo svantaggio principale di un Application Proxy?
A: È più lento del Packet Filtering e richiede un proxy dedicato per ogni protocollo supportato
W: Non può filtrare il traffico in base al contenuto applicativo
W: Non supporta connessioni HTTPS cifrate
W: Non può essere usato in combinazione con un firewall stateful
---
Q: Cos'è un Circuit Level Proxy?
A: Un proxy che verifica solo le informazioni di livello sessione (handshake TCP) senza controllo applicativo
W: Un proxy che analizza il contenuto di ogni protocollo applicativo
W: Un firewall che opera esclusivamente a layer 3 del modello OSI
W: Un sistema IDS integrato nel firewall perimetrale
---
Q: Qual è l'esempio più noto di Circuit Level Proxy?
A: SOCKS proxy
W: Squid proxy
W: Apache reverse proxy
W: Nginx forward proxy
---
Q: Qual è la funzione di caching in un Forward Proxy?
A: Memorizza le pagine web più richieste e le restituisce dalla cache locale risparmiando banda
W: Distribuisce le richieste in ingresso su più server backend
W: Termina le connessioni SSL al posto dei server interni
W: Assegna indirizzi IP dinamici ai client della rete interna
---
Q: Qual è la funzione di load balancing in un Reverse Proxy?
A: Distribuisce le richieste in ingresso su più server backend bilanciando il carico
W: Memorizza le pagine web più richieste riducendo il traffico verso Internet
W: Nasconde l'identità dei client interni ai server esterni
W: Filtra il traffico in uscita impedendo l'esfiltrazione di dati
---
Q: Cosa fa la terminazione SSL in un Reverse Proxy?
A: Il proxy gestisce la cifratura HTTPS e i server interni comunicano in HTTP non cifrato
W: Il proxy blocca tutte le connessioni SSL non autorizzate
W: I server interni gestiscono la cifratura e il proxy la decifratura
W: Il proxy rifiuta le connessioni con certificati SSL scaduti
---
Q: Quanti firewall sono necessari per creare una DMZ?
A: Due firewall (o un singolo firewall con tre interfacce di rete)
W: Un solo firewall con regole ACL avanzate
W: Tre firewall — uno per Internet, uno per la DMZ, uno per la LAN
W: Il numero dipende dal numero di server pubblici da proteggere
---
Q: Quali server si trovano tipicamente nella DMZ?
A: Web server, mail server SMTP, DNS server — tutti i server che offrono servizi all'esterno
W: Database server, application server, server di backup
W: Server RADIUS, server LDAP, server di autenticazione
W: Workstation degli utenti, stampanti di rete, server file interni
---
Q: Cos'è un Bastion Host?
A: Un sistema hardened che esegue il minimo indispensabile di servizi per ridurre la superficie di attacco
W: Un server dedicato esclusivamente all'autenticazione degli utenti remoti
W: Un firewall hardware posizionato tra Internet e la DMZ
W: Un sistema di backup ridondante per il firewall principale
---
Q: Cosa NON può fare un firewall?
A: Proteggere da minacce interne o da dispositivi infetti portati dall'esterno nella rete
W: Filtrare il traffico in base agli indirizzi IP sorgente e destinazione
W: Bloccare connessioni verso porte specifiche
W: Registrare nei log il traffico bloccato
---
Q: Cos'è un IDS?
A: Un sistema hardware e/o software che identifica e notifica accessi non autorizzati a computer o reti
W: Un firewall di nuova generazione con ispezione deep packet integrata
W: Un sistema di autenticazione centralizzato per l'accesso alla rete
W: Un proxy che intermedia tutte le connessioni verso Internet
---
Q: Qual è l'analogia classica per spiegare la differenza tra firewall e IDS?
A: Il firewall è la porta blindata, l'IDS è il sistema d'allarme che scatta se qualcuno la supera
W: Il firewall è il poliziotto, l'IDS è il giudice che decide la pena
W: Il firewall è l'antivirus, l'IDS è il backup dei dati
W: Il firewall è il lucchetto, l'IDS è la chiave
---
Q: Quali sono i quattro componenti principali di un IDS?
A: Sensori, console, motore (engine) e database delle regole
W: Firewall, proxy, scanner e logger
W: Client, server, database e interfaccia web
W: Sonde, analizzatore, reporter e blocklist
---
Q: Cosa fanno i sensori in un sistema IDS?
A: Raccolgono informazioni dalla rete o dai computer posizionandosi in punti strategici
W: Analizzano i dati raccolti e identificano le violazioni
W: Mostrano all'operatore lo stato della rete e gli alert
W: Memorizzano le regole e i pattern di attacco
---
Q: Cosa analizza un NIDS?
A: Il traffico di uno o più segmenti di LAN per individuare anomalie o probabili intrusioni
W: I log e le attività degli host critici della rete
W: Il traffico cifrato HTTPS decifrando i pacchetti
W: Solo il traffico in ingresso dall'esterno ignorando quello interno
---
Q: Perché un NIDS è utile anche se esiste già un firewall?
A: Analizza il traffico che il firewall non blocca e monitora il traffico interno alla rete
W: Perché i firewall moderni non supportano il filtraggio a layer 7
W: Perché il NIDS è più veloce del firewall nel bloccare gli attacchi
W: Perché il firewall non può loggare il traffico mentre il NIDS sì
---
Q: Perché i sensori NIDS devono essere trasparenti nella rete?
A: Per non essere individuati dagli attaccanti e per non creare colli di bottiglia nelle prestazioni
W: Perché la legge impone che i sistemi di monitoraggio non siano visibili
W: Per poter intercettare anche il traffico cifrato senza modificarlo
W: Per risparmiare indirizzi IP nella rete
---
Q: Dove vengono tipicamente posizionati i sensori NIDS?
A: Nei punti di passaggio (router, gateway), punti vulnerabili (web server) e punti sensibili (database)
W: Solo all'esterno del firewall perimetrale
W: Esclusivamente sui server della DMZ
W: In modo casuale per coprire tutta la rete uniformemente
---
Q: Cosa analizza un HIDS?
A: Log di sistema, attività degli utenti, attività delle applicazioni e modifiche a file sull'host
W: Il traffico di rete tra i vari segmenti della LAN
W: Le connessioni in ingresso dall'esterno verso i server pubblici
W: Il traffico DNS per rilevare attacchi di tipo DNS poisoning
---
Q: Cos'è un DIDS?
A: Un sistema ibrido che combina NIDS e HIDS aggregando dati da sensori di rete e host
W: Un IDS distribuito su più sedi geografiche collegate via VPN
W: Un IDS dedicato esclusivamente alla rilevazione di attacchi DoS
W: Un database centralizzato di signature per sistemi IDS multipli
---
Q: Qual è il vantaggio della Misuse Detection?
A: Genera un numero relativamente basso di falsi positivi ed è affidabile per attacchi noti
W: Rileva attacchi sconosciuti analizzando il comportamento anomalo
W: Non richiede aggiornamenti periodici del database delle signature
W: Funziona anche su traffico cifrato senza decifrarlo
---
Q: Qual è il principale svantaggio della Anomaly Detection?
A: Genera più falsi positivi perché attività legittime ma insolite possono essere scambiate per attacchi
W: Non rileva mai attacchi sconosciuti limitandosi ai pattern nel database
W: Richiede una connessione Internet costante per aggiornarsi
W: Non può essere usata insieme alla Misuse Detection
---
Q: Cosa fa un IDS passivo?
A: Rileva una violazione e si limita a notificarla all'operatore senza interventi automatici
W: Rileva una violazione e prende contromisure automatiche per eliminarla
W: Monitora il traffico senza mai generare alert per non disturbare gli utenti
W: Blocca automaticamente gli IP attaccanti modificando le regole del firewall
---
Q: Cosa fa un IDS attivo?
A: Rileva una violazione e prende contromisure automatiche come bloccare un IP o modificare le regole del firewall
W: Rileva una violazione e notifica solo l'operatore senza agire autonomamente
W: Monitora solo il traffico in entrata ignorando quello interno
W: Genera report periodici senza monitoraggio in tempo reale
---
Q: Cosa distingue un IPS da un IDS?
A: L'IPS integra funzionalità di firewall e NIDS potendo bloccare attacchi a layer 4 e layer 7
W: L'IPS analizza solo il traffico interno mentre l'IDS solo quello esterno
W: L'IPS usa solo signature-based detection mentre l'IDS usa anomaly detection
W: L'IPS è sempre hardware mentre l'IDS è sempre software
---
Q: Cos'è un honeypot?
A: Un sistema esca che sembra contenere informazioni preziose ma è isolato e usato per studiare gli attaccanti
W: Un sistema di backup che mantiene copie cifrate dei dati sensibili
W: Un firewall specializzato nel rilevare attacchi di tipo phishing
W: Un server proxy che anonimizza il traffico degli utenti interni
---
Q: Qual è il vantaggio principale di un honeypot low-interaction?
A: Facile da gestire, basso rischio, ottimo per bloccare attacchi da tool automatici
W: Permette di osservare in dettaglio il comportamento di attaccanti esperti
W: Fornisce informazioni su nuovi tipi di attacco mai visti prima
W: Può ingannare anche gli attaccanti più esperti a lungo termine
---
Q: Qual è il rischio principale di un honeypot high-interaction?
A: Se mal protetto l'attaccante potrebbe usarlo come trampolino per attaccare altre reti
W: È troppo facile da riconoscere per gli attaccanti esperti
W: Non fornisce informazioni utili perché l'attaccante sa di essere monitorato
W: Richiede una connessione Internet dedicata ad alta banda
---
Q: Quali tre cose garantisce SSL/TLS?
A: Autenticazione, riservatezza e integrità
W: Cifratura, compressione e non ripudio
W: Autenticazione, disponibilità e compressione
W: Riservatezza, anonimato e integrità
---
Q: Chi sviluppò originariamente SSL?
A: Netscape, a metà degli anni '90
W: Microsoft, come componente di Internet Explorer
W: IBM, come estensione del protocollo SNA
W: IETF, come successore di TLS
---
Q: Quali versioni di TLS sono considerate deprecate e insicure?
A: Tutte le versioni fino a TLS 1.1 inclusa
W: Solo SSL 2.0 e SSL 3.0
W: TLS 1.0 e TLS 1.1 ma non SSL 3.0 che è ancora sicuro
W: Solo TLS 1.3 perché troppo recente per essere testata
---
Q: Cosa viene negoziato durante la fase di handshake TLS?
A: I parametri della sessione sicura inclusi cipher suite, certificato del server e chiave di sessione
W: Solo gli indirizzi IP sorgente e destinazione della connessione
W: Il tipo di compressione da usare per i dati trasmessi
W: La versione del protocollo HTTP da usare sopra TLS
---
Q: Cosa contiene il certificato digitale inviato dal server durante l'handshake TLS?
A: La chiave pubblica del server firmata da una CA
W: La chiave privata del server cifrata con la chiave del client
W: La chiave di sessione simmetrica già pronta all'uso
W: Le regole di accesso al server per il client connesso
---
Q: Come viene trasmessa la premaster key al server durante l'handshake TLS?
A: Il client la cifra con la chiave pubblica del server estratta dal certificato
W: Il server la genera e la invia al client cifrata con la chiave privata
W: Viene derivata da entrambi senza mai trasmetterla usando Diffie-Hellman
W: Viene inviata in chiaro perché sarà cifrata successivamente
---
Q: Perché dopo l'handshake TLS si usa la crittografia simmetrica invece di quella asimmetrica?
A: Perché la crittografia simmetrica è molto più veloce per cifrare grandi quantità di dati
W: Perché la crittografia asimmetrica non supporta lo streaming di dati
W: Perché i certificati digitali sono validi solo per l'handshake iniziale
W: Perché la crittografia simmetrica è più sicura per i dati applicativi
---
Q: Cosa aggiunge il TLS Record Protocol ai dati prima di cifrarli?
A: Un MAC (Message Authentication Code) per garantire l'integrità
W: Un certificato digitale per autenticare ogni frammento di dati
W: Una firma RSA del mittente per garantire il non ripudio
W: Un numero di sequenza per riordinare i frammenti in caso di perdita
---
Q: Qual è la differenza fondamentale tra SSL/TLS e PGP/S/MIME?
A: SSL/TLS protegge il canale, PGP/S/MIME proteggono il messaggio stesso end-to-end
W: SSL/TLS è più sicuro perché usa cifratura asimmetrica per tutti i dati
W: PGP/S/MIME proteggono solo i metadati mentre SSL/TLS protegge il contenuto
W: Non c'è differenza sostanziale — entrambi proteggono il messaggio end-to-end
---
Q: In PGP come viene cifrato il messaggio?
A: Il mittente genera una chiave di sessione simmetrica, cifra il messaggio con essa e cifra la chiave con la chiave pubblica del destinatario
W: Il mittente cifra il messaggio direttamente con la chiave pubblica del destinatario
W: Il messaggio viene cifrato con la chiave privata del mittente per garantire l'autenticità
W: Si usa solo crittografia simmetrica con una chiave pre-condivisa
---
Q: Come funziona la firma digitale in PGP?
A: Il mittente calcola l'hash del messaggio e lo cifra con la propria chiave privata
W: Il mittente cifra l'intero messaggio con la chiave pubblica del destinatario
W: Il mittente invia il messaggio in chiaro con allegata la propria chiave pubblica
W: La firma viene generata dal server di posta e non dal mittente
---
Q: Cos'è il Web of Trust di PGP?
A: Un sistema decentralizzato in cui gli utenti firmano le chiavi pubbliche degli altri garantendo per la loro identità
W: Un server centralizzato gestito da MIT dove sono depositate tutte le chiavi PGP
W: Una CA gerarchica gestita dalla comunità open source
W: Un protocollo per verificare automaticamente l'identità del mittente
---
Q: Su quale standard di certificati si basa S/MIME?
A: X.509v3 per i certificati e PKCS#7 per il formato dei dati
W: OpenPGP (RFC 4880) per entrambi certificati e dati
W: X.509v1 per i certificati e PKCS#12 per i dati
W: PEM per i certificati e DER per i dati
---
Q: In quale contesto è preferibile PGP rispetto a S/MIME?
A: Tra individui, attivisti e comunità open source che non vogliono affidarsi a CA centralizzate
W: In aziende con infrastruttura PKI esistente e Outlook come client di posta
W: Quando si ha bisogno di integrazione trasparente con client di posta aziendali
W: Quando il certificato emesso da CA ha un costo troppo elevato
---
Q: Perché WEP è considerato insicuro?
A: Il vettore di inizializzazione (IV) di soli 24 bit veniva riutilizzato permettendo il recupero della chiave
W: Usava AES con chiavi troppo corte non sufficienti per la sicurezza moderna
W: Non supportava l'autenticazione degli utenti lasciando la rete aperta
W: La chiave veniva trasmessa in chiaro durante la fase di associazione
---
Q: Cosa migliorava WPA rispetto a WEP?
A: Introduceva TKIP con gestione dinamica delle chiavi — la chiave cambia per ogni pacchetto
W: Sostituiva RC4 con AES rendendolo molto più sicuro
W: Aggiungeva l'autenticazione tramite server RADIUS obbligatorio
W: Aumentava la lunghezza del vettore di inizializzazione da 24 a 128 bit
---
Q: Su cosa si basa la cifratura in WPA2?
A: AES-CCMP (Counter Mode with CBC-MAC Protocol)
W: TKIP con RC4 e chiavi dinamiche
W: AES in modalità ECB con chiavi a 256 bit
W: RC4 con vettori di inizializzazione a 48 bit
---
Q: Cosa introduce WPA3 per proteggere contro attacchi dictionary offline?
A: SAE (Simultaneous Authentication of Equals) che sostituisce il 4-way handshake di WPA2
W: TKIP con rotazione delle chiavi ogni 10 secondi
W: Un server RADIUS obbligatorio anche in modalità Personal
W: Cifratura AES-256 obbligatoria per tutte le connessioni
---
Q: Cosa garantisce il forward secrecy introdotto da WPA3?
A: Se una chiave di sessione viene compromessa le sessioni precedenti restano protette perché ogni sessione usa chiavi diverse
W: Le chiavi di cifratura vengono cambiate ogni 60 secondi automaticamente
W: Il traffico passato non può essere decifrato anche se si conosce la password della rete
W: La stessa chiave non viene mai usata due volte nello stesso giorno
---
Q: Cosa identifica il SSID in una rete WiFi?
A: Il nome della rete WiFi visibile agli utenti (es. "CasaMia")
W: Il MAC address dell'Access Point che identifica univocamente ogni AP
W: Il canale radio su cui trasmette l'Access Point
W: L'indirizzo IP assegnato all'Access Point dal DHCP
---
Q: Cosa identifica il BSSID in una rete WiFi?
A: Il MAC address dell'interfaccia wireless dell'Access Point
W: Il nome della rete WiFi visibile agli utenti
W: L'indirizzo IP dell'Access Point nella rete locale
W: Il canale radio e la frequenza usata dall'Access Point
---
Q: Cos'è un ESS (Extended Service Set)?
A: L'insieme di più BSS connessi tramite Distribution System che condividono lo stesso SSID
W: Un singolo Access Point con il suo insieme di client connessi
W: Una rete WiFi ad-hoc senza Access Point
W: Un gruppo di reti WiFi con SSID diversi gestiti centralmente
---
Q: Cosa permette l'ESS che un singolo BSS non può offrire?
A: Il roaming — un client può spostarsi tra celle diverse restando connesso alla stessa rete logica
W: La connessione contemporanea su più bande di frequenza
W: L'autenticazione centralizzata tramite server RADIUS
W: La cifratura WPA3 che richiede più Access Point
---
Q: Cos'è la modalità Ad-Hoc (IBSS) in WiFi?
A: Una rete peer-to-peer senza Access Point dove le stazioni comunicano direttamente tra loro
W: Una modalità in cui l'AP si connette via wireless a un altro AP senza cavo
W: Una rete temporanea gestita da un AP mobile
W: Una modalità di backup quando l'AP principale è offline
---
Q: Qual è lo svantaggio della modalità Repeater per un Access Point?
A: La banda si dimezza ad ogni hop perché lo stesso canale serve sia per ricevere che ritrasmettere
W: Non supporta client con WPA2 — solo WEP è compatibile
W: Richiede sempre un cavo Ethernet di backup per funzionare
W: Può coprire al massimo 50 metri di distanza dall'AP principale
---
Q: In quale modalità un AP collega due reti cablate separate tramite un link wireless punto-punto?
A: Bridge mode
W: Repeater mode
W: Root mode
W: Mesh mode
---
Q: Cos'è un WPAN e quale tecnologia ne è un esempio?
A: Wireless Personal Area Network con raggio corto — Bluetooth (802.15), ZigBee, NFC
W: Wireless Wide Area Network che copre intere nazioni — tecnologie 4G/5G
W: Wireless Metropolitan Area Network che copre aree urbane — WiMAX (802.16)
W: Wireless Local Area Network per uffici e case — WiFi (802.11)
---
Q: Qual è la differenza tra WPA-Personal e WPA-Enterprise?
A: Personal usa una Pre-Shared Key condivisa da tutti, Enterprise usa credenziali individuali con server RADIUS
W: Personal supporta solo WPA2, Enterprise supporta WPA2 e WPA3
W: Personal è più sicuro perché usa chiavi più lunghe
W: Enterprise usa la stessa password per tutti ma la cambia ogni ora
---
Q: Perché WPA-Personal è inadeguato per grandi organizzazioni?
A: Non si può revocare l'accesso a un singolo utente senza cambiare la password per tutti
W: Supporta un numero massimo di 50 dispositivi connessi contemporaneamente
W: Non supporta la cifratura AES richiedendo il meno sicuro TKIP
W: Richiede che ogni utente abbia un certificato digitale
---
Q: Cosa significa Authentication nel sistema AAA?
A: Verifica dell'identità — chi sei? L'utente presenta credenziali che il sistema verifica
W: Verifica dei permessi — cosa puoi fare sulla rete?
W: Registrazione delle attività — cosa hai fatto durante la sessione?
W: Assegnazione delle risorse — quanta banda puoi usare?
---
Q: Cosa significa Authorization nel sistema AAA?
A: Verifica dei permessi — cosa puoi fare? Determina a quali risorse l'utente può accedere
W: Verifica dell'identità tramite username e password
W: Registrazione delle attività per audit di sicurezza
W: Generazione delle chiavi di cifratura per la sessione
---
Q: Cosa significa Accounting nel sistema AAA?
A: Registrazione delle attività dell'utente — quando si è connesso, cosa ha fatto, quando si è disconnesso
W: Verifica dell'identità tramite credenziali
W: Determinazione dei permessi di accesso alle risorse
W: Fatturazione dei servizi utilizzati dall'utente
---
Q: In RADIUS, quale dispositivo funge da client RADIUS?
A: Il NAS o l'Access Point che riceve la richiesta di accesso dall'utente e la inoltra al server RADIUS
W: Il dispositivo dell'utente che vuole accedere alla rete
W: Il server che verifica le credenziali e decide se concedere l'accesso
W: Il firewall che filtra il traffico RADIUS sulla rete
---
Q: Quali sono i tre possibili messaggi di risposta del server RADIUS?
A: Access-Accept, Access-Reject, Access-Challenge
W: Access-Grant, Access-Deny, Access-Pending
W: Access-OK, Access-Error, Access-Retry
W: Access-Allow, Access-Block, Access-Verify
---
Q: Come è protetto il traffico tra Access Point e server RADIUS?
A: Da un shared secret — una password condivisa configurata su entrambi i dispositivi
W: Da un tunnel VPN dedicato tra AP e server RADIUS
W: Dal certificato digitale dell'Access Point verificato dalla CA
W: Dalle chiavi WPA2 usate anche per cifrare il traffico di autenticazione
---
Q: Cos'è 802.1X?
A: Uno standard IEEE per il controllo dell'accesso alla rete basato su porta — la porta resta bloccata finché l'utente non si autentica
W: Un protocollo di cifratura per reti wireless che sostituisce WEP
W: Un sistema di autenticazione centralizzato equivalente a RADIUS
W: Uno standard per il roaming tra Access Point di produttori diversi
---
Q: Chi è il Supplicant in 802.1X?
A: Il dispositivo dell'utente che vuole accedere alla rete e gestisce l'autenticazione EAP
W: Il server RADIUS che verifica le credenziali e decide l'accesso
W: L'Access Point o switch che controlla l'accesso alla porta
W: Il certificato digitale presentato durante l'autenticazione
---
Q: Chi è l'Authenticator in 802.1X?
A: Il dispositivo di rete (AP o switch) che controlla l'accesso e inoltra le richieste al server
W: Il dispositivo dell'utente che presenta le credenziali
W: Il server RADIUS che verifica le credenziali
W: L'amministratore di rete che configura le policy di accesso
---
Q: Quale protocollo usa la comunicazione tra Supplicant e Authenticator in 802.1X?
A: EAPOL (EAP Over LAN) — frame Ethernet speciali
W: RADIUS con EAP incapsulato
W: TLS direttamente su Ethernet
W: UDP con pacchetti EAP standard
---
Q: Qual è il vantaggio di EAP-PEAP rispetto a EAP-TLS in termini di deployment?
A: Non richiede certificato lato client — solo il server si autentica con certificato semplificando il deployment
W: È più sicuro perché usa certificati sia lato client che lato server
W: Non richiede nemmeno il certificato lato server riducendo i costi
W: Supporta solo smartcard eliminando il rischio di furto password
---
Q: In EAP-PEAP come si autentica il client una volta stabilito il tunnel TLS?
A: Con username e password tipicamente usando MSCHAPv2 come metodo interno
W: Con un certificato digitale X.509 presentato dentro il tunnel
W: Con un token OTP hardware sincronizzato con il server
W: Con la chiave pre-condivisa WPA configurata sull'AP
---
Q: Qual è il problema principale di HTTP/1.0?
A: Ogni risorsa richiedeva una nuova connessione TCP separata con overhead di handshake
W: Non supportava i metodi POST e PUT per l'invio di dati
W: Non supportava la cifratura HTTPS delle connessioni
W: Limitava la dimensione degli header HTTP a 256 byte
---
Q: Cosa introduceva HTTP/1.1 come comportamento predefinito?
A: Connessioni persistenti (Keep-Alive) — la connessione TCP resta aperta per più richieste
W: La cifratura TLS obbligatoria per tutte le connessioni
W: Il multiplexing di più richieste sulla stessa connessione in parallelo
W: La compressione automatica degli header per ridurre la banda
---
Q: Cos'è il problema Head-of-Line Blocking in HTTP/1.1?
A: Se una richiesta si blocca tutte le successive devono aspettare perché le risposte devono essere ordinate
W: Se l'header di una richiesta supera 1KB la connessione viene chiusa
W: Il server non può inviare risposte mentre elabora la richiesta precedente
W: Il client non può inviare più di una richiesta simultaneamente
---
Q: Come risolve HTTP/2 il problema del Head-of-Line Blocking?
A: Con il multiplexing — i frame binari di più risposte si intrecciano sulla stessa connessione in modo asincrono
W: Aprendo connessioni TCP multiple in parallelo per ogni richiesta
W: Usando UDP invece di TCP per eliminare il controllo di flusso
W: Comprimendo le richieste in modo che si completino più velocemente
---
Q: Qual è la novità principale di HTTP/3 rispetto a HTTP/2?
A: Usa QUIC su UDP invece di TCP eliminando il TCP Head-of-Line Blocking a livello di trasporto
W: Introduce la cifratura TLS obbligatoria che HTTP/2 non aveva
W: Elimina completamente gli header HTTP riducendo l'overhead
W: Usa connessioni multiple TCP in parallelo per ogni risorsa
---
Q: Cosa indica il codice di stato HTTP 200?
A: OK — la richiesta ha avuto successo
W: Created — una nuova risorsa è stata creata
W: No Content — successo ma nessun corpo nella risposta
W: Accepted — la richiesta è stata accettata ma non ancora elaborata
---
Q: Cosa indica il codice di stato HTTP 404?
A: Not Found — la risorsa richiesta non esiste sul server
W: Forbidden — l'utente è autenticato ma non ha i permessi
W: Unauthorized — manca l'autenticazione
W: Gone — la risorsa esisteva ma è stata rimossa definitivamente
---
Q: Cosa indica il codice di stato HTTP 500?
A: Internal Server Error — errore generico lato server
W: Bad Gateway — il server ha ricevuto una risposta invalida dal server a monte
W: Service Unavailable — il server è sovraccarico o in manutenzione
W: Gateway Timeout — il server a monte non ha risposto in tempo
---
Q: Cosa indica il codice di stato HTTP 401?
A: Unauthorized — manca l'autenticazione, il client deve autenticarsi
W: Forbidden — il client è autenticato ma non ha i permessi
W: Not Found — la risorsa non esiste
W: Bad Request — la sintassi della richiesta è errata
---
Q: Cosa indica il codice di stato HTTP 301?
A: Moved Permanently — la risorsa ha un nuovo URI definitivo
W: Moved Temporarily — la risorsa è temporaneamente su un altro URI
W: Not Modified — la risorsa non è cambiata dalla versione in cache
W: Multiple Choices — ci sono più versioni della risorsa disponibili
---
Q: Cosa fa il metodo HTTP GET?
A: Richiede una rappresentazione della risorsa specificata — è idempotente e non modifica dati
W: Invia dati al server per l'elaborazione come la sottomissione di un form
W: Sostituisce completamente la risorsa specificata con nuovi dati
W: Cancella la risorsa specificata dall'URI
---
Q: Cosa fa il metodo HTTP POST?
A: Invia dati al server per l'elaborazione — non è idempotente, inviarlo due volte può creare duplicati
W: Richiede una risorsa senza modificare lo stato del server
W: Aggiorna parzialmente la risorsa specificata
W: Verifica l'esistenza di una risorsa senza scaricarne il contenuto
---
Q: Cosa fa il metodo HTTP HEAD?
A: Restituisce solo gli header senza il body — utile per verificare esistenza e dimensione di una risorsa
W: Invia i soli header della richiesta per testare il server
W: Cancella gli header di cache della risorsa specificata
W: Inizializza una sessione prima di inviare la richiesta principale
---
Q: A cosa serve l'header HTTP Host?
A: Permette il Virtual Hosting — un server fisico con un IP ospita più domini diversi
W: Indica il tipo di contenuto inviato nel body della richiesta
W: Specifica il browser e il sistema operativo del client
W: Autentica il client presso il server senza password
---
Q: Come funziona il meccanismo dei cookie in HTTP?
A: Il server invia un cookie con Set-Cookie, il browser lo memorizza e lo rispedisce in ogni richiesta successiva
W: Il client genera il cookie e lo invia al server per identificarsi
W: I cookie vengono generati dal router e assegnati automaticamente ai client
W: I cookie sono memorizzati solo sul server e mai trasmessi al client
---
Q: Qual è il vantaggio delle sessioni rispetto ai cookie per dati sensibili?
A: I dati restano sul server — il client riceve solo un Session ID opaco senza dati sensibili
W: Le sessioni sono più veloci perché non richiedono trasmissione di dati
W: Le sessioni sono cifrate automaticamente mentre i cookie no
W: Le sessioni non scadono mai mentre i cookie hanno una durata limitata
---
Q: In FTP, quante connessioni TCP vengono usate per una sessione?
A: Due — una per i comandi (controllo) e una per i dati
W: Una sola connessione che gestisce sia comandi che dati
W: Tre — una per i comandi, una per i dati in upload, una per i dati in download
W: Il numero dipende dal numero di file da trasferire
---
Q: In FTP Active mode, chi avvia la connessione dati?
A: Il server si connette attivamente alla porta comunicata dal client con il comando PORT
W: Il client si connette alla porta 21 del server per i dati
W: Il client si connette alla porta casuale comunicata dal server
W: La connessione dati viene stabilita contemporaneamente a quella di controllo
---
Q: Perché FTP Active mode è problematica con i firewall?
A: Il firewall lato client vede arrivare una connessione in ingresso non sollecitata dal client a livello TCP
W: Perché usa porte privilegiate sotto la 1024 bloccate dai firewall
W: Perché cifra il traffico con un algoritmo non supportato dai firewall moderni
W: Perché richiede l'apertura di tutte le porte sul server FTP
---
Q: In FTP Passive mode, chi avvia la connessione dati?
A: Il client si connette alla porta casuale comunicata dal server con il comando PASV
W: Il server si connette attivamente al client sulla porta specificata con PORT
W: La connessione dati viene stabilita automaticamente senza comandi espliciti
W: Entrambi stabiliscono una connessione e usano quella che si connette prima
---
Q: Cosa fa il comando FTP RETR?
A: Scarica un file dal server al client
W: Carica un file dal client al server sovrascrivendo l'esistente
W: Elenca i file nella directory corrente
W: Rinomina un file sul server
---
Q: Cosa fa il comando FTP TYPE I?
A: Imposta la modalità di trasferimento binaria necessaria per immagini, archivi ed eseguibili
W: Imposta la modalità ASCII per i file di testo
W: Inizia il trasferimento di un file in modalità incrementale
W: Verifica l'integrità del file dopo il trasferimento
---
Q: Quali sono i quattro agenti del sistema email?
A: MUA (client utente), MSA (submission), MTA (transfer), MDA (delivery)
W: Client, Server, Relay, Archive
W: Sender, Router, Receiver, Storage
W: Composer, Dispatcher, Carrier, Inbox
---
Q: Cosa fa il comando SMTP MAIL FROM?
A: Specifica il mittente della busta — l'indirizzo a cui arrivano i bounce se la mail non viene consegnata
W: Specifica il mittente visibile nel client di posta del destinatario
W: Inizia la trasmissione del corpo del messaggio
W: Autentica il mittente presso il server SMTP
---
Q: Cosa fa il comando SMTP DATA?
A: Segnala la fine dei comandi di busta e inizia la trasmissione del contenuto del messaggio
W: Specifica i dati di autenticazione del mittente
W: Indica la dimensione del messaggio che sarà inviato
W: Richiede al server di confermare la ricezione dei dati
---
Q: Perché MIME è stato introdotto per le email?
A: SMTP originale supportava solo testo ASCII a 7 bit — MIME permette allegati binari e caratteri non ASCII
W: Per aggiungere la cifratura end-to-end alle email
W: Per ridurre la dimensione dei messaggi con compressione automatica
W: Per permettere l'invio di email a destinatari multipli
---
Q: Cosa fa la codifica Base64 in MIME?
A: Converte dati binari in caratteri ASCII — ogni 3 byte diventano 4 caratteri con aumento dimensione del 33%
W: Comprime i dati binari riducendo la dimensione del file allegato
W: Cifra i dati binari per proteggerli durante il transito
W: Converte i caratteri non ASCII in sequenze di caratteri ASCII sicuri
---
Q: Quando è preferibile usare POP3 rispetto a IMAP?
A: Quando si usa un solo dispositivo e si vuole archiviare le email localmente
W: Quando si accede alla posta da più dispositivi diversi
W: Quando si vogliono gestire cartelle lato server
W: Quando si ha bisogno di sincronizzazione in tempo reale
---
Q: Qual è la struttura gerarchica del DNS dall'alto verso il basso?
A: Root (.) → TLD (.com, .it) → Authoritative Nameserver del dominio specifico
W: Authoritative Nameserver → TLD → Root → Client
W: ISP DNS → Root → TLD → Authoritative Nameserver
W: Client → Local DNS → TLD → Root → Authoritative Nameserver
---
Q: Cosa fa il Recursive Resolver durante una query DNS?
A: Interroga iterativamente Root, TLD e Authoritative Nameserver per trovare la risposta e la restituisce al client
W: Risponde solo alle query provenienti dalla stessa subnet
W: Detiene le informazioni definitive per i domini di cui è autoritativo
W: Gestisce solo i domini di primo livello come .com e .it
---
Q: Cosa è il TTL in una risposta DNS?
A: Il tempo per cui la risposta può essere mantenuta in cache prima di doverla richiedere di nuovo
W: Il numero massimo di hop che una query può fare nella gerarchia DNS
W: Il tempo di timeout dopo cui una query DNS viene considerata fallita
W: La priorità della risposta rispetto ad altre risposte per lo stesso dominio
---
Q: Cos'è la tecnologia Anycast usata per i Root Server DNS?
A: Lo stesso indirizzo IP è annunciato da migliaia di server fisici nel mondo — il traffico va al più vicino
W: I 13 Root Server si replicano automaticamente in tempo reale su ogni continente
W: I Root Server usano connessioni ridondanti per garantire alta disponibilità
W: Il traffico DNS viene distribuito casualmente tra i 13 Root Server
---
Q: Cosa afferma il Principio di Kerckhoffs?
A: Un sistema crittografico deve essere sicuro anche se l'algoritmo è pubblico — solo la chiave deve essere segreta
W: La sicurezza si ottiene tenendo segreti sia l'algoritmo che la chiave
W: La lunghezza della chiave è il fattore più importante per la sicurezza
W: Un algoritmo sicuro non deve mai essere reso pubblico
---
Q: Cosa si intende per Security through Obscurity e perché è pericolosa?
A: Nascondere il funzionamento del sistema come misura di sicurezza — è pericolosa perché se il sistema viene scoperto non ha protezione reale
W: Usare algoritmi così complessi da non poter essere compresi dagli attaccanti
W: Cifrare le chiavi crittografiche con altri algoritmi per nasconderle
W: Limitare la documentazione pubblica per ridurre la superficie di attacco
---
Q: Cos'è il One-Time Pad e perché è teoricamente inviolabile?
A: Usa una chiave casuale lunga quanto il messaggio usata una volta sola — il testo cifrato non rivela nulla sul testo in chiaro
W: Usa una chiave simmetrica di 256 bit rinnovata ad ogni messaggio
W: È inviolabile perché usa crittografia quantistica basata su principi fisici
W: Cifra il messaggio più volte con chiavi diverse derivate da un seed
---
Q: Quali sono le tre regole che deve rispettare la chiave di un OTP?
A: Deve essere lunga quanto il messaggio, totalmente casuale, usata una volta sola e poi distrutta
W: Deve essere di almeno 256 bit, condivisa in modo sicuro, rinnovata ogni 24 ore
W: Deve essere generata da un algoritmo certificato, custodita in un HSM, cambiata ogni sessione
W: Deve essere più lunga del messaggio, parzialmente casuale, usabile al massimo 10 volte
---
Q: Qual è il limite principale dell'OTP nella pratica?
A: La chiave deve essere lunga quanto il messaggio e distribuita in modo sicuro — impraticabile per grandi volumi di dati
W: È troppo lento per le CPU moderne richiedendo operazioni XOR ripetute
W: Non supporta messaggi più lunghi di 128 bit
W: È vulnerabile agli attacchi brute-force con computer quantistici moderni
---
Q: Cosa garantisce la Confusione nei cifrari a blocchi secondo Shannon?
A: Rende complessa la relazione tra chiave e testo cifrato — ogni bit della chiave influenza molti bit del cifrato
W: Distribuisce le proprietà statistiche del testo in chiaro su tutto il testo cifrato
W: Garantisce che blocchi identici producano blocchi cifrati diversi
W: Impedisce che due messaggi con la stessa chiave producano lo stesso cifrato
---
Q: Cosa garantisce la Diffusione nei cifrari a blocchi secondo Shannon?
A: Le proprietà statistiche del testo in chiaro vengono distribuite su tutto il testo cifrato nascondendo i pattern
W: Rende complessa la relazione tra la chiave e il testo cifrato
W: Garantisce che la modifica di un bit della chiave cambi tutto il cifrato
W: Impedisce gli attacchi brute-force aumentando lo spazio delle chiavi
---
Q: Cosa afferma il Criterio di Avalanche (SAC)?
A: Modificando un singolo bit del messaggio o della chiave ogni bit del cifrato ha il 50% di probabilità di cambiare
W: Modificando un bit del messaggio cambia esattamente la metà dei bit del cifrato
W: Modificando un bit del messaggio cambiano tutti i bit del cifrato
W: Modificando un bit della chiave il cifrato diventa completamente diverso
---
Q: Cosa fa una S-Box in un cifrario a blocchi?
A: Sostituisce un gruppo di bit di input con un diverso gruppo di bit di output garantendo la confusione
W: Rimescola l'ordine dei bit garantendo la diffusione
W: Combina i dati con la sottochiave tramite operazione XOR
W: Espande il blocco di dati aumentando il numero di bit da processare
---
Q: Cosa fa una P-Box in un cifrario a blocchi?
A: Rimescola la posizione dei bit distribuendo l'output di una S-Box come input di più S-Box successive
W: Sostituisce i bit di input con bit diversi usando una tabella di lookup
W: Combina i dati con la sottochiave tramite XOR
W: Comprime i bit riducendo la dimensione del blocco
---
Q: Qual è il vantaggio fondamentale delle Reti di Feistel?
A: La funzione F non deve essere invertibile permettendo di usare funzioni arbitrariamente complesse e sicure
W: Elaborano tutti i bit in parallelo rendendole molto più veloci
W: Non richiedono S-Box riducendo la complessità computazionale
W: Permettono chiavi di lunghezza arbitraria senza modificare la struttura
---
Q: Come funziona una rete di Feistel ad ogni round?
A: Il blocco è diviso in L e R — R diventa il nuovo L, e il nuovo R è L XOR F(R, sottochiave)
W: Il blocco intero viene passato alla funzione F con la sottochiave e il risultato è il nuovo blocco
W: L e R vengono entrambi passati alla funzione F e poi ricombinati tramite XOR
W: Il blocco viene diviso in 4 parti che vengono elaborate in parallelo
---
Q: Come si decifra con una rete di Feistel?
A: Si applica lo stesso algoritmo di cifratura ma con le sottochiavi in ordine inverso
W: Si applica un algoritmo di decifratura separato e diverso da quello di cifratura
W: Si invertono le operazioni della funzione F applicandola al contrario
W: Non è possibile decifrare — le reti di Feistel sono one-way
---
Q: Qual era la lunghezza effettiva della chiave DES?
A: 56 bit — su 64 formali, 8 bit sono usati per il controllo di parità
W: 64 bit tutti utilizzati per la cifratura
W: 128 bit come nel progetto originale Lucifer di IBM
W: 48 bit — il numero di bit delle sottochiavi usate nei 16 round
---
Q: Quanti round ha il DES?
A: 16 round
W: 10 round
W: 32 round
W: 8 round
---
Q: Perché il DES è considerato insicuro oggi?
A: La chiave di 56 bit permette solo 2^56 combinazioni — attaccabile con brute-force con hardware moderno
W: Le sue S-Box sono state trovate matematicamente deboli e pubblicate online
W: Usa una rete di Feistel con soli 8 round insufficienti per la sicurezza moderna
W: Il codice sorgente è pubblico permettendo agli attaccanti di trovare vulnerabilità
---
Q: Qual è la sequenza operativa del 3DES?
A: E-D-E — Cifratura con K1, Decifratura con K2, Cifratura con K3
W: E-E-E — tre cifrature consecutive con le tre chiavi
W: D-E-D — Decifratura, Cifratura, Decifratura per maggiore sicurezza
W: E-D-D — Cifratura con K1, Decifratura con K2, Decifratura con K3
---
Q: Nella Keying Option 3 del 3DES con K1=K2=K3, cosa si ottiene?
A: Compatibilità con il DES normale — la decifratura con K1 annulla la cifratura con K1
W: Sicurezza tripla equivalente a 168 bit effettivi
W: Una cifratura più lenta ma equivalente ad AES-128
W: Un errore — le tre chiavi devono essere sempre diverse
---
Q: Perché il 2DES non raddoppia la sicurezza a 112 bit?
A: A causa del Meet-in-the-Middle attack — un attaccante può attaccare i due stadi separatamente
W: Perché le due chiavi devono essere identiche per il protocollo
W: Perché DES applicato due volte produce lo stesso risultato di una sola applicazione
W: Perché il secondo DES decifra quello che il primo ha cifrato
---
Q: Qual è la dimensione del blocco in AES?
A: 128 bit in tutte le varianti (AES-128, AES-192, AES-256)
W: 64 bit come nel DES per retrocompatibilità
W: Variabile — 128 bit per AES-128, 192 per AES-192, 256 per AES-256
W: 256 bit per garantire la sicurezza military grade
---
Q: Quanti round usa AES con chiave a 128 bit?
A: 10 round
W: 16 round come DES
W: 14 round
W: 12 round
---
Q: Su quale tipo di struttura si basa AES a differenza di DES?
A: Una rete SP pura — non usa la struttura di Feistel
W: Una rete di Feistel come DES ma con più round
W: Una rete di Feistel modificata con quattro metà invece di due
W: Una struttura completamente nuova senza precedenti nella crittografia
---
Q: Cosa fa SubBytes in AES?
A: Sostituisce ogni byte della matrice con un valore diverso dalla S-Box garantendo confusione non lineare
W: Trasla le righe della matrice di posizioni diverse
W: Mescola matematicamente i byte di ogni colonna
W: Combina la matrice con la sottochiave tramite XOR
---
Q: Cosa fa AddRoundKey in AES?
A: Combina byte per byte la matrice State con la sottochiave del round corrente tramite XOR
W: Aggiunge bit casuali alla matrice per aumentare la confusione
W: Sostituisce ogni byte usando la sottochiave come indice nella S-Box
W: Ruota le colonne della matrice in base ai bit della sottochiave
---
Q: Qual è il difetto fatale della modalità ECB?
A: Blocchi di testo in chiaro identici producono blocchi cifrati identici rivelando i pattern nei dati
W: Non supporta messaggi più lunghi di un singolo blocco
W: Richiede un IV che deve essere trasmesso in chiaro aumentando l'overhead
W: Non può essere implementata in hardware richiede solo software
---
Q: Come risolve CBC il problema dell'ECB?
A: Prima di cifrare ogni blocco lo combina XOR con il blocco cifrato precedente rompendo i pattern
W: Usa una chiave diversa per ogni blocco derivata dalla chiave principale
W: Cifra ogni blocco due volte con chiavi diverse
W: Aggiunge padding casuale a ogni blocco prima della cifratura
---
Q: A cosa serve il Vettore di Inizializzazione (IV) in CBC?
A: Garantisce che due messaggi identici cifrati con la stessa chiave producano cifrati diversi
W: Serve come chiave aggiuntiva per il primo round di cifratura
W: Viene usato per autenticare il mittente del messaggio
W: Contiene la lunghezza del messaggio per permettere il corretto unpadding
---
Q: Perché CBC non può essere parallelizzato in fase di cifratura?
A: Ogni blocco dipende dal cifrato del blocco precedente — impossibile calcolare il blocco N senza il blocco N-1
W: Perché richiede accesso sequenziale al disco per leggere i dati
W: Perché la chiave viene modificata ad ogni round in modo sequenziale
W: Perché il IV deve essere aggiornato dopo ogni blocco in modo sequenziale
---
Q: Perché la modalità CTR è più efficiente di CBC?
A: I blocchi sono indipendenti — possono essere cifrati in parallelo su più core della CPU
W: Usa una chiave più corta riducendo il tempo di key schedule
W: Non richiede padding per l'ultimo blocco del messaggio
W: Usa operazioni più semplici che la CPU esegue più velocemente
---
Q: In CTR cosa viene dato come input all'algoritmo di cifratura invece del testo in chiaro?
A: Un contatore (Nonce + numero progressivo) che produce una sequenza pseudo-casuale
W: Il testo in chiaro direttamente come in ECB
W: Il testo in chiaro XOR con il blocco precedente come in CBC
W: La chiave principale senza alcuna modifica
---
Q: Cosa succede in RSA se si usa la stessa coppia (e,n) per cifrare?
A: Chiunque conosca la chiave pubblica (e,n) può cifrare messaggi ma solo chi ha (d,n) può decifrarli
W: Solo il proprietario della chiave può sia cifrare che decifrare
W: Chiunque può sia cifrare che decifrare conoscendo solo la chiave pubblica
W: La chiave pubblica può essere usata solo per verificare firme non per cifrare
---
Q: Cos'è la funzione Trapdoor (One-Way Function) su cui si basa RSA?
A: Moltiplicare due numeri primi è facile, ma fattorizzare il prodotto in numeri primi è computazionalmente impossibile
W: Calcolare l'hash di un messaggio è facile ma invertirlo è impossibile
W: Cifrare con la chiave pubblica è facile ma decifrare senza la chiave privata è impossibile
W: Generare numeri casuali è facile ma prevedere il prossimo numero è impossibile
---
Q: Quali valori compongono la chiave pubblica RSA?
A: La coppia (e, n) dove e è l'esponente pubblico e n è il modulo p×q
W: La coppia (d, n) dove d è l'esponente privato e n è il modulo
W: La coppia (p, q) dove p e q sono i due numeri primi scelti
W: La coppia (e, φ(n)) dove φ(n) è il totiente di Eulero
---
Q: Quali valori compongono la chiave privata RSA?
A: La coppia (d, n) dove d è l'inverso moltiplicativo modulare di e modulo φ(n)
W: La coppia (e, n) dove e è l'esponente e n è il modulo
W: La coppia (p, q) — i due numeri primi originali
W: La coppia (d, φ(n)) dove φ(n) è il totiente di Eulero
---
Q: Come si usa RSA nella crittografia ibrida?
A: Per cifrare e scambiare in modo sicuro la piccola chiave di sessione simmetrica
W: Per cifrare l'intero messaggio garantendo la massima sicurezza
W: Per generare i numeri casuali usati negli algoritmi simmetrici
W: Per autenticare il server durante la connessione HTTPS
---
Q: Quali sono le quattro proprietà fondamentali di una funzione di hash crittografica?
A: Efficienza computazionale, pre-image resistance, collision resistance, effetto valanga
W: Velocità, segretezza, unicità, reversibilità
W: Compressione, autenticazione, integrità, non ripudio
W: Unidirezionalità, bidirezionalità, compressione, espansione
---
Q: Perché l'hash non è cifratura?
A: L'hash distrugge informazioni e non è reversibile — la cifratura è bidirezionale e permettere la decifratura
W: L'hash usa chiavi pubbliche mentre la cifratura usa chiavi simmetriche
W: L'hash produce output di lunghezza variabile mentre la cifratura produce output fisso
W: L'hash è più lento della cifratura e non adatto per grandi volumi di dati
---
Q: Come vengono conservate le password nei database ben progettati?
A: Viene salvato solo l'hash della password — al login si ricalcola l'hash e si confronta
W: Vengono cifrate con AES-256 usando una chiave master del server
W: Vengono salvate in chiaro in un database separato con accesso limitato
W: Vengono cifrate con la chiave pubblica dell'utente
---
Q: Cosa garantisce il Non Ripudio nella firma digitale?
A: Il firmatario non può negare di aver firmato — solo lui possiede la chiave privata usata per generare la firma
W: Il documento firmato non può essere letto da terzi non autorizzati
W: La firma viene verificata automaticamente da un'autorità centrale
W: Il documento firmato non può essere modificato neanche dal firmatario
---
Q: Cosa contiene una busta crittografica CAdES o PAdES?
A: Il documento originale, l'hash cifrato con la chiave privata del firmatario, e il certificato digitale del firmatario
W: Il documento cifrato con la chiave pubblica del destinatario
W: Solo l'hash del documento e la chiave pubblica del firmatario
W: Il documento e la chiave simmetrica usata per cifrarlo
---
Q: Qual è la differenza pratica tra CAdES e PAdES?
A: CAdES funziona per qualsiasi file e produce un .p7m, PAdES è solo per PDF e la firma è integrata nel file
W: PAdES produce un .p7m separato, CAdES integra la firma nel documento
W: CAdES è più sicuro perché usa RSA-4096 mentre PAdES usa RSA-2048
W: Non c'è differenza pratica — sono formati intercambiabili
---
Q: Perché un file .p7m (CAdES) richiede software apposito per essere aperto?
A: Il formato .p7m è una busta crittografica che richiede software specifico per estrarre il documento e verificare la firma
W: Perché il documento è cifrato e serve la chiave privata per aprirlo
W: Perché .p7m è un formato proprietario non supportato dai sistemi operativi standard
W: Perché contiene virus e il sistema operativo lo blocca preventivamente
---
Q: Cos'è un certificato digitale X.509?
A: Un documento informatico che attesta l'autenticità della chiave pubblica dell'intestatario firmato da una CA
W: Una password cifrata usata per autenticare l'utente presso i server
W: Una chiave simmetrica condivisa tra client e server per la cifratura
W: Un file che contiene le regole di accesso dell'utente alle risorse di rete
---
Q: Cosa contiene un certificato digitale X.509?
A: Dati dell'intestatario, dati del certificato (numero seriale, scadenza), dati della CA e firma digitale della CA
W: La chiave privata dell'intestatario cifrata con la chiave della CA
W: Solo la chiave pubblica dell'intestatario senza altri metadati
W: Le credenziali di accesso dell'utente cifrate con la chiave della CA
---
Q: Cos'è la Chain of Trust nei certificati digitali?
A: Una catena gerarchica in cui ogni certificato è firmato da una CA superiore fino alla Root CA pre-installata nel sistema
W: Una lista di tutti i certificati emessi dalla stessa CA
W: Il percorso di rete seguito dai pacchetti cifrati con SSL/TLS
W: La sequenza di operazioni matematiche usate per generare una coppia di chiavi
---
Q: Perché un certificato self-signed causa un avviso di sicurezza nel browser?
A: Nessuna Root CA fidata garantisce per esso — la catena di fiducia non può essere verificata
W: Perché usa algoritmi crittografici obsoleti non supportati dai browser moderni
W: Perché non contiene la chiave pubblica del server
W: Perché scade dopo 24 ore e il browser lo considera già scaduto
---
Q: Cos'è un Distributed Ledger (Registro Distribuito)?
A: Un registro copiato e distribuito a tutti i nodi della rete — non esiste una copia centrale
W: Un database centralizzato con accesso distribuito a tutti gli utenti
W: Un sistema di backup che replica i dati su più server geograficamente distanti
W: Un protocollo per sincronizzare database tra sedi aziendali diverse
---
Q: Cosa contiene ogni blocco nella blockchain?
A: I dati delle transazioni, il timestamp, l'hash del blocco corrente e l'hash del blocco precedente
W: Solo i dati delle transazioni cifrati con la chiave pubblica del mittente
W: I dati delle transazioni e la firma digitale del nodo che ha creato il blocco
W: L'hash del blocco corrente e le chiavi pubbliche di tutti i partecipanti
---
Q: Perché la blockchain è considerata immutabile?
A: Modificare un blocco cambia il suo hash invalidando a cascata tutti i blocchi successivi che lo referenziano
W: Perché i dati sono cifrati con AES-256 rendendo impossibile la modifica
W: Perché ogni transazione richiede l'approvazione di tutti i nodi della rete
W: Perché le chiavi private necessarie per modificare i dati sono distrutte dopo la creazione
---
Q: Cosa dovrebbe fare un attaccante per modificare un blocco nella blockchain e farla franca?
A: Ricalcolare l'hash di quel blocco e di tutti i successivi su almeno il 51% dei nodi della rete simultaneamente
W: Ottenere la chiave privata del proprietario del blocco da modificare
W: Convincere la CA a emettere un certificato falso per autenticarsi come nodo legittimo
W: Disabilitare temporaneamente il consenso della rete e reinserire il blocco modificato
---
"""

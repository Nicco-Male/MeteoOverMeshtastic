# MeteoOverMeshtastic – Guida completa all'uso

**MeteoOverMeshtastic** è uno script in Python che inoltra le osservazioni della propria stazione Meteo (via Weather Underground) sulla rete **Meshtastic**.  È stato pensato per essere leggero, configurabile tramite variabili d’ambiente e facilmente integrabile come servizio periodico.  Questa guida spiega passo per passo come installare, configurare ed eseguire il programma, in modo che anche i principianti possano utilizzarlo senza problemi.

## 1. Requisiti

Prima di iniziare assicurati di avere:

- **Python 3.8 o superiore** installato sul tuo sistema. Lo script utilizza un ambiente virtuale, quindi la versione di Python di sistema non sarà modificata.
- Una **stazione Weather Underground** attiva e relativa **chiave API** (API key) per recuperare i dati meteo.
- Un **dispositivo Meshtastic** configurato e acceso; può essere raggiunto in modalità **TCP**, **seriale** oppure lasciato in modalità *auto* (lo script sceglie in base ai parametri forniti).
- Accesso alla shell del sistema su cui verrà eseguito lo script e, se vuoi usare **systemd**, privilegi da amministratore per installare unità di servizio.

## 2. Installazione rapida

Per un’installazione rapida e senza sorprese puoi utilizzare lo script `setup.sh` incluso nel progetto.  Questo script crea un ambiente virtuale e installa tutte le dipendenze necessarie.  Ecco come procedere:

1. **Clona** o **scarica** il repository in una directory a tua scelta:

   ```bash
   git clone https://github.com/Nicco-Male/MeteoOverMeshtastic.git
   cd MeteoOverMeshtastic
   ```

2. **Rendi eseguibile** lo script di setup e avvialo:

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   Lo script creerà la cartella `.venv`, installerà l’ultima versione di `pip` e tutte le dipendenze elencate in `requirements.txt`. Al termine comparirà un messaggio con i comandi per attivare la virtualenv e per avviare il programma.

3. **Copia il file di esempio `.env`** e personalizza i valori:

   ```bash
   cp .env.example .env
   nano .env
   ```

   Nel prossimo capitolo viene spiegato il significato di ogni variabile.

## 3. Configurazione tramite `.env`

Lo script legge i parametri di configurazione dalle **variabili d’ambiente** e, se presente, dal file `.env` usando la libreria `python‑dotenv`.  L’esempio contenuto in `.env.example` è un ottimo punto di partenza.  Di seguito è riportata la lista completa delle variabili supportate:

| Variabile | Descrizione | Valore di default / Obbligatorio |
| --- | --- | --- |
| `WEATHER_API_KEY` | **Chiave API Weather Underground**. È indispensabile per interrogare le API e recuperare le osservazioni meteo. | *Obbligatoria* – se non impostata lo script si interrompe con errore. |
| `STATION_ID` | ID della stazione su Weather Underground. | `test` |
| `UNITS` | Unità di misura da usare per le API (`m` per metriche, `e` per imperiali, ecc.). | `m` |
| `WEATHER_URL` | Endpoint API di Weather Underground da cui prelevare i dati. | `https://api.weather.com/v2/pws/observations/current` |
| `LOCATION_NAME` | Nome della località che comparirà nel messaggio inviato su Meshtastic. | `TestName (region)` |
| `TIMEZONE` | Fuso orario per formattare data e ora del messaggio. Usa l’identificatore [IANA TZ](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones), ad esempio `Europe/Rome`. | `Europe/Rome` |
| `MESHTASTIC_MODE` | Modalità di connessione a Meshtastic. Può essere `tcp`, `serial` oppure `auto`. In modalità `auto` lo script prova a usare la porta seriale (`MESHTASTIC_SERIAL_PORT`) e, se non trovata, passa alla connessione TCP (`MESHTASTIC_IP` + `MESHTASTIC_PORT`). | `auto` |
| `MESHTASTIC_IP` | Indirizzo IP del dispositivo Meshtastic per la connessione TCP. Necessario se `MESHTASTIC_MODE` è `tcp`. | — |
| `MESHTASTIC_PORT` | Porta TCP del dispositivo Meshtastic. | `4403` |
| `MESHTASTIC_SERIAL_PORT` | Dispositivo seriale (es. `/dev/ttyUSB0` su Linux, `COM3` su Windows). Necessario se `MESHTASTIC_MODE` è `serial`. | — |
| `DESTINATION_NODE` | ID del nodo Meshtastic destinatario. Se lasciato vuoto o impostato a `None` lo script invierà il messaggio in **broadcast**. | *Nessun default* |
| `CHANNEL_INDEX` | Indice del canale Meshtastic su cui inviare il messaggio. | `1` |
| `RUN_INTERVAL_HOURS` | Intervallo in ore per l’esecuzione periodica con systemd timer. Viene utilizzato dallo script di installazione systemd. | `4` (nel file di esempio) |

**Consiglio:** dopo aver modificato `.env`, verifica di non aver lasciato spazi o virgolette indesiderate e assicurati che la chiave API sia corretta.  In caso di errori di configurazione, lo script stampa messaggi esplicativi e termina l’esecuzione.

## 4. Come funziona lo script

Una volta avviato, lo script esegue i seguenti passi:

1. **Carica le variabili d’ambiente** dal file `.env` tramite `python‑dotenv`.
2. **Determina la modalità di connessione** a Meshtastic (`tcp`, `serial` o `auto`):
   - In modalità `tcp`, verifica che `MESHTASTIC_IP` e `MESHTASTIC_PORT` siano impostati e costruisce l’indirizzo `ip:porta`.
   - In modalità `serial`, richiede `MESHTASTIC_SERIAL_PORT`.
   - In modalità `auto`, preferisce la porta seriale se definita, altrimenti usa la connessione TCP.
   Se nessuna configurazione è disponibile viene emesso un errore esplicativo.
3. **Recupera i dati meteo** da Weather Underground usando l’endpoint definito e la chiave API.  Eventuali eccezioni (ad esempio assenza della chiave API o problemi di rete) vengono segnalate sullo standard output e non interrompono il resto del sistema.
4. **Estrae e formatta i campi** (temperatura, umidità, vento, precipitazioni, pressione) creando un messaggio con emoji e unità di misura.  La data e l’ora sono formattate secondo la timezone impostata.
5. **Invia il messaggio** al nodo di destinazione tramite la libreria Meshtastic: se `DESTINATION_NODE` è impostata, il messaggio viene recapitato a quel nodo; altrimenti viene trasmesso in broadcast.  Dopo l’invio l’interfaccia viene chiusa e viene stampato un log.

Il file `MeteoOverMeshtastic.py` è scritto in modo modulare: se desideri cambiare i campi da visualizzare o la formattazione del messaggio, puoi modificare il dizionario `JSON_FIELDS` o la funzione `format_weather_message` contenuta nel file.

## 5. Esecuzione manuale

Per lanciare lo script manualmente (ad esempio per un test), attiva la virtualenv e avvia il programma:

```bash
.venv/bin/python MeteoOverMeshtastic.py
```

Se tutto è configurato correttamente vedrai i log con indicazioni della modalità di connessione (`Connessione TCP a IP:porta` oppure `Connessione seriale su /dev/ttyUSB0`), l’eventuale recupero dei dati meteo e l’invio del messaggio.

## 6. Esecuzione automatica con systemd

Se desideri che MeteoOverMeshtastic invii i dati a intervalli regolari senza dover eseguire manualmente il programma, puoi utilizzare gli script e le unità forniti nella cartella `deploy/systemd`.  Questo metodo è consigliato per server domestici o dispositivi Raspberry Pi sempre accesi.

### 6.1 Contenuto della cartella `deploy/systemd`

La cartella contiene quattro file principali:

- `meteo-over-meshtastic.service`: unità di servizio che definisce la directory di lavoro, il percorso del programma e l’utente con cui eseguirlo.
- `meteo-over-meshtastic.timer`: definisce l’intervallo di esecuzione in minuti tramite il placeholder `@RUN_INTERVAL_HOURS@`.
- `start-meteo.sh`: wrapper che carica il file `.env` e avvia il programma, stampando a log l’intervallo corrente.
- `install.sh`: script che sostituisce i placeholder nei file unit, copia le unità nella directory `/etc/systemd/system`, ricarica systemd e abilita il timer.

### 6.2 Installazione del servizio

1. Assicurati che il file `.env` contenga la variabile `RUN_INTERVAL_HOURS` con l’intervallo desiderato, ad esempio:

   ```ini
   RUN_INTERVAL_HOURS=4
   ```

2. Esegui lo script di installazione con i privilegi di root:

   ```bash
   sudo ./deploy/systemd/install.sh
   ```

   Lo script copierà le unità in `/etc/systemd/system`, sostituirà i placeholder con i valori del tuo progetto e abiliterà il timer. Al termine riceverai un messaggio con l’intervallo impostato.

3. Verifica lo stato del servizio e del timer con:

   ```bash
   systemctl status meteo-over-meshtastic.service
   systemctl status meteo-over-meshtastic.timer
   ```

4. Per modificare l’intervallo in futuro, aggiorna `RUN_INTERVAL_MINUTES` in `.env` e riesegui `sudo ./deploy/systemd/install.sh`.

### 6.3 Esecuzione con un utente dedicato

Nel file di servizio predefinito, la direttiva `User=meteo` definisce l’utente con cui viene eseguito lo script.  Puoi modificare questo valore per utilizzare un utente diverso, a patto che abbia accesso alla directory del progetto. Ricorda di creare l’utente e concedergli i permessi necessari prima di installare il servizio.

## 7. Aggiornamenti e manutenzione

Per aggiornare il progetto:

1. Esegui un `git pull` nella cartella del repository per recuperare eventuali nuove versioni.
2. Avvia di nuovo lo script `setup.sh` per aggiornare le dipendenze, se necessario.
3. Se utilizzi systemd, riesegui lo script `deploy/systemd/install.sh` con `sudo` per aggiornare il servizio.

Ricorda di verificare periodicamente la scadenza della tua API key di Weather Underground e di mantenerla segreta.  È buona pratica non committare il file `.env` su repository pubblici.

## 8. Risoluzione dei problemi

| Problema | Possibile causa e soluzione |
| --- | --- |
| **Errore “WEATHER_API_KEY non impostata”** | La variabile `WEATHER_API_KEY` non è definita nel file `.env`. Aggiungila e assicurati che il valore sia corretto. |
| **Messaggio “[ERRORE] MESHTASTIC_MODE=tcp richiede MESHTASTIC_IP e MESHTASTIC_PORT”** | Hai impostato `MESHTASTIC_MODE=tcp` ma non hai definito `MESHTASTIC_IP` o `MESHTASTIC_PORT`. Compila entrambi o passa a modalità `auto`. |
| **Il programma stampa “Connessione Meshtastic fallita”** | La connessione al dispositivo non è riuscita. Verifica che il dispositivo sia acceso, che l’IP/porta o la porta seriale siano corretti e che eventuali firewall non blocchino la connessione. |
| **Non arrivano dati meteo** | Controlla che la stazione Weather Underground invii regolarmente i dati e che l’ID e la chiave API siano corretti. In caso di timeout o HTTP error la funzione `get_weather_data` segnala l’errore. |
| **Il messaggio mostra “Nessun dato meteo disponibile.”** | La variabile `fallback_message` è usata se non ci sono osservazioni oppure se si verifica un’eccezione durante la formattazione. Verifica la configurazione e lo stato della stazione. |

## 9. Licenza

Questo progetto è rilasciato con doppia licenza: **MIT** per il codice e **CC BY‑SA 4.0** per la documentazione, come indicato nei file `LICENSE-CODE` e `LICENSE-DOCS`.  Puoi utilizzare e modificare il software liberamente rispettando i termini delle licenze.

---

Speriamo che questa guida dettagliata ti aiuti ad utilizzare MeteoOverMeshtastic senza intoppi. In caso di dubbi o problemi, apri un ticket nel repository GitHub oppure contribuisci con miglioramenti alla documentazione.

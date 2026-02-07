# MeteoOverMeshtastic

Invia le osservazioni di Weather Underground tramite Meshtastic.

## Guida rapida

1. Rendi eseguibile lo script di setup:

   ```bash
   chmod +x ./setup.sh
   ```

2. Crea il file `.env` a partire dall'esempio:

   ```bash
   cp .env.example .env
   ```

3. Apri `.env` e compila i valori. Esempio:

   ```ini
   WEATHER_API_KEY=la_tua_chiave_api
   STATION_ID=la_tua_stazione
   UNITS=m
   MESHTASTIC_MODE=auto
   MESHTASTIC_IP=192.168.0.60
   MESHTASTIC_PORT=4403
   MESHTASTIC_SERIAL_PORT=
   DESTINATION_NODE=
   CHANNEL_INDEX=1
   WEATHER_URL=https://api.weather.com/v2/pws/observations/current
   LOCATION_NAME=Bientina (Pi)
   ```
   

4. Avvia lo script di setup:

   ```bash
   ./setup.sh
   ```
   
 5.  Avvia il programma usando l'interprete della venv:

   ```bash
   .venv/bin/python MeteoOverMeshtastic.py
   ```

## Guida dettagliata a `.env` e configurazione

Lo script legge le impostazioni tramite variabili d'ambiente (con `os.getenv`) e
carica automaticamente il file `.env` tramite `python-dotenv`. Le voci che
seguono sono allineate al file `.env.example` e alle impostazioni definite in
`MeteoOverMeshtastic.py`. 

### 1) Preparazione del file `.env`

1. Copia il file di esempio:

   ```bash
   cp .env.example .env
   ```

2. Apri `.env` e compila i valori. Esempio:

   ```ini
   WEATHER_API_KEY=la_tua_chiave_api
   STATION_ID=la_tua_stazione
   UNITS=m
   MESHTASTIC_MODE=auto
   MESHTASTIC_IP=192.168.0.60
   MESHTASTIC_PORT=4403
   MESHTASTIC_SERIAL_PORT=
   DESTINATION_NODE=
   CHANNEL_INDEX=1
   WEATHER_URL=https://api.weather.com/v2/pws/observations/current
   LOCATION_NAME=Bientina (Pi)
   ```

### 2) Caricamento automatico del `.env`

Se il file `.env` è presente nella cartella del progetto, viene caricato in
automatico all'avvio. Puoi comunque sovrascrivere le variabili esportandole
manualmente prima di eseguire lo script (ad esempio con `export`).

### 3) Variabili disponibili e significato

Le variabili seguenti controllano la configurazione principale:

| Variabile | Descrizione | Default |
| --- | --- | --- |
| `WEATHER_API_KEY` | Chiave API Weather Underground. **Obbligatoria**. | Nessun default (se manca, lo script si ferma). |
| `STATION_ID` | ID della stazione Weather Underground. | `test` |
| `UNITS` | Unità di misura per le osservazioni (`m` per metriche). | `m` |
| `WEATHER_URL` | Endpoint API Weather Underground. | `https://api.weather.com/v2/pws/observations/current` |
| `LOCATION_NAME` | Nome località mostrato nel messaggio inviato. | `TestName (region)` |
| `MESHTASTIC_MODE` | Modalità Meshtastic (`tcp`, `serial` o `auto`). | `auto` |
| `MESHTASTIC_IP` | IP del dispositivo Meshtastic (modalità TCP). | `192.168.0.60` |
| `MESHTASTIC_PORT` | Porta TCP del dispositivo Meshtastic. | `4403` |
| `MESHTASTIC_SERIAL_PORT` | Porta seriale Meshtastic (modalità serial). | Nessun default. |
| `DESTINATION_NODE` | Nodo di destinazione Meshtastic. Vuoto o `None` per il broadcast. | Nessun default (broadcast). |
| `CHANNEL_INDEX` | Indice del canale Meshtastic usato per l'invio. | `1` |

### 4) Configurazione lato Meshtastic

Nel file `MeteoOverMeshtastic.py` la sezione **CONFIGURAZIONE MESHTASTIC**
definisce:

- **Connessione TCP**: lo script usa `MESHTASTIC_IP` e `MESHTASTIC_PORT` per
  costruire la stringa `ip:porta` (es. `192.168.0.60:4403`).
- **Modalità**: lo script legge `MESHTASTIC_MODE` (`tcp`, `serial` o `auto`) e
  decide se usare la connessione TCP o seriale in base alle variabili presenti.
- **`destination_node`** e **`channel_index`**: ora derivano da
  `DESTINATION_NODE` e `CHANNEL_INDEX`. Se `DESTINATION_NODE` è vuoto o `None`
  il messaggio viene inviato in broadcast, altrimenti a un nodo specifico.

Se vuoi usare una connessione seriale, imposta `MESHTASTIC_MODE=serial` e
configura `MESHTASTIC_SERIAL_PORT` con un device seriale (es. `/dev/ttyUSB0`
o `COM3`).

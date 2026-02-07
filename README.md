# MeteoOverMeshtastic

Invia le osservazioni di Weather Underground tramite Meshtastic.

## Guida rapida

1. Rendi eseguibile lo script di setup:

   ```bash
   chmod +x ./setup.sh
   ```

2. Avvia lo script di setup:

   ```bash
   ./setup.sh
   ```

3. Avvia il programma usando l'interprete della venv:

   ```bash
   .venv/bin/python MeteoOverMeshtastic.py
   ```

## Installazione

1. Crea e attiva un ambiente virtuale (opzionale ma consigliato).
2. Installa le dipendenze prima di eseguire lo script:

```bash
pip install -r requirements.txt
```

3. Copia `.env.example` in `.env` e aggiorna i valori richiesti.

### Problemi di permessi durante `pip install`

Se vedi un errore simile a:

```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied: '.../site-packages/...'
```

significa che stai installando in un ambiente non scrivibile (es. una venv
di sistema in `/opt`). La soluzione consigliata è usare una venv nella home:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

In alternativa (meno consigliata), puoi installare in user space:

```bash
pip install --user -r requirements.txt
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
   MESHTASTIC_IP=192.168.0.60
   MESHTASTIC_PORT=4403
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
| `MESHTASTIC_IP` | IP del dispositivo Meshtastic (modalità TCP). | `192.168.0.60` |
| `MESHTASTIC_PORT` | Porta TCP del dispositivo Meshtastic. | `4403` |

### 4) Configurazione lato Meshtastic

Nel file `MeteoOverMeshtastic.py` la sezione **CONFIGURAZIONE MESHTASTIC**
definisce:

- **Connessione TCP**: lo script usa `MESHTASTIC_IP` e `MESHTASTIC_PORT` per
  costruire la stringa `ip:porta` (es. `192.168.0.60:4403`).
- **`is_tcp`**: è impostato a `True`, quindi la connessione seriale non viene
  usata (a meno di modificare il codice).
- **`destination_node`** e **`channel_index`**: se `destination_node` è `None`
  il messaggio viene inviato in broadcast, altrimenti a un nodo specifico.

Se vuoi usare una connessione seriale, devi cambiare `is_tcp` a `False` e
impostare `port` con un device seriale (es. `/dev/ttyUSB0` o `COM3`).

### 5) Configurazione Weather Underground

La sezione **CONFIGURAZIONE WEATHER UNDERGROUND** usa le variabili d'ambiente
per creare la richiesta API e mappa i campi JSON in `JSON_FIELDS`. Se la chiave
API non è impostata, lo script stampa un errore e termina l'acquisizione dei
dati.

### 6) Esecuzione completa (esempio)

```bash
python MeteoOverMeshtastic.py
```

### Script di setup (opzionale)

Se preferisci, puoi usare lo script di supporto per creare un ambiente virtuale
e installare i requisiti. Prima rendilo eseguibile:

```bash
chmod +x ./setup.sh
```

Poi eseguilo:

```bash
./setup.sh
```

## Esecuzione

Se hai usato lo script di setup, l'avvio consigliato utilizza l'interprete
virtuale creato in `.venv`:

```bash
.venv/bin/python MeteoOverMeshtastic.py
```

In alternativa, se hai attivato manualmente la venv, puoi usare `python`:

```bash
python MeteoOverMeshtastic.py
```

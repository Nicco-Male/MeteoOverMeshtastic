# Systemd

Questa cartella contiene i file di esempio per eseguire MeteoOverMeshtastic con
`systemd` e un timer configurabile tramite `.env`.

## File inclusi

- `meteo-over-meshtastic.service`: unità di servizio con i percorsi del
  progetto e la variabile `EnvironmentFile`.
- `meteo-over-meshtastic.timer`: timer con placeholder
  `@RUN_INTERVAL_HOURS@` (da sostituire in fase di installazione).
- `start-meteo.sh`: wrapper che carica `.env`, logga l'intervallo e avvia una
  singola esecuzione (il loop è gestito da `systemd`).
- `install.sh`: script di installazione che legge `.env`, genera le unità in
  `/etc/systemd/system` e abilita il timer.

## Installazione

1. Assicurati che `.env` contenga `RUN_INTERVAL_HOURS`:

   ```ini
   RUN_INTERVAL_HOURS=2
   ```

2. Esegui lo script di installazione con privilegi di root:

   ```bash
   sudo ./deploy/systemd/install.sh
   ```

## Aggiornare l'intervallo

1. Modifica `RUN_INTERVAL_HOURS` in `.env`.
2. Rilancia lo script di installazione:

   ```bash
   sudo ./deploy/systemd/install.sh
   ```

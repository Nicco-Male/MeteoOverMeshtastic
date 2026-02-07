import meshtastic
import meshtastic.serial_interface
import meshtastic.tcp_interface
import sys
import os
import requests
import json
from datetime import datetime
import pytz

# -------------------------------------------------
# CONFIGURAZIONE MESHTASTIC
# -------------------------------------------------

MESHTASTIC_MODE = os.getenv("MESHTASTIC_MODE", "auto").lower()
MESH_IP = os.getenv("MESHTASTIC_IP")
MESH_PORT = os.getenv("MESHTASTIC_PORT")
SERIAL_PORT = os.getenv("MESHTASTIC_SERIAL_PORT")

is_tcp = False
port = None  # es. "COM3" o "/dev/ttyUSB0" o "192.168.1.199:4403"

if MESHTASTIC_MODE == "tcp":
    if not MESH_IP or not MESH_PORT:
        print("[ERRORE] MESHTASTIC_MODE=tcp richiede MESHTASTIC_IP e MESHTASTIC_PORT.")
        sys.exit(1)
    port = f"{MESH_IP}:{MESH_PORT}"
    is_tcp = True
elif MESHTASTIC_MODE == "serial":
    if not SERIAL_PORT:
        print("[ERRORE] MESHTASTIC_MODE=serial richiede MESHTASTIC_SERIAL_PORT.")
        sys.exit(1)
    port = SERIAL_PORT
    is_tcp = False
elif MESHTASTIC_MODE == "auto":
    if SERIAL_PORT:
        port = SERIAL_PORT
        is_tcp = False
    elif MESH_IP and MESH_PORT:
        port = f"{MESH_IP}:{MESH_PORT}"
        is_tcp = True
    else:
        print("[ERRORE] Nessuna configurazione Meshtastic trovata. Imposta MESHTASTIC_SERIAL_PORT oppure MESHTASTIC_IP e MESHTASTIC_PORT.")
        sys.exit(1)
else:
    print(f"[ERRORE] MESHTASTIC_MODE non valido: {MESHTASTIC_MODE}. Usa tcp, serial o auto.")
    sys.exit(1)

destination_node = None
channel_index    = 1

fallback_message = "Nessun dato meteo disponibile."

# -------------------------------------------------
# CONFIGURAZIONE WEATHER UNDERGROUND (come ESEMPIO)
# -------------------------------------------------

# Imposta le variabili d'ambiente prima di avviare lo script (vedi .env.example).
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
STATION_ID      = os.getenv("STATION_ID", "test")
UNITS           = os.getenv("UNITS", "m")

WEATHER_URL = os.getenv("WEATHER_URL", "https://api.weather.com/v2/pws/observations/current")

LOCATION_NAME = os.getenv("LOCATION_NAME", "TestName (region)")
TIMEZONE = os.getenv("TIMEZONE", "Europe/Rome")

JSON_FIELDS = {
    "temperature": ("metric", "temp"),
    "humidity": "humidity",
    "wind_speed": ("metric", "windSpeed"),
    "precip_rate": ("metric", "precipRate"),
    "precip_total": ("metric", "precipTotal"),
    "pressure": ("metric", "pressure")
}

# -------------------------------------------------
# FUNZIONI WEATHER UNDERGROUND
# -------------------------------------------------

def get_weather_data():
    if not WEATHER_API_KEY:
        print("[ERRORE] WEATHER_API_KEY non impostata. Configura la variabile d'ambiente WEATHER_API_KEY.")
        return None
    params = {
        "stationId": STATION_ID,
        "format": "json",
        "units": UNITS,
        "apiKey": WEATHER_API_KEY
    }

    try:
        r = requests.get(WEATHER_URL, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERRORE] Chiamata Weather Underground fallita: {e}")
        return None


def extract_field(obs, field):
    if isinstance(field, tuple):
        return obs.get(field[0], {}).get(field[1])
    return obs.get(field)


def format_weather_message(weather_json):
    try:
        observations = weather_json.get("observations")
        if not observations:
            return fallback_message

        obs = observations[0]

        def default_value(value, default="N/D"):
            return default if value is None else value

        temp = default_value(extract_field(obs, JSON_FIELDS["temperature"]))
        hum  = default_value(extract_field(obs, JSON_FIELDS["humidity"]))
        wind = default_value(extract_field(obs, JSON_FIELDS["wind_speed"]))
        rain = default_value(extract_field(obs, JSON_FIELDS["precip_rate"]))
        rtot = default_value(extract_field(obs, JSON_FIELDS["precip_total"]))
        pres = default_value(extract_field(obs, JSON_FIELDS["pressure"]))

        try:
            tz = pytz.timezone(TIMEZONE)
        except Exception as e:
            print(f"[ERRORE] Timezone non valida '{TIMEZONE}': {e}. Uso UTC.")
            tz = pytz.UTC
        now = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")

        msg = (
            f"{LOCATION_NAME}\n"
            f"Meteo alle {now}\n"
            f"Temp: {temp} °C\n"
            f"Umidità: {hum} %\n"
            f"Vento: {wind} km/h\n"
            f"Pioggia: {rain} mm\n"
            f"Da mezzanotte: {rtot} mm\n"
            f"Pressione: {pres} hPa"
        )

        return msg

    except Exception as e:
        print(f"[ERRORE] Formattazione meteo fallita: {e}")
        return fallback_message

# -------------------------------------------------
# MESHTASTIC
# -------------------------------------------------

def send_message(iface, text):
    try:
        if destination_node:
            iface.sendText(text, destinationId=destination_node, channelIndex=channel_index)
            print(f"[INFO] Messaggio inviato a nodo {destination_node}:\n{text}")
        else:
            iface.sendText(text, channelIndex=channel_index)
            print(f"[INFO] Messaggio broadcast inviato:\n{text}")
    except Exception as e:
        print(f"[ERRORE] Invio messaggio fallito: {e}")
    finally:
        iface.close()


def on_connected(iface):
    print("[INFO] Connesso al dispositivo Meshtastic. Recupero meteo...")
    weather = get_weather_data()
    if weather:
        msg = format_weather_message(weather)
    else:
        msg = fallback_message
    send_message(iface, msg)

# -------------------------------------------------
# AVVIO
# -------------------------------------------------

try:
    if is_tcp:
        print(f"[INFO] Connessione TCP a {port}...")
        ip, tcp_port = port.split(":")
        interface = meshtastic.tcp_interface.TCPInterface(ip, int(tcp_port))
    else:
        print(f"[INFO] Connessione seriale su {port}...")
        interface = meshtastic.serial_interface.SerialInterface(port)
except Exception as e:
    print(f"[ERRORE] Connessione Meshtastic fallita: {e}")
    sys.exit(1)

if getattr(interface, "isConnected", False) or getattr(interface, "is_connected", False):
    on_connected(interface)
else:
    interface.onConnected = on_connected

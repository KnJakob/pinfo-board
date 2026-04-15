import requests
import streamlit as st


@st.cache_data(ttl=3600)
def get_weather_data():
    # Letzte 2h + naechste 22h fuer ein zukunftsorientiertes Diagramm
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 52.52,
        "longitude": 13.41,
        "hourly": "temperature_2m,rain,cloud_cover,weather_code,is_day",
        "timezone": "Europe/Berlin",
        "past_hours": 2,
        "forecast_hours": 22,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error when retrieving weather {e}")
        return None


# weather code
def get_weather_icon(wmo_code):
    if wmo_code == 0:
        return "☀️"  # Klar
    elif wmo_code in [1, 2, 3]:
        return "⛅"  # Leicht bis stark bewölkt
    elif wmo_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "🌧️"  # Regen/Schauer
    elif wmo_code in [71, 73, 75, 85, 86]:
        return "❄️"  # Schnee
    elif wmo_code in [95, 96, 99]:
        return "⛈️"  # Gewitter
    else:
        return "🌫️"  # Nebel oder unklar

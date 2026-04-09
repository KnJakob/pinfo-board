import requests

def get_weather_data():
    # sunset, sunrise
    # rain, temperature
    url = "https://api.open-meteo.com/v1/forecast?latitude=52.52&longitude=13.41&daily=sunrise,sunset&hourly=temperature_2m,rain,cloud_cover,weather_code&timezone=Europe%2FBerlin&forecast_days=1"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error when retrieving weather {e}")
        return None

# weather code
def get_weather_icon(wmo_code):
    if wmo_code == 0: return "☀️" # Klar
    elif wmo_code in [1, 2, 3]: return "⛅" # Leicht bis stark bewölkt
    elif wmo_code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: return "🌧️" # Regen/Schauer
    elif wmo_code in [71, 73, 75, 85, 86]: return "❄️" # Schnee
    elif wmo_code in [95, 96, 99]: return "⛈️" # Gewitter
    else: return "🌫️" # Nebel oder unklar


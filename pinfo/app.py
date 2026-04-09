import streamlit as st
import pandas as pd
from utils import weather
from datetime import datetime

# Seitenkonfiguration (muss als erstes aufgerufen werden)
st.set_page_config(page_title="Pi Wetter-Dashboard", layout="wide")

st.title("Berlin Wetterbericht 🐻")

# Daten abrufen
data = weather.get_weather_data()

if data:
    # --- Tägliche Daten aufbereiten ---
    # Die API gibt die Zeit als String zurück (z.B. "2026-04-09T06:15"). Wir schneiden die letzten 5 Zeichen ab für die Uhrzeit.
    sunrise = data['daily']['sunrise'][0][-5:]
    sunset = data['daily']['sunset'][0][-5:]
    
    st.info(f"🌅 Sonnenaufgang: {sunrise} Uhr | 🌇 Sonnenuntergang: {sunset} Uhr")

    # --- Stündliche Daten aufbereiten ---
    hourly = data['hourly']
    
    # Pandas DataFrame erstellen für einfache Streamlit-Charts
    df = pd.DataFrame({
        "Zeit": pd.to_datetime(hourly['time']),
        "Temperatur (°C)": hourly['temperature_2m'],
        "Regen (mm)": hourly['rain'],
        "Wolken (%)": hourly['cloud_cover'],
        "Wettercode": hourly['weather_code']
    }).set_index("Zeit")

    # --- Aktuelles Wetter (Wir nehmen einfach die Daten der aktuellen Stunde) ---
    current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
    
    try:
        current_data = df.loc[current_hour]
        icon = weather.get_weather_icon(current_data["Wettercode"])
        
        st.subheader("Aktuelle Werte")
        col1, col2, col3 = st.columns(3)
        col1.metric("Wetter", icon)
        col2.metric("Temperatur", f"{current_data['Temperatur (°C)']} °C")
        col3.metric("Regen", f"{current_data['Regen (mm)']} mm")
    except KeyError:
        st.write("Aktuelle Stunde nicht im Datensatz gefunden.")

    st.divider()

    # --- Diagramme für den Tagesverlauf ---
    st.write("### 🌡️ Temperaturverlauf")
    st.line_chart(df["Temperatur (°C)"])

    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.write("### 🌧️ Regenmenge (mm)")
        # Streamlit Bar Chart
        st.bar_chart(df["Regen (mm)"])
        
    with col_chart2:
        st.write("### ☁️ Wolkenbedeckung (%)")
        # Area chart sieht für Wolken schön aus
        st.area_chart(df["Wolken (%)"])

else:
    st.error("Es konnten keine Wetterdaten geladen werden. Bitte überprüfe deine Internetverbindung oder API-URL.")

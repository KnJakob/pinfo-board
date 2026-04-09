import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

from utils import weather
from utils import color

# Seitenkonfiguration
st.set_page_config(page_title="Pi Wetter-Dashboard", layout="wide")

st.title("Berlin Wetterbericht 🐻")

# Daten abrufen
data = weather.get_weather_data()

if data:
    # --- Tägliche Daten aufbereiten (Zeiten parsen) ---
    sunrise_str = data['daily']['sunrise'][0]
    sunset_str = data['daily']['sunset'][0]
    
    # In echte Datetime-Objekte umwandeln für das Diagramm
    sunrise = datetime.fromisoformat(sunrise_str)
    sunset = datetime.fromisoformat(sunset_str)
    
    st.info(f"🌅 Sonnenaufgang: {sunrise.strftime('%H:%M')} Uhr | 🌇 Sonnenuntergang: {sunset.strftime('%H:%M')} Uhr")

    # --- Stündliche Daten in DataFrame packen ---
    hourly = data['hourly']
    df = pd.DataFrame({
        "Zeit": pd.to_datetime(hourly['time']),
        "Temperatur (°C)": hourly['temperature_2m'],
        "Regen (mm)": hourly['rain'],
        "Wolken (%)": hourly['cloud_cover'],
        "Wettercode": hourly['weather_code']
    })
    max_temp = df["Temperatur (°C)"].max()

    # Die Icons direkt als neue Spalte in den Datensatz packen
    df["Icon"] = df["Wettercode"].apply(weather.get_weather_icon)

    # --- 1. Aktuelles Wetter Karte ---
    current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
    
    # Suchen der aktuellen Stunde im DataFrame
    current_data_df = df[df["Zeit"] == current_hour]
    
    if not current_data_df.empty:
        current_data = current_data_df.iloc[0]
        st.subheader("Aktuelle Werte")
        col1, col2, col3 = st.columns(3)
        col1.metric("Wetter", current_data["Icon"])
        col2.metric("Temperatur", f"{current_data['Temperatur (°C)']} °C")
        col3.metric("Regen", f"{current_data['Regen (mm)']} mm")
    else:
        st.write("Aktuelle Stunde nicht im Datensatz gefunden.")

    st.divider()

    # --- 2. Temperaturverlauf mit Icons und Tageszeit-Hintergrund ---
    st.write("### 🌡️ Temperaturverlauf")
    
    # Farbe aus utils laden
    line_color = color.get_color_of_today()
    
    # Definition der grau zu schattierenden Nacht-Zeiten (Tagesanfang bis Sonnenaufgang & Sonnenuntergang bis Tagesende)
    night_areas = pd.DataFrame({
        "start": [df["Zeit"].min(), sunset],
        "end": [sunrise, df["Zeit"].max()]
    })

    # Layer 1: Grauer Hintergrund für die Nacht
    rect = alt.Chart(night_areas).mark_rect(opacity=0.15, color='gray').encode(
        x='start:T',
        x2='end:T'
    )

    # Layer 2: Die Temperatur-Linie
    base = alt.Chart(df).encode(
        x=alt.X("Zeit:T", title="Uhrzeit", axis=alt.Axis(format="%H:%M", tickCount=12))
    )
    line = base.mark_line(color=line_color, strokeWidth=3).encode(
        y=alt.Y("Temperatur (°C):Q", scale=alt.Scale(zero=False)) # zero=False sorgt dafür, dass die Skala nicht bei 0 anfangen muss
    )

    # Layer 3: Die Icons über den Datenpunkten
    icons = base.mark_text(align='center', size=18).encode(
        y=alt.value(0),  # Platziert das Icon 0 Pixel vom oberen Rand des Diagramms entfernt
        text="Icon:N"
    )

    # Alle drei Layer übereinanderlegen und in Streamlit rendern
    combined_chart = rect + line + icons
    st.altair_chart(combined_chart, width='stretch')


    # --- 3. Ausklappbare Details für Regen und Wolken ---
    with st.expander("🌧️ Regen und ☁️ Wolken im Detail anzeigen", expanded=False):
        col_chart1, col_chart2 = st.columns(2)
        
        # Für die nativen Streamlit-Charts setzen wir den Index wieder auf Zeit
        df_charts = df.set_index("Zeit")
        
        with col_chart1:
            st.write("#### Regenmenge (mm)")
            st.bar_chart(df_charts["Regen (mm)"], color="#5c9ce6") # Optional: Blau für Regen
            
        with col_chart2:
            st.write("#### Wolkenbedeckung (%)")
            st.area_chart(df_charts["Wolken (%)"], color="#b3b3b3") # Optional: Grau für Wolken

else:
    st.error("Es konnten keine Wetterdaten geladen werden.")

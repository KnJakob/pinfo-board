import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import locale

from utils import weather
from utils import color


def setup_page():
    """Konfiguriert die Streamlit-Seite. Muss als erstes aufgerufen werden."""
    st.set_page_config(page_title="Pi Dashboard", layout="wide")

    # Versuche das Datum auf Deutsch zu stellen
    try:
        locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
    except:
        pass


@st.fragment(run_every="1s")
def render_header():
    """Rendert den Seitenkopf mit Datum und Uhrzeit."""
    heute = datetime.now()
    datum_str = heute.strftime("%A, %d. %B %Y")
    uhrzeit_str = heute.strftime("%H:%M:%S")

    st.title(f"📅 {datum_str} · 🕒 {uhrzeit_str} Uhr")
    st.divider()


def render_current_weather(current_data_df, max_temp):
    """Rendert die linke Kachel mit den aktuellen Wetterdaten."""
    st.subheader("Aktuelle Lage")
    if not current_data_df.empty:
        current_data = current_data_df.iloc[0]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Wetter", current_data["Icon"])
        c2.metric("Temp", f"{current_data['Temperatur (°C)']} °C")
        c3.metric("Regen", f"{current_data['Regen (mm)']} mm")
        c4.metric("Max", f"{max_temp} °C")
    else:
        st.write("Warte auf aktuelle Daten...")


def render_color_of_the_day(daily_color):
    """Rendert die rechte Kachel mit der Tagesfarbe."""
    try:
        r = int(daily_color[1:3], 16)
        g = int(daily_color[3:5], 16)
        b = int(daily_color[5:7], 16)
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        text_color = "#111111" if luminance > 0.6 else "#FFFFFF"
    except ValueError:
        text_color = "#FFFFFF"

    color_box_html = f"""
    <div style="
        background-color: {daily_color}; 
        height: 160px; 
        border-radius: 10px; 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        color: white; 
        font-size: 24px; 
        font-weight: bold; 
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);">
        Color of the day: {daily_color}
    </div>
    """
    st.markdown(color_box_html, unsafe_allow_html=True)


def render_weather_chart(df, daily_color):
    """Rendert das Altair-Diagramm fuer Temperatur, Regen und Tag/Nacht-Zyklus."""
    st.write(" ")  # Abstand
    st.subheader("📈 Temperatur & Niederschlag")

    # Hintergrund fuer Nachtstunden aus dem API-Flag
    night_areas = df[df["IstTag"] == 0][["Zeit"]].copy()
    night_areas["end"] = night_areas["Zeit"] + pd.Timedelta(hours=1)
    rect = (
        alt.Chart(night_areas)
        .mark_rect(opacity=0.15, color="gray")
        .encode(x="Zeit:T", x2="end:T")
    )

    # Basis-Chart
    base = alt.Chart(df).encode(
        x=alt.X("Zeit:T", axis=alt.Axis(format="%H:%M", title="Uhrzeit", tickCount=12))
    )

    # Regen (Flächendeckend)
    rain_chart = base.mark_area(opacity=0.3, color="#5c9ce6").encode(
        y=alt.Y("Regen (mm):Q", axis=alt.Axis(title="Regen (mm)", titleColor="#5c9ce6"))
    )

    # Temperatur (Linie)
    temp_line = base.mark_line(color=daily_color, strokeWidth=3).encode(
        y=alt.Y(
            "Temperatur (°C):Q",
            scale=alt.Scale(zero=False),
            axis=alt.Axis(title="Temperatur (°C)", titleColor=daily_color),
        )
    )

    now_marker = (
        temp_line.mark_point(color="#e53935", fill="#e53935", size=100, opacity=1)
        .encode(y=alt.Y("Temperatur (°C):Q"))
        .transform_filter(alt.datum.IstJetzt == 1)
    )
    # Icons über der Temperatur
    icons = base.mark_text(dy=-15, size=18, font="Noto Color Emoji").encode(
        y=alt.Y("Temperatur (°C):Q"), text="Icon:N"
    )

    # Layer zusammensetzen
    temp_with_night = alt.layer(rect, temp_line, icons, now_marker)
    final_chart = alt.layer(rain_chart, temp_with_night).resolve_scale(y="independent")

    st.altair_chart(final_chart, width="stretch")


@st.fragment(run_every="30s")
def render_dashboard():
    """Rendert den Datenbereich und aktualisiert ihn regelmaessig."""
    data = weather.get_weather_data()

    if data and "hourly" in data:
        # Daten aufbereiten
        hourly = data["hourly"]
        now = pd.Timestamp.now().floor("h")
        df = pd.DataFrame(
            {
                "Zeit": pd.to_datetime(hourly["time"]),
                "Temperatur (°C)": hourly["temperature_2m"],
                "Regen (mm)": hourly["rain"],
                "Wolken (%)": hourly["cloud_cover"],
                "Wettercode": hourly["weather_code"],
                "IstTag": hourly["is_day"],
                "IstJetzt": (pd.to_datetime(hourly["time"]).floor("h") == now).astype(
                    int
                ),
            }
        )

        now_ts = datetime.now()
        current_hour = now_ts.replace(minute=0, second=0, microsecond=0)
        window_start = current_hour - pd.Timedelta(hours=2)
        window_end = current_hour + pd.Timedelta(hours=22)
        window_df = df[(df["Zeit"] >= window_start) & (df["Zeit"] <= window_end)]
        if not window_df.empty:
            df = window_df.copy()

        df["Icon"] = [weather.get_weather_icon(code) for code in df["Wettercode"]]

        current_data_df = df[df["Zeit"] == current_hour]
        max_temp = df["Temperatur (°C)"].max()
        daily_color = color.get_color_of_today()

        # Layout der Kacheln (Top-Bereich)
        col_left, col_right = st.columns(2)

        with col_left:
            with st.container(border=True):
                render_current_weather(current_data_df, max_temp)

        with col_right:
            with st.container(border=False):
                render_color_of_the_day(daily_color)

        # Haupt-Chart rendern
        render_weather_chart(df, daily_color)

    else:
        st.error("Es konnten keine Wetterdaten geladen werden.")


def main():
    """Hauptfunktion, die den Ablauf des Dashboards steuert."""
    setup_page()
    render_header()
    render_dashboard()


if __name__ == "__main__":
    main()

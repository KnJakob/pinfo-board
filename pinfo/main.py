import streamlit as st
from utils import color_today

# Seite konfigurieren
st.set_page_config(page_title="Pi Color", page_icon="🎨")

def main():
    st.title("Farbe des Tages")
    
    # Farbe abrufen
    color = color_today.get_color_of_today()
    
    # CSS Injection: Ändert den Hintergrund der App passend zur Farbe
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        .color-card {{
            background: rgba(255, 255, 255, 0.8);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: #333;
        }}
        </style>
        <div class="color-card">
            <h1>{color}</h1>
            <p>Diese Daten kommen direkt vom Raspberry Pi 5</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()
    st.subheader("Raw API Output")
    st.code(f"Current Color: {color}")

if __name__ == "__main__":
    main()















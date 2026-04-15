import requests
from datetime import date

import streamlit as st


@st.cache_data(ttl=3600*3)
def fetch_color_from_api(target_date):
    url = "https://colors.zoodinkers.com/api"

    try:
        response = requests.get(url, params={"date": target_date}, timeout=10)
        response.raise_for_status()
        data = response.json()

        return data.get("hex") or "#FFFFFF"

    except Exception as e:
        print(f"Error when retrieving color {e}")
        return "#FFFFFF"


def get_color_of_today():
    today_str = date.today().strftime("%Y-%m-%d")
    return fetch_color_from_api(today_str)

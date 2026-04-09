import requests
from datetime import date

import streamlit as st


@st.cache_data(ttl=3600*3)
def fetch_color_from_api(target_date):
    url = f"http://colors.zoodinkers.com/api?date={target_date}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        return data.get("hex") or "#FFFFFF"

    except Exception as e:
        return f"Error: {e}"

def get_color_of_today():
    today_str = date.today().strftime("%Y-%m-%d")
    return fetch_color_from_api(today_str)


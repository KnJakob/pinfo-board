import requests
from datetime import date

def get_color_of_today():
    today = date.today().strftime("%Y-%m-%d")
    
    url = f"http://colors.zoodinkers.com/api?date={today}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        color = data.get("hex", "No color field found in response")
        return color

    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"
    except ValueError:
        return response.text.strip()


if __name__ == "__main__":
    today_color = get_color_of_today()
    print(f"Today's color is: {today_color}")

import sqlite3
import requests
import os
import datetime

def fetch_real_data():
    api_token = os.getenv("AIS_TOKEN")
    if not api_token:
        print("CRITICAL: No AIS_TOKEN found in environment variables!")
        return []

    # שימוש בפורמט ה-URL הישיר של AISStream
    url = f"https://api.aisstream.io/v1/vessels?apiKey={api_token}"
    
    # הגדרת אזור מצרי הורמוז
    payload = {
        "bounding_box": [[55.0, 26.0], [57.0, 27.5]]
    }

    try:
        print(f"Attempting to fetch data from AISStream...")
        response = requests.post(url, json=payload, timeout=15)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Received {len(data)} potential targets.")
            vessels = []
            for entry in data:
                vessels.append((
                    str(entry.get('mmsi')),
                    entry.get('name', 'Unknown'),
                    entry.get('type_str', 'Vessel'),
                    entry.get('flag', 'Unknown'),
                    entry.get('last_location', {}).get('lat'),
                    entry.get('last_location', {}).get('lon'),
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
            return vessels
        else:
            print(f"API Error Details: {response.text}")
            return []
    except Exception as e:
        print(f"Connection Error: {e}")
        return []

def save_to_db(vessels):
    conn = sqlite3.connect('hormuz_ships.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ship_logs
                 (mmsi TEXT, name TEXT, ship_type TEXT, country TEXT, 
                  lat REAL, lon REAL, timestamp DATETIME)''')
    
    if vessels:
        c.executemany("INSERT INTO ship_logs VALUES (?, ?, ?, ?, ?, ?, ?)", vessels)
        print(f"Successfully inserted {len(vessels)} rows.")
    else:
        print("No vessels to insert this time.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    ships = fetch_real_data()
    save_to_db(ships)

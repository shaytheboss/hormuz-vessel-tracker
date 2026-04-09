import sqlite3
import requests
import os
import datetime

def fetch_real_data():
    # משיכת הטוקן מההגדרות המאובטחות של GitHub
    api_token = os.getenv("AIS_TOKEN")
    if not api_token:
        print("Error: No API token found!")
        return []

    # הגדרת האזור הגיאוגרפי של מצרי הורמוז (Polygon)
    url = "https://api.aisstream.io/v1/vessels"
    
    # אנחנו נשתמש ב-Bounding Box פשוט למצרים
    # Lat: 26.0 to 27.5, Lon: 55.0 to 57.0
    params = {
        "apiKey": api_token,
        "mmsi": "", # נשאיר ריק כדי לקבל את כל הספינות באזור
        "boxtopleft": "27.5,55.0",
        "boxbottomright": "26.0,57.0"
    }

    try:
        # הערה: AISStream משתמש לעיתים ב-WebSockets, אבל יש להם גם REST API פשוט
        # כאן אנחנו מדמים את המבנה של התגובה שלהם
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            data = response.json()
            # עיבוד הנתונים (תלוי במבנה ה-JSON המדויק שלהם)
            vessels = []
            for item in data.get('entries', []):
                vessels.append((
                    str(item.get('mmsi')),
                    item.get('name', 'Unknown'),
                    item.get('type_str', 'Other'),
                    item.get('flag', 'Unknown'),
                    item.get('lat'),
                    item.get('lon'),
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
            return vessels
        else:
            print(f"API Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching data: {e}")
        return []

def update_db(vessels):
    conn = sqlite3.connect('hormuz_ships.db')
    c = conn.cursor()
    
    # וידוא שהטבלה קיימת
    c.execute('''CREATE TABLE IF NOT EXISTS ship_logs
                 (mmsi TEXT, name TEXT, ship_type TEXT, country TEXT, 
                  lat REAL, lon REAL, timestamp DATETIME)''')

    # הכנסת הנתונים החדשים
    if vessels:
        c.executemany("INSERT INTO ship_logs VALUES (?, ?, ?, ?, ?, ?, ?)", vessels)
        print(f"Added {len(vessels)} new ship records.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    ships = fetch_real_data()
    update_db(ships)
    

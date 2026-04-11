import requests
import sqlite3
import os
import datetime

DB_PATH = "hormuz_ships.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    # איפוס הטבלה כדי להבטיח מבנה תקין
    conn.execute('DROP TABLE IF EXISTS ship_logs')
    conn.execute('''CREATE TABLE ship_logs
        (mmsi TEXT, name TEXT, ship_type TEXT, country TEXT,
         lat REAL, lon REAL, speed REAL, destination TEXT, 
         region TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def fetch_region(api_key, bounding_box, region_name):
    # שימוש ב-API של חיפוש (HTTP) במקום סטרימינג
    url = "https://api.aisstream.io/v1/vessels"
    params = {
        "apiKey": api_key,
        "latMin": bounding_box[0][0],
        "latMax": bounding_box[1][0],
        "lonMin": bounding_box[0][1],
        "lonMax": bounding_box[1][1]
    }
    
    try:
        print(f"📡 Fetching {region_name}...")
        response = requests.get(url, params=params, timeout=20)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"⚠️ {region_name} failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching {region_name}: {e}")
        return []

def run():
    init_db()
    token = os.environ.get("AIS_TOKEN", "")
    
    # הגדרת האזורים (הורמוז וסואץ)
    regions = {
        "Hormuz": [[26.0, 55.8], [27.4, 56.6]],
        "Suez": [[29.5, 32.2], [31.5, 32.6]]
    }
    
    conn = sqlite3.connect(DB_PATH)
    curr_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    total_captured = 0
    for name, bbox in regions.items():
        vessels = fetch_region(token, bbox, name)
        for ship in vessels:
            meta = ship.get("MetaData", {})
            pos = ship.get("Message", {}).get("PositionReport", {})
            
            conn.execute(
                "INSERT INTO ship_logs VALUES (?,?,?,?,?,?,?,?,?,?)",
                (str(meta.get("MMSI")),
                 str(meta.get("ShipName", "Unknown")).strip(),
                 str(meta.get("ShipType", "")),
                 meta.get("Flag", ""),
                 pos.get("Latitude"),
                 pos.get("Longitude"),
                 pos.get("Sog", 0),
                 "Unknown", # ב-HTTP פשוט לרוב אין StaticData
                 name,
                 curr_time)
            )
            total_captured += 1
            
    conn.commit()
    conn.close()
    print(f"✅ Success! Captured {total_captured} vessels across all regions.")

if __name__ == "__main__":
    run()

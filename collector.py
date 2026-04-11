import websocket, json, sqlite3, os, datetime, threading, time

DB_PATH = "hormuz_ships.db"
DURATION = int(os.getenv("COLLECTION_SECONDS", "300"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    # איפוס הטבלה כדי לוודא התאמה למבנה החדש (10 עמודות)
    conn.execute('DROP TABLE IF EXISTS ship_logs') 
    conn.execute('''CREATE TABLE ship_logs
        (mmsi TEXT, name TEXT, ship_type TEXT, country TEXT,
         lat REAL, lon REAL, speed REAL, destination TEXT, 
         region TEXT, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def on_message(ws, message):
    try:
        msg = json.loads(message)
        meta = msg.get("MetaData", {})
        payload = msg.get("Message", {})
        
        # הוצאת נתונים מהודעות מיקום וסטטיסטיקה
        pos = payload.get("PositionReport", {})
        static = payload.get("ShipStaticData", {})
        
        lat = pos.get("Latitude") or static.get("Latitude")
        lon = pos.get("Longitude") or static.get("Longitude")
        
        if not (meta and lat and lon): return

        conn = sqlite3.connect(DB_PATH)
        # זיהוי אזור
        region = "Hormuz" if lon > 45 else "Suez"
        
        conn.execute(
            "INSERT INTO ship_logs VALUES (?,?,?,?,?,?,?,?,?,?)",
            (str(meta.get("MMSI")),
             str(meta.get("ShipName", "Unknown")).strip(),
             str(meta.get("ShipType", "")),
             meta.get("Flag", ""),
             lat, lon, pos.get("Sog", 0), 
             static.get("Destination", "Unknown"), 
             region, datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()
        print(f"✓ {region}: {meta.get('ShipName', 'Unknown')}")
    except: pass

def on_open(ws):
    token = os.environ.get("AIS_TOKEN", "")
    # הודעת הרישום שעבדה לקולגה (v0 style)
    ws.send(json.dumps({
        "APIKey": token,
        "BoundingBoxes": [
            [[26.0, 55.8], [27.4, 56.6]], # הורמוז מצומצם
            [[29.5, 32.2], [31.5, 32.6]]  # סואץ
        ],
        "FilterMessageTypes": ["PositionReport", "ShipStaticData"]
    }))
    print("📡 Monitoring active on v0...")

def run():
    init_db()
    # חזרה לכתובת שעבדה ב-100%
    ws = websocket.WebSocketApp(
        "wss://stream.aisstream.io/v0/stream",
        on_open=on_open, on_message=on_message,
        on_error=lambda ws, e: print(f"Error: {e}"),
        on_close=lambda ws, c, m: print("Connection closed")
    )
    t = threading.Thread(target=ws.run_forever, daemon=True)
    t.start()
    time.sleep(DURATION)
    ws.close()

if __name__ == "__main__":
    run()

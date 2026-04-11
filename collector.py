import websocket, json, sqlite3, os, datetime, threading, time

DB_PATH = "hormuz_ships.db"
DURATION = int(os.getenv("COLLECTION_SECONDS", "300"))

def init_db():
    conn = sqlite3.connect(DB_PATH)
    # טבלה מורחבת הכוללת מהירות, יעד ואזור
    conn.execute('''CREATE TABLE IF NOT EXISTS ship_logs
        (mmsi TEXT, name TEXT, ship_type TEXT, country TEXT,
         lat REAL, lon REAL, speed REAL, destination TEXT, 
         region TEXT, timestamp DATETIME)''')
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON ship_logs(timestamp)")
    conn.commit()
    conn.close()

def on_message(ws, message):
    try:
        msg = json.loads(message)
        meta = msg.get("MetaData", {})
        msg_type = msg.get("MessageType")
        payload = msg.get("Message", {})
        
        if not meta: return

        conn = sqlite3.connect(DB_PATH)
        curr_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        # זיהוי אזור לפי קווי אורך
        lon = 0
        lat = 0
        speed = 0
        dest = "Unknown"
        
        if msg_type == "PositionReport":
            pos = payload.get("PositionReport", {})
            lat = pos.get("Latitude")
            lon = pos.get("Longitude")
            speed = pos.get("Sog", 0)
        elif msg_type == "ShipStaticData":
            static = payload.get("ShipStaticData", {})
            dest = static.get("Destination", "Unknown")
            # בסטטי אין מיקום, אז ננסה לעדכן רשומה קיימת או לדלג
        
        if lat and lon:
            region = "Hormuz" if lon > 45 else "Suez"
            
            conn.execute(
                "INSERT INTO ship_logs VALUES (?,?,?,?,?,?,?,?,?,?)",
                (str(meta.get("MMSI")),
                 str(meta.get("ShipName", "Unknown")).strip(),
                 str(meta.get("ShipType", "")),
                 meta.get("Flag", ""),
                 lat, lon, speed, dest, region, curr_time)
            )
            conn.commit()
            print(f"✓ {region}: {meta.get('ShipName', 'Unknown')}")
            
        conn.close()
    except Exception as e:
        pass 

def on_open(ws):
    token = os.environ.get("AIS_TOKEN", "")
    ws.send(json.dumps({
        "APIKey": token,
        "BoundingBoxes": [
            [[26.0, 55.8], [27.4, 56.6]], # מיצרי הורמוז (מצומצם)
            [[29.5, 32.2], [31.5, 32.6]]  # תעלת סואץ
        ],
        "FilterMessageTypes": ["PositionReport", "ShipStaticData"]
    }))
    print("📡 Monitoring Hormuz & Suez Channels...")

def run():
    init_db()
    ws = websocket.WebSocketApp(
        "wss://stream.aisstream.io/v0/stream",
        on_open=on_open,
        on_message=on_message,
        on_error=lambda ws, e: print(f"WS Error: {e}"),
        on_close=lambda ws, c, m: print("Connection closed")
    )

    t = threading.Thread(target=ws.run_forever, daemon=True)
    t.start()
    time.sleep(DURATION)
    ws.close()
    print("✅ Collection complete.")

if __name__ == "__main__":
    run()

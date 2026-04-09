import websocket
import json
import sqlite3
import datetime
import os

def save_to_db(vessels):
    if not vessels:
        return
    conn = sqlite3.connect('hormuz_ships.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ship_logs
                 (mmsi TEXT, name TEXT, ship_type TEXT, country TEXT, 
                  lat REAL, lon REAL, timestamp DATETIME)''')
    c.executemany("INSERT INTO ship_logs VALUES (?, ?, ?, ?, ?, ?, ?)", vessels)
    conn.commit()
    conn.close()

def on_message(ws, message):
    msg = json.loads(message)
    # שליפת נתוני הספינה מההודעה של AISStream
    metadata = msg.get("MetaData", {})
    message_content = msg.get("Message", {}).get("PositionReport", {})
    
    if metadata and message_content:
        ship_data = (
            str(metadata.get("MMSI")),
            metadata.get("ShipName", "Unknown").strip(),
            metadata.get("ShipType"),
            metadata.get("Flag"),
            message_content.get("Latitude"),
            message_content.get("Longitude"),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        save_to_db([ship_data])
        print(f"✅ Captured ship: {ship_data[1]}")

def run_collector():
    api_token = os.getenv("AIS_TOKEN")
    if not api_token:
        print("❌ Missing AIS_TOKEN!")
        return

    # הודעת ההתחברות ל-AISStream (Subscription)
    subscribe_msg = {
        "APIKey": api_token,
        "BoundingBoxes": [[[26.0, 55.0], [27.5, 57.0]]] # קואורדינטות מצרי הורמוז
    }
    
    # חיבור לכתובת ה-Stream האמיתית
    ws = websocket.WebSocketApp(
        "wss://stream.aisstream.io/v1/stream",
        on_open=lambda ws: ws.send(json.dumps(subscribe_msg)),
        on_message=on_message,
        on_error=lambda ws, err: print(f"Error: {err}")
    )
    
    # הזרמה למשך 20 שניות בלבד כדי לא לחרוג מזמן הריצה של ה-Action
    print("📡 Listening to Hormuz Strait for 20 seconds...")
    ws.run_forever(timeout=20)

if __name__ == "__main__":
    run_collector()

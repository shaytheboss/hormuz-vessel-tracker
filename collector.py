import websocket
import json
import sqlite3
import datetime
import os

def save_to_db(vessels):
    conn = sqlite3.connect('hormuz_ships.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ship_logs
                 (mmsi TEXT, name TEXT, ship_type TEXT, country TEXT, 
                  lat REAL, lon REAL, timestamp DATETIME)''')
    if vessels:
        c.executemany("INSERT INTO ship_logs VALUES (?, ?, ?, ?, ?, ?, ?)", vessels)
        conn.commit()
    conn.close()

def on_message(ws, message):
    msg = json.loads(message)
    vessel = msg.get("MetaData", {})
    pos = msg.get("Message", {}).get("PositionReport", {})
    
    if vessel and pos:
        ship_data = (
            str(vessel.get("MMSI")),
            vessel.get("ShipName", "Unknown").strip(),
            vessel.get("ShipType"),
            vessel.get("Flag"),
            pos.get("Latitude"),
            pos.get("Longitude"),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        # שמירה מיידית של הספינה שמצאנו
        save_to_db([ship_data])
        print(f"Captured: {ship_data[1]}")
        # אנחנו נסגור את החיבור אחרי שקיבלנו כמה ספינות כדי לא להיתקע לנצח
        ws.close()

def run_collector():
    api_token = os.getenv("AIS_TOKEN")
    subscribe_msg = {
        "APIKey": api_token,
        "BoundingBoxes": [[[26.0, 55.0], [27.5, 57.0]]] # מצרי הורמוז
    }
    
    ws = websocket.WebSocketApp(
        "wss://stream.aisstream.io/v1/stream",
        on_message=on_message,
        on_open=lambda ws: ws.send(json.dumps(subscribe_msg))
    )
    # נריץ למשך 30 שניות מקסימום כדי לא לחרוג מהזמן של ה-Action
    ws.run_forever(timeout=30)

if __name__ == "__main__":
    run_collector()

import websocket
import json
import sqlite3
import os
import datetime

def on_message(ws, message):
    msg = json.loads(message)
    # שליפת נתונים בסיסיים
    meta = msg.get("MetaData", {})
    pos = msg.get("Message", {}).get("PositionReport", {})
    
    if meta and pos:
        conn = sqlite3.connect('hormuz_ships.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS ship_logs
                     (mmsi TEXT, name TEXT, ship_type TEXT, country TEXT, 
                      lat REAL, lon REAL, timestamp DATETIME)''')
        
        data = (str(meta.get("MMSI")), meta.get("ShipName"), meta.get("ShipType"),
                meta.get("Flag"), pos.get("Latitude"), pos.get("Longitude"),
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        c.execute("INSERT INTO ship_logs VALUES (?,?,?,?,?,?,?)", data)
        conn.commit()
        conn.close()
        print(f"Captured: {meta.get('ShipName')}")
        ws.close() # סוגר אחרי ספינה אחת לבדיקה

def run():
    token = os.getenv("AIS_TOKEN")
    auth_msg = {"APIKey": token, "BoundingBoxes": [[[26.0, 55.0], [27.5, 57.0]]]}
    
    ws = websocket.WebSocketApp(
        "wss://stream.aisstream.io/v1/stream",
        on_open=lambda ws: ws.send(json.dumps(auth_msg)),
        on_message=on_message
    )
    ws.run_forever(timeout=20)

if __name__ == "__main__":
    run()

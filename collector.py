import websocket
import json
import sqlite3
import os
import datetime
import threading
import time

def create_table_if_not_exists():
    conn = sqlite3.connect('hormuz_ships.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ship_logs
                 (mmsi TEXT, name TEXT, ship_type TEXT, country TEXT, 
                  lat REAL, lon REAL, timestamp DATETIME)''')
    conn.commit()
    conn.close()

def on_message(ws, message):
    try:
        msg = json.loads(message)
        meta = msg.get("MetaData", {})
        pos = msg.get("Message", {}).get("PositionReport", {})
        if meta and pos:
            conn = sqlite3.connect('hormuz_ships.db')
            c = conn.cursor()
            data = (str(meta.get("MMSI")), str(meta.get("ShipName", "Unknown")).strip(), 
                    meta.get("ShipType"), meta.get("Flag"), 
                    pos.get("Latitude"), pos.get("Longitude"),
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            c.execute("INSERT INTO ship_logs VALUES (?,?,?,?,?,?,?)", data)
            conn.commit()
            conn.close()
            print(f"Captured: {meta.get('ShipName')}")
    except Exception as e:
        print(f"Msg Error: {e}")

def on_open(ws):
    print("Connection established. Sending subscription bounding box...")
    # כאן אנחנו שולחים רק את הגבולות, כי ה-Key כבר ב-URL
    auth_msg = {
        "APIKey": os.getenv("AIS_TOKEN"), 
        "BoundingBoxes": [[[26.0, 55.0], [27.5, 57.0]]]
    }
    ws.send(json.dumps(auth_msg))

def run():
    create_table_if_not_exists()
    token = os.getenv("AIS_TOKEN")
    
    # שינוי קריטי: הכנסת ה-Token ישירות לכתובת ה-URL
    ws_url = f"wss://stream.aisstream.io/v1/stream"
    
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=lambda ws, err: print(f"Socket Error: {err}"),
        on_close=lambda ws, status, msg: print(f"Closed: {status} - {msg}")
    )

    wst = threading.Thread(target=ws.run_forever)
    wst.daemon = True
    wst.start()
    
    print("📡 Monitoring Hormuz Strait for 5 minutes...")
    time.sleep(300)
    ws.close()
    print("✅ Cycle complete.")

if __name__ == "__main__":
    run()

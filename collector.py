import sqlite3
import datetime

def init_and_update():
    # יצירת חיבור לקובץ ה-Database (ייווצר אוטומטית אם לא קיים)
    conn = sqlite3.connect('hormuz_ships.db')
    c = conn.cursor()
    
    # יצירת הטבלה
    c.execute('''CREATE TABLE IF NOT EXISTS ship_logs
                 (mmsi TEXT, name TEXT, ship_type TEXT, country TEXT, 
                  lat REAL, lon REAL, timestamp DATETIME)''')

    # נתונים זמניים (סימולציה) עד שנחבר API אמיתי
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sample_data = [
        ('123456789', 'Ever Given', 'Cargo', 'Panama', 26.5, 56.1, now),
        ('987654321', 'Oil Star', 'Tanker', 'Liberia', 26.3, 56.4, now),
        ('555666777', 'Zhen Hua', 'Cargo', 'China', 26.8, 56.7, now)
    ]
    
    # הכנסת הנתונים
    c.executemany("INSERT INTO ship_logs VALUES (?, ?, ?, ?, ?, ?, ?)", sample_data)
    
    conn.commit()
    conn.close()
    print(f"Update successful at {now}")

if __name__ == "__main__":
    init_and_update()
  

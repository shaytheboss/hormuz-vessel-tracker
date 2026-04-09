import streamlit as st
import pandas as pd
import sqlite3
import urllib.request
import os

# הגדרות עמוד
st.set_page_config(page_title="Hormuz Vessel Tracker", layout="wide")

# עיצוב בסיסי ב-CSS
st.markdown("""
    <style>
    .stMetric {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚢 ניטור מצרי הורמוז - מאגר נתונים מצטבר")
st.write("המערכת מושכת נתונים ממאגר המידע המרוחק בענף ה-Data")

def load_data():
    # כתובת הקובץ בענף הנתונים (data branch)
    db_url = "https://github.com/shaytheboss/hormuz-vessel-tracker/raw/data/hormuz_ships.db"
    local_db = "local_hormuz_ships.db"
    
    try:
        # הורדת הקובץ מגיטהאב לסביבת העבודה של Streamlit
        urllib.request.urlretrieve(db_url, local_db)
        
        # התחברות וקריאה
        conn = sqlite3.connect(local_db)
        df = pd.read_sql("SELECT * FROM ship_logs ORDER BY timestamp DESC", conn)
        conn.close()
        
        # ניקוי: מחיקת הקובץ המקומי אחרי הטעינה (אופציונלי)
        if os.path.exists(local_db):
            os.remove(local_db)
            
        return df
    except Exception as e:
        # אם הקובץ עדיין לא קיים (לפני ההרצה הראשונה של ה-Action)
        return pd.DataFrame()

# טעינת הנתונים
df = load_data()

if not df.empty:
    # הצגת מדדים (KPIs)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("סה\"כ אירועים שנרשמו", len(df))
    with m2:
        tankers = len(df[df['ship_type'].str.contains('Tanker', case=False, na=False)])
        st.metric("מכליות נפט", tankers)
    with m3:
        last_update = df['timestamp'].iloc[0]
        st.metric("עדכון אחרון", str(last_update).split(".")[0])

    st.divider()

    # תצוגת מפה
    st.subheader("📍 מפת תנועה מצטברת")
    # סינון שורות בלי קואורדינטות
    map_df = df.dropna(subset=['lat', 'lon'])
    if not map_df.empty:
        st.map(map_df[['lat', 'lon']])

    st.divider()

    # טבלת נתונים
    st.subheader("📋 יומן מעברים היסטורי")
    st.dataframe(
        df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "timestamp": "זמן דיווח",
            "name": "שם הספינה",
            "ship_type": "סוג",
            "country": "מדינה/דגל",
            "lat": "קו רוחב",
            "lon": "קו אורך"
        }
    )
else:
    st.warning("⚠️ לא נמצאו נתונים בענף ה-Data. וודא שה-Workflow רץ לפחות פעם אחת בהצלחה.")
    st.info("ברגע שה-Action יסתיים ב-V ירוק, הנתונים יופיעו כאן אוטומטית.")
    

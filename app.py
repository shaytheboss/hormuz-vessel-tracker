import streamlit as st
import pandas as pd
import sqlite3
import urllib.request
import os

st.set_page_config(page_title="Global Maritime Watch", layout="wide")

st.title("🛳️ ניטור עורקי שיט אסטרטגיים")

def load_data():
    # שים לב לנתיב ה-Raw של הקובץ שלך
    db_url = "https://raw.githubusercontent.com/shaytheboss/hormuz-vessel-tracker/data/hormuz_ships.db"
    local_db = "local_ships.db"
    if os.path.exists(local_db): os.remove(local_db)
    
    try:
        urllib.request.urlretrieve(db_url, local_db)
        conn = sqlite3.connect(local_db)
        query = "SELECT * FROM ship_logs ORDER BY timestamp DESC"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # תפריט צד לבחירת אזור
    regions = ["All"] + list(df['region'].unique())
    selected_region = st.sidebar.selectbox("בחר אזור לניטור:", regions)
    
    if selected_region != "All":
        df = df[df['region'] == selected_region]

    st.metric("מספר ספינות שזוהו", len(df))

    # הצגת מפה
    st.subheader(f"מפת תנועה - {selected_region}")
    map_df = df.rename(columns={'lat': 'latitude', 'lon': 'longitude'})
    st.map(map_df)

    # טבלת נתונים מורחבת
    st.subheader("נתונים גולמיים")
    st.dataframe(df[['timestamp', 'name', 'country', 'speed', 'destination', 'region']])
else:
    st.warning("ממתין לנתונים מה-Action... וודא שהריצה הראשונה הסתיימה.")

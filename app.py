import streamlit as st
import pandas as pd
import sqlite3

# הגדרות עמוד
st.set_page_config(page_title="Hormuz Watcher", layout="wide")

# תיקון השגיאה: שימוש ב-unsafe_allow_html=True
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

st.title("🚢 Hormuz Strait Traffic Control")
st.write("ניטור תנועה ימית בזמן אמת - מצרי הורמוז")

def load_data():
    try:
        conn = sqlite3.connect('hormuz_ships.db')
        df = pd.read_sql("SELECT * FROM ship_logs ORDER BY timestamp DESC", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # כרטיסי מידע
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("סה\"כ ספינות", len(df))
    m2.metric("מכליות נפט", len(df[df['ship_type'] == 'Tanker']))
    m3.metric("מדינות", df['country'].nunique())
    m4.metric("עדכון אחרון", str(df['timestamp'].iloc[0]).split(".")[0])

    st.divider()

    # מפה בסיסית של Streamlit (בלי ספריות חיצוניות בינתיים כדי למנוע שגיאות)
    st.subheader("📍 מיקומי ספינות אחרונים")
    # Streamlit צריך עמודות בשם lat ו-lon בשביל המפה המובנית
    map_df = df[['lat', 'lon']].dropna()
    st.map(map_df)

    st.subheader("📋 רשימת מעברים מפורטת")
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("ממתין לנתונים ראשוניים מה-Workflow...")
    

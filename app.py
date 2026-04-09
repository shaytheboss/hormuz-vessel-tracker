import streamlit as st
import pandas as pd
import sqlite3

# הגדרות עמוד למראה מקצועי
st.set_page_config(page_title="Hormuz Watcher", layout="wide", initial_sidebar_state="collapsed")

# הוספת CSS מותאם אישית למראה כהה ונקי
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_stdio=True)

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
    # שורת מדדים עליונה
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("סה\"כ ספינות", len(df))
    m2.metric("מכליות נפט", len(df[df['ship_type'] == 'Tanker']))
    m3.metric("מדינות מיוצגות", df['country'].nunique())
    m4.metric("עדכון אחרון", str(df['timestamp'].iloc[0]).split(".")[0])

    st.markdown("---")

    # חלוקה לשני טורים: מפה (בעתיד) וטבלה
    col_table, col_chart = st.columns([2, 1])

    with col_table:
        st.subheader("📋 רשימת מעברים מפורטת")
        # עיצוב הטבלה
        st.dataframe(
            df, 
            column_config={
                "mmsi": "ID",
                "name": "שם הספינה",
                "ship_type": "סוג",
                "country": "דגל",
                "lat": "Lat",
                "lon": "Lon",
                "timestamp": "זמן"
            },
            hide_index=True, 
            use_container_width=True
        )

    with col_chart:
        st.subheader("📊 פילוח לפי סוג")
        type_counts = df['ship_type'].value_counts()
        st.bar_chart(type_counts)

else:
    st.info("ממתין לנתונים ראשוניים...")
    

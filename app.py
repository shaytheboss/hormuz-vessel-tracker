import streamlit as st
import pandas as pd
import sqlite3

# הגדרות עמוד רחב
st.set_page_config(page_title="Hormuz Vessel Tracker", layout="wide")

st.title("🚢 ניטור ספינות - מצרי הורמוז")

def load_data():
    try:
        # התחברות לקובץ שה-Action יצר
        conn = sqlite3.connect('hormuz_ships.db')
        df = pd.read_sql("SELECT * FROM ship_logs ORDER BY timestamp DESC", conn)
        conn.close()
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    # כרטיסי מידע עליונים
    c1, c2, c3 = st.columns(3)
    c1.metric("ספינות במערכת", len(df))
    c2.metric("מכליות נפט", len(df[df['ship_type'] == 'Tanker']))
    c3.metric("עדכון אחרון", str(df['timestamp'].iloc[0]).split(".")[0])

    st.divider()

    # הצגת הטבלה
    st.subheader("📋 רשימת מעברים")
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.warning("בסיס הנתונים עדיין ריק. וודא שה-Workflow רץ בהצלחה.")
  

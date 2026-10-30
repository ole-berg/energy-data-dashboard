import streamlit as st
import psycopg2
import pandas as pd
from zoneinfo import ZoneInfo


def load_data():
    conn = psycopg2.connect(st.secrets["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute("SELECT timestamp, price FROM day_ahead WHERE timestamp > now() - interval '1 week'")
    results = cur.fetchall()
    data = pd.DataFrame(results, columns=["timestamp", "price"])
    data["price"] = data["price"].astype(float)
    data["timestamp"] = pd.to_datetime(data["timestamp"]).dt.tz_localize(tz="utc").tz_convert(tz=ZoneInfo("Europe/Berlin"))
    return data

data = load_data()
st.title("🎈 My new app test")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
st.dataframe(data)
st.line_chart(data, x="timestamp", y="price")
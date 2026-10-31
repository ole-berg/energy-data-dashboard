import streamlit as st
import psycopg2
import pandas as pd
from zoneinfo import ZoneInfo
from datetime import datetime


def load_data():
    conn = psycopg2.connect(st.secrets["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(
        "SELECT timestamp, price FROM day_ahead WHERE timestamp > now() - interval '1 week'"
    )
    results = cur.fetchall()
    data = pd.DataFrame(results, columns=["timestamp", "price"])
    data["price"] = data["price"].astype(float)
    data["timestamp"] = pd.to_datetime(data["timestamp"]).dt.tz_convert(
        tz=ZoneInfo("Europe/Berlin")
    )
    return data


data = load_data()
current_time = datetime.now(tz=ZoneInfo("Europe/Berlin"))
current_price = (
    data[data["timestamp"] < current_time]
    .sort_values(by="timestamp", ascending=False)
    .iloc[0]["price"]
)
next_price = (
    data[data["timestamp"] > current_time]
    .sort_values(by="timestamp", ascending=True)
    .iloc[0]["price"]
)
st.metric("Price", value=current_price, delta=next_price-current_price, delta_color="inverse")
st.title("🎈 My new app test")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
st.dataframe(data)
st.line_chart(data, x="timestamp", y="price")

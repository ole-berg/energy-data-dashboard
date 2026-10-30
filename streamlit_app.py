import streamlit as st
import psycopg2
import pandas as pd


def load_data():
    conn = psycopg2.connect(st.secrets("DATABASE_URL"))
    cur = conn.cursor()
    cur.execute("SELECT timestamp, price FROM day_ahead WHERE timestamp > now() - interval '1 week'")
    results = cur.fetchall()
    data = pd.DataFrame(results, columns=["timestamp", "price"])
    return data

data = load_data()
st.title("🎈 My new app test")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
st.dataframe(data)
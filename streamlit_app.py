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
    data["price"] = data["price"].apply(lambda x: round(x/10, 2))
    return data

def get_cheapest_price(duration: int = 4):
    next_prices = (
        data[data["timestamp"] > current_time]
        .sort_values(by="timestamp", ascending=True)
        .head(duration)
    )
    len_prices = len(next_prices)
    current_min = [datetime.now(tz=ZoneInfo("Europe/Berlin")), 1000]
    pure_next_prices = next_prices["price"].tolist()
    for idx, row in next_prices.iterrows():
        if idx <= len_prices - duration:
            print((row["timestamp"], row["price"]))
            cum_price = sum(pure_next_prices[idx:idx+duration])*0.25
            print(cum_price)
            if cum_price < current_min[1]:
                current_min = [row["timestamp"], cum_price]
        else:
            return current_min
    return current_min

data = load_data()
current_time = datetime.now(tz=ZoneInfo("Europe/Berlin"))
current_prices = data[data["timestamp"] < current_time].sort_values(
    by="timestamp", ascending=True
)
current_price = current_prices.iloc[-1]["price"]
previous_price = current_prices.iloc[-2]["price"]
next_price = (
    data[data["timestamp"] > current_time]
    .sort_values(by="timestamp", ascending=True)
    .iloc[0]["price"]
)
st.metric(
    "Price",
    value=str(current_price) + " ct",
    delta=round(current_price - previous_price, 2),
    delta_color="inverse",
    delta_description="vs. 15 min ago",
    chart_data=current_prices["price"][-5:],
    chart_type="area",
)
cheapest_price = get_cheapest_price(4)
st.metric(
    "Cheapest price for 1 hour",
    value=str(cheapest_price[1]) + " ct at " + str(cheapest_price[0]),
)
st.title("🎈 My new app test")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)
st.dataframe(data)
st.line_chart(data, x="timestamp", y="price")

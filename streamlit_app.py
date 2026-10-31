import streamlit as st
import psycopg2
import pandas as pd
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta


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
    ).reset_index(drop=True)
    len_prices = len(next_prices)
    current_min = [datetime.now(tz=ZoneInfo("Europe/Berlin")), 1000]
    pure_next_prices = next_prices["price"].tolist()
    for idx, row in next_prices.iterrows():
        if idx <= len_prices - duration:
            cum_price = sum(pure_next_prices[idx:idx+duration])*0.25
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
    "Current Price",
    value=str(current_price) + " ct",
    delta=round(current_price - previous_price, 2),
    delta_color="inverse",
    delta_description="vs. 15 min ago",
    chart_data=current_prices["price"][-5:],
    chart_type="area",
)
duration = st.slider("Duration in quarters", min_value=1, max_value=12, value=4)
cheapest_price = get_cheapest_price(duration)
time_to_wait = int((cheapest_price[0] - current_time).total_seconds() / 60)
st.metric(
    f"Cheapest price for {duration} quarters",
    value=str(round(cheapest_price[1], 2)) + " ct/kW at " + str(cheapest_price[0].strftime("%H:%M")),
)
if time_to_wait < 15:
    st.markdown(":loudspeaker: :shimmer[CHEAPEST PRICE NOW]")
else:
    st.markdown(f":alarm_clock: Next cheapest price in {str(timedelta(minutes=time_to_wait))[:-3]} hours.")
st.dataframe(data)
st.subheader("Price on " + str(current_time.strftime("%d.%m.%Y")))
st.line_chart(data, x="timestamp", y="price", x_label="Time", y_label="Price")

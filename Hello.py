""" APP """

import json
import base64
import streamlit as st

# from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests

# import time


# ---------------------------------#
# New feature (make sure to upgrade your streamlit library)
# pip install --upgrade streamlit

# ---------------------------------#
# Page layout
## Page expands to full width
st.set_page_config(layout="wide")
# ---------------------------------#
# Title

# image = Image.open("logo.jpg")

# st.image(image, width=500)


st.sidebar.header("KRİPTO FİYAT LİSTESİ")
st.title("Crypto Price App")
st.markdown(
    """
Bu uygulama **CoinMarketCap**'ten en iyi 100 kripto para birimi için kripto para birimi fiyatlarını alır!

"""
)
# ---------------------------------#
# About
expander_bar = st.expander("About")
expander_bar.markdown(
    """
* **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json, time
* **Data source:** [CoinMarketCap](http://coinmarketcap.com).
"""
)


# ---------------------------------#
# Page layout (continued)
## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.columns((2, 1))

# ---------------------------------#
# Sidebar + Main panel
col1.header("Ayarlar")

## Sidebar - Currency price unit
currency_price_unit = col1.selectbox(" Fiyat için para birimini seçin", ("USD", "", ""))


# Web scraping of CoinMarketCap data
# @st.cache_data
def load_data():
    """Fetch data from CoinMarketCap"""
    try:
        cmc = requests.get("https://coinmarketcap.com", timeout=10)
        soup = BeautifulSoup(cmc.content, "html.parser")
        data = soup.find("script", id="__NEXT_DATA__", type="application/json")
        # print(data)
        coin_data = json.loads(data.contents[0])
        coin_data1 = json.loads(coin_data["props"]["initialState"])
        listings = coin_data1["cryptocurrency"]["listingLatest"]["data"]
        st.json(listings)
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    name_indis = listings[0]["keysArr"].index("name")
    symbol_indis = listings[0]["keysArr"].index("symbol")
    price_indis = listings[0]["keysArr"].index("quote.USD.price")
    change_1h_indis = listings[0]["keysArr"].index("quote.USD.percentChange1h")
    change_24h_indis = listings[0]["keysArr"].index("quote.USD.percentChange24h")
    change_7d_indis = listings[0]["keysArr"].index("quote.USD.percentChange7d")
    market_cap_indis = listings[0]["keysArr"].index("quote.USD.marketCap")
    volume_24h_indis = listings[0]["keysArr"].index("quote.USD.volume24h")
    change_30d_indis = listings[0]["keysArr"].index("quote.USD.percentChange30d")
    change_60d_indis = listings[0]["keysArr"].index("quote.USD.percentChange60d")
    change_90d_indis = listings[0]["keysArr"].index("quote.USD.percentChange90d")
    change_1y_indis = listings[0]["keysArr"].index("quote.USD.percentChange1y")
    change_ytd_indis = listings[0]["keysArr"].index(
        "quote.USD.ytdPriceChangePercentage"
    )

    return pd.DataFrame(
        {
            "coin_name": [i[name_indis] for i in listings[1:]],
            "coin_symbol": [i[symbol_indis] for i in listings[1:]],
            "price": [i[price_indis] for i in listings[1:]],
            "percent_change_1h": [i[change_1h_indis] for i in listings[1:]],
            "percent_change_24h": [i[change_24h_indis] for i in listings[1:]],
            "percent_change_7d": [i[change_7d_indis] for i in listings[1:]],
            "percent_change_30d": [i[change_30d_indis] for i in listings[1:]],
            "percent_change_60d": [i[change_60d_indis] for i in listings[1:]],
            "percent_change_90d": [i[change_90d_indis] for i in listings[1:]],
            "percent_change_1y": [i[change_1y_indis] for i in listings[1:]],
            "percent_change_ytd": [i[change_ytd_indis] for i in listings[1:]],
            "market_cap": [i[market_cap_indis] for i in listings[1:]],
            "volume_24h": [i[volume_24h_indis] for i in listings[1:]],
        }
    )


df = load_data()

## Sidebar - Cryptocurrency selections
sorted_coin = sorted(df["coin_symbol"])
selected_coin = col1.multiselect("Cryptocurrency", sorted_coin, sorted_coin)

df_selected_coin = df[(df["coin_symbol"].isin(selected_coin))]  # Filtering data

## Sidebar - Number of coins to display
num_coin = col1.slider("Kaç Coin Gösterilsin", 1, 100, 100)
df_coins = df_selected_coin[:num_coin]

## Sidebar - Percent change timeframe
percent_timeframe = col1.selectbox(
    "Zaman aralığı", ["7d", "24h", "1h", "30d", "60d", "90d", "1y", "ytd"]
)
percent_dict = {
    "7d": "percent_change_7d",
    "24h": "percent_change_24h",
    "1h": "percent_change_1h",
    "30d": "percent_change_30d",
    "60d": "percent_change_60d",
    "90d": "percent_change_90d",
    "1y": "percent_change_1y",
    "ytd": "percent_change_ytd",
}
selected_percent_timeframe = percent_dict[percent_timeframe]

## Sidebar - Sorting values
sort_values = col1.selectbox("Sort values?", ["Yes", "No"])

col2.subheader("Price Data of Selected Cryptocurrency")
col2.write(
    "Data Dimension: "
    + str(df_selected_coin.shape[0])
    + " rows and "
    + str(df_selected_coin.shape[1])
    + " columns."
)

col2.dataframe(df_coins)


# Download CSV data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(data):
    """download csv file"""
    csv = data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    return f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'


col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

# ---------------------------------#
# Preparing data for Bar plot of % Price change
col2.subheader("Table of % Price Change")
df_change = pd.concat(
    [
        df_coins.coin_symbol,
        df_coins.percent_change_1h,
        df_coins.percent_change_24h,
        df_coins.percent_change_7d,
        df_coins.percent_change_30d,
        df_coins.percent_change_60d,
        df_coins.percent_change_90d,
        df_coins.percent_change_1y,
        df_coins.percent_change_ytd,
    ],
    axis=1,
)
df_change = df_change.set_index("coin_symbol")
# print(type(df_change["percent_change_90d"]))
# print(df_change["percent_change_90d"])
df_change["positive_percent_change_1h"] = df_change["percent_change_1h"] > 0
df_change["positive_percent_change_24h"] = df_change["percent_change_24h"] > 0
df_change["positive_percent_change_7d"] = df_change["percent_change_7d"] > 0
df_change["positive_percent_change_30d"] = df_change["percent_change_30d"] > 0
df_change["positive_percent_change_60d"] = df_change["percent_change_60d"] > 0
df_change["positive_percent_change_90d"] = df_change["percent_change_90d"] > 0
df_change["positive_percent_change_1y"] = df_change["percent_change_1y"] > 0
df_change["positive_percent_change_ytd"] = df_change["percent_change_ytd"] > 0
col2.dataframe(df_change)

# Conditional creation of Bar plot (time frame)
col3.subheader("Bar plot of % Price Change")

if percent_timeframe == "7d":
    if sort_values == "Yes":
        df_change = df_change.sort_values(by=["percent_change_7d"])
    col3.write("*7 days period*")
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change["percent_change_7d"].plot(
        kind="barh",
        color=df_change.positive_percent_change_7d.map({True: "g", False: "r"}),
    )
elif percent_timeframe == "24h":
    if sort_values == "Yes":
        df_change = df_change.sort_values(by=["percent_change_24h"])
    col3.write("*24 hour period*")
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change["percent_change_24h"].plot(
        kind="barh",
        color=df_change.positive_percent_change_24h.map({True: "g", False: "r"}),
    )
elif percent_timeframe == "30d":
    if sort_values == "Yes":
        df_change = df_change.sort_values(by=["percent_change_30d"])
    col3.write("*30 days period*")
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change["percent_change_30d"].plot(
        kind="barh",
        color=df_change.positive_percent_change_30d.map({True: "g", False: "r"}),
    )
elif percent_timeframe == "60d":
    if sort_values == "Yes":
        df_change = df_change.sort_values(by=["percent_change_60d"])
    col3.write("*60 days period*")
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change["percent_change_60d"].plot(
        kind="barh",
        color=df_change.positive_percent_change_60d.map({True: "g", False: "r"}),
    )
elif percent_timeframe == "90d":
    if sort_values == "Yes":
        df_change = df_change.sort_values(by=["percent_change_90d"])
    col3.write("*90 days period*")
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change["percent_change_90d"].plot(
        kind="barh",
        color=df_change.positive_percent_change_90d.map({True: "g", False: "r"}),
    )
elif percent_timeframe == "1y":
    if sort_values == "Yes":
        df_change = df_change.sort_values(by=["percent_change_1y"])
    col3.write("*1 year period*")
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change["percent_change_1y"].plot(
        kind="barh",
        color=df_change.positive_percent_change_1y.map({True: "g", False: "r"}),
    )
elif percent_timeframe == "ytd":
    if sort_values == "Yes":
        df_change = df_change.sort_values(by=["percent_change_ytd"])
    col3.write("*Year to date period*")
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change["percent_change_ytd"].plot(
        kind="barh",
        color=df_change.positive_percent_change_ytd.map({True: "g", False: "r"}),
    )
else:
    if sort_values == "Yes":
        df_change = df_change.sort_values(by=["percent_change_1h"])
    col3.write("*1 hour period*")
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change["percent_change_1h"].plot(
        kind="barh",
        color=df_change.positive_percent_change_1h.map({True: "g", False: "r"}),
    )

col3.pyplot(plt)

import multiprocessing

must_reload_page = False

def start_flask():
    if not hasattr(st, 'already_started_server'):
        st.already_started_server = True
        must_reload_page = True

        from flask import Flask

        app = Flask(__name__)

        @app.route('/foo')
        def serve_foo():
            return 'This page is served via Flask!'

        app.run(port=8888)

def reload_page():
    if must_reload_page:
        must_reload_page = False
        st.experimental_rerun()

if __name__=='__main__':
    flask_process = multiprocessing.Process(target=start_flask)
    reload_process = multiprocessing.Process(target=reload_page)
    flask_process.start()
    reload_process.start()


# Your normal Streamlit app goes here:
x = st.slider('Pick a number')
st.write('You picked:', x)


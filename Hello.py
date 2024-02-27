""" APP """

import streamlit as st

# from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json

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
@st.cache_data
def load_data():
    """fetch data"""
    cmc = requests.get("https://coinmarketcap.com", timeout=10)
    soup = BeautifulSoup(cmc.content, "html.parser")

    data = soup.find("script", id="__NEXT_DATA__", type="application/json")

    coin_data = json.loads(data.contents[0])
    coin_data1 = json.loads(coin_data["props"]["initialState"])
    # print("coin data", type(json.loads(coin_data["props"]["initialState"])))
    # st.json(coin_data["props"]["initialState"])
    listings = coin_data1["cryptocurrency"]["listingLatest"]["data"]
    # st.json(coin_data1["cryptocurrency"]["listingLatest"]["data"])
    # for i in listings:
    #     coins[str(i["id"])] = i["slug"]

    coin_name = []
    coin_symbol = []
    market_cap = []
    percent_change_1h = []
    percent_change_24h = []
    percent_change_7d = []
    percent_change_30d = []
    price = []
    volume_24h = []
    first = False
    name_indis = 0
    symbol_indis = 0
    price_indis = 0
    change_1h_indis = 0
    change_24h_indis = 0
    change_7d_indis = 0
    market_cap_indis = 0
    volume_24h_indis = 0
    change_30d_indis = 0
    for i in listings:
        if not first and i["keysArr"] != []:
            print(i["keysArr"])
            for i, j in enumerate(i["keysArr"]):
                match j:
                    case "name":
                        name_indis = i
                    case "symbol":
                        symbol_indis = i
                    case "quote.USD.price":
                        price_indis = i
                    case "quote.USD.percentChange1h":
                        change_1h_indis = i
                    case "quote.USD.percentChange24h":
                        change_24h_indis = i
                    case "quote.USD.percentChange7d":
                        change_7d_indis = i
                    case "quote.USD.marketCap":
                        market_cap_indis = i
                    case "quote.USD.volume24h":
                        volume_24h_indis = i
                    case "quote.USD.percentChange30d":
                        change_30d_indis = i
                    case _:
                        print(i, j)
            first = True
            continue
        coin_name.append(i[name_indis])
        coin_symbol.append(i[symbol_indis])
        price.append(i[price_indis])
        percent_change_1h.append(i[change_1h_indis])
        percent_change_24h.append(i[change_24h_indis])
        percent_change_7d.append(i[change_7d_indis])
        percent_change_30d.append(i[change_30d_indis])
        market_cap.append(i[market_cap_indis])
        volume_24h.append(i[volume_24h_indis])

    data_frame = pd.DataFrame(
        columns=[
            "coin_name",
            "coin_symbol",
            "market_cap",
            "percent_change_1h",
            "percent_change_24h",
            "percent_change_7d",
            "percent_change_30d",
            "price",
            "volume_24h",
        ]
    )
    data_frame["coin_name"] = coin_name
    data_frame["coin_symbol"] = coin_symbol
    data_frame["price"] = price
    data_frame["percent_change_1h"] = percent_change_1h
    data_frame["percent_change_24h"] = percent_change_24h
    data_frame["percent_change_7d"] = percent_change_7d
    data_frame["percent_change_30d"] = percent_change_30d
    data_frame["market_cap"] = market_cap
    data_frame["volume_24h"] = volume_24h
    print(data_frame)
    return data_frame


df = load_data()

## Sidebar - Cryptocurrency selections
sorted_coin = sorted(df["coin_symbol"])
selected_coin = col1.multiselect("Cryptocurrency", sorted_coin, sorted_coin)

df_selected_coin = df[(df["coin_symbol"].isin(selected_coin))]  # Filtering data

## Sidebar - Number of coins to display
num_coin = col1.slider("Kaç Coin Gösterilsin", 1, 100, 100)
df_coins = df_selected_coin[:num_coin]

## Sidebar - Percent change timeframe
percent_timeframe = col1.selectbox("Zaman aralığı", ["7d", "24h", "1h", "30d"])
percent_dict = {
    "7d": "percent_change_7d",
    "24h": "percent_change_24h",
    "1h": "percent_change_1h",
    "30d": "percent_change_30d",
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
    ],
    axis=1,
)
df_change = df_change.set_index("coin_symbol")
df_change["positive_percent_change_1h"] = df_change["percent_change_1h"] > 0
df_change["positive_percent_change_24h"] = df_change["percent_change_24h"] > 0
df_change["positive_percent_change_7d"] = df_change["percent_change_7d"] > 0
df_change["positive_percent_change_30d"] = df_change["percent_change_30d"] > 0
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

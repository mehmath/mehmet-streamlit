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
st.set_page_config(page_title="Plotting Demo", page_icon="📈", layout="wide")

# ---------------------------------#
# Title

# image = Image.open("logo.jpg")

# st.image(image, width=500)


st.sidebar.header("Plotting Demo")
st.title("Borsa Istanbul")
st.markdown(
    """
Bu uygulama https://www.getmidas.com/canli-borsa/xu100-bist-100-hisseleri verisi çekiyor

"""
)
# ---------------------------------#
# About
# expander_bar = st.expander("About")
# expander_bar.markdown(
#     """
# * **Python libraries:** base64, pandas, streamlit, numpy, matplotlib, seaborn, BeautifulSoup, requests, json, time
# * **Data source:** [CoinMarketCap](http://coinmarketcap.com).
# """
# )


# ---------------------------------#
# Page layout (continued)
## Divide page to 3 columns (col1 = sidebar, col2 and col3 = page contents)
col1 = st.sidebar
col2, col3 = st.columns((2, 1))

# # ---------------------------------#
# # Sidebar + Main panel
col1.header("Ayarlar")

# ## Sidebar - Currency price unit
# currency_price_unit = col1.selectbox(" Fiyat için para birimini seçin", ("USD", "", ""))


# Web scraping of CoinMarketCap data
# @st.cache_data
def load_data():
    """Fetch data from CoinMarketCap"""
    try:
        cmc = requests.get(
            "https://www.getmidas.com/canli-borsa/xu100-bist-100-hisseleri", timeout=10
        )
        soup = BeautifulSoup(cmc.content, "html.parser")
        # print(soup.prettify())
        # data = soup.find("table", {"class": "stock-table w-100"})
        # print(data)

        head_data = []
        data = []
        table = soup.find("table", attrs={"class": "stock-table w-100"})
        table_body = table.find("tbody")
        table_thead = table.find("thead")
        # st.json(table_thead)

        head_rows = table_thead.find_all("tr")
        for row in head_rows:
            cols = row.find_all("th")
            cols = [ele.text.strip() for ele in cols]
            head_data.append([ele for ele in cols if ele])

        rows = table_body.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            cols = [ele.text.strip() for ele in cols]
            data.append([ele for ele in cols if ele])

        # st.json(head_data)
        # st.json(data)
        # coin_data = json.loads(data.contents[0])
        # coin_data1 = json.loads(coin_data["props"]["initialState"])
        # listings = coin_data1["cryptocurrency"]["listingLatest"]["data"]
    except requests.exceptions.RequestException as e:
        print(e)
        return None

    hisse_indis = head_data[0].index("Hisse")
    son_indis = head_data[0].index("Son")
    alis_indis = head_data[0].index("Alış")
    satis_indis = head_data[0].index("Satış")
    fark_indis = head_data[0].index("Fark")
    dusuk_indis = head_data[0].index("En Düşük")
    yuksek_indis = head_data[0].index("En Yüksek")
    aof_indis = head_data[0].index("AOF")
    hacimtl_indis = head_data[0].index("Hacim TL")
    hacimlot_indis = head_data[0].index("Hacim Lot")

    return pd.DataFrame(
        {
            "hisse_name": [i[hisse_indis] for i in data],
            "son_fiyat": [i[son_indis] for i in data],
            "alis_fiyat": [i[alis_indis] for i in data],
            "satis_fiyat": [i[satis_indis] for i in data],
            "percent_change_1d": [
                float(i[fark_indis].strip("%").replace(",", ".")) for i in data
            ],
            "dusuk_fiyat": [i[dusuk_indis] for i in data],
            "yuksek_fiyat": [i[yuksek_indis] for i in data],
            "aof": [i[aof_indis] for i in data],
            "hacim_tl": [i[hacimtl_indis] for i in data],
            "hacim_lot": [i[hacimlot_indis] for i in data],
        }
    )


# print(load_data())
# st.json(load_data())

df = load_data()

## Sidebar - Cryptocurrency selections
sorted_coin = sorted(df["hisse_name"])
selected_coin = col1.multiselect("Hisseler", sorted_coin, sorted_coin)

df_selected_coin = df[(df["hisse_name"].isin(selected_coin))]  # Filtering data

## Sidebar - Number of coins to display
num_coin = col1.slider("Kaç Hisse Gösterilsin", 1, 100, 100)
df_coins = df_selected_coin[:num_coin]

## Sidebar - Percent change timeframe
percent_timeframe = col1.selectbox("Zaman aralığı", ["1d"])
percent_dict = {
    "1d": "percent_change_1d",
}
selected_percent_timeframe = percent_dict[percent_timeframe]

## Sidebar - Sorting values
sort_values = col1.selectbox("Sort values?", ["Yes", "No"])

col2.subheader("Seçilen hisse fiyat datası")
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
        df_coins.hisse_name,
        df_coins.percent_change_1d,
    ],
    axis=1,
)
df_change = df_change.set_index("hisse_name")
# print(type(df_change["percent_change_1d"]))
# print(df_change["percent_change_1d"])
df_change["positive_percent_change_1d"] = df_change["percent_change_1d"] > 0
col2.dataframe(df_change)

# Conditional creation of Bar plot (time frame)
col3.subheader("Bar plot of % Price Change")

if percent_timeframe == "1d":
    if sort_values == "Yes":
        df_change = df_change.sort_values(by=["percent_change_1d"])
    col3.write("*7 days period*")
    plt.figure(figsize=(5, 25))
    plt.subplots_adjust(top=1, bottom=0)
    df_change["percent_change_1d"].plot(
        kind="barh",
        color=df_change.positive_percent_change_1d.map({True: "g", False: "r"}),
    )

col3.pyplot(plt)

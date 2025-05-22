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
currency_price_unit = col1.selectbox(
    " Fiyat için para birimini seçin", ("USD", "BTC", "")
)


# Web scraping of CoinMarketCap data
# @st.cache_data # Consider re-enabling caching after debugging
# Web scraping of CoinMarketCap data
# @st.cache_data # Hata ayıklama sonrası önbelleğe almayı yeniden etkinleştirmeyi düşünün
def load_data():
    """Fetch data from CoinMarketCap"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        cmc = requests.get("https://coinmarketcap.com", headers=headers, timeout=10)
        cmc.raise_for_status() # Kötü yanıtlar için HTTPError yükselt (4xx veya 5xx)
        soup = BeautifulSoup(cmc.content, "html.parser")

        data = soup.find("script", id="__NEXT_DATA__", type="application/json")
        if not data or not data.contents:
            st.error("Could not find __NEXT_DATA__ script tag on CoinMarketCap")
            return pd.DataFrame()

        coin_data = json.loads(data.contents[0])
# coin_data'yı bir dosyaya yaz
        # try:
        #     with open("coin_data.json", "w", encoding="utf-8") as f:
        #         json.dump(coin_data, f, ensure_ascii=False, indent=4)
        #     st.success("coin_data başarıyla 'coin_data.json' dosyasına yazıldı.")
        # except IOError as e:
        #     st.error(f"coin_data dosyasına yazılırken hata oluştu: {e}")

        # Güncellenmiş: Veri yapısını log dosyasından kontrol edin
        # 'props' -> 'pageProps' -> 'dehydratedState' -> 'queries' -> [0] -> 'state' -> 'data' -> 'data' -> 'listing' -> 'cryptoCurrencyList'
        try:
            listings = coin_data["props"]["dehydratedState"]["queries"][1]["state"]["data"]["data"]["listing"]["cryptoCurrencyList"]
        except (KeyError, IndexError, TypeError) as e:
            st.error(f"Error accessing cryptocurrency list in API response. Structure might have changed. Error: {e}")
            # Hata ayıklama için API yanıtının bir kısmını göster
            st.json(coin_data.get("props", {}).get("pageProps", {}).get("dehydratedState", {}))
            return pd.DataFrame()


        if not listings or not isinstance(listings, list):
             st.error("No cryptocurrency data found in the expected path or data is not a list.")
             return pd.DataFrame()

        # Güncellenmiş: Veri çıkarma mantığı
        extracted_data = []
        for coin in listings:
            # Temel bilgileri güvenli bir şekilde al
            coin_name = coin.get("name")
            coin_symbol = coin.get("symbol")
            cmc_rank = coin.get("cmcRank")

            # Fiyat tekliflerini (quotes) güvenli bir şekilde al
            quotes = coin.get("quotes", [])
            usd_quote = next((q for q in quotes if q.get("name") == "USD"), None) # USD fiyatını bul
            btc_quote = next((q for q in quotes if q.get("name") == "BTC"), None) # BTC fiyatını bul (gerekirse)

            if not usd_quote: # En azından USD fiyatı olmalı
                continue # USD fiyatı yoksa bu coini atla

            # Gerekli alanları USD fiyat teklifinden al
            price = usd_quote.get("price")
            market_cap = usd_quote.get("marketCap")
            percent_change_1h = usd_quote.get("percentChange1h")
            percent_change_24h = usd_quote.get("percentChange24h")
            percent_change_7d = usd_quote.get("percentChange7d")
            percent_change_30d = usd_quote.get("percentChange30d")
            percent_change_60d = usd_quote.get("percentChange60d")
            percent_change_90d = usd_quote.get("percentChange90d")
            volume_24h = usd_quote.get("volume24h")
            # Yıllık ve YTD (Yılbaşından Bugüne) değişim CoinMarketCap API'sinde farklı isimlere sahip olabilir, kontrol edilmeli
            # Örnek olarak varsayılan değerler kullanıldı, API yanıtına göre güncelleyin
            percent_change_1y = usd_quote.get("percentChange1y") # Bu anahtarın varlığından emin olun
            percent_change_ytd = usd_quote.get("ytdPriceChangePercentage") # Bu anahtarın varlığından emin olun


            extracted_data.append({
                 "coin_name": coin_name,
                 "coin_symbol": coin_symbol,
                 "rank": cmc_rank,
                 "price": price,
                 "percent_change_1h": percent_change_1h,
                 "percent_change_24h": percent_change_24h,
                 "percent_change_7d": percent_change_7d,
                 "percent_change_30d": percent_change_30d,
                 "percent_change_60d": percent_change_60d,
                 "percent_change_90d": percent_change_90d,
                 "percent_change_1y": percent_change_1y,
                 "percent_change_ytd": percent_change_ytd,
                 "market_cap": market_cap,
                 "volume_24h": volume_24h,
             })

        df = pd.DataFrame(extracted_data)

         # İsteğe bağlı: Temel verilerin (ör. isim, sembol, fiyat) eksik olduğu satırları bırak
        essential_cols = ["coin_name", "coin_symbol", "price"]
        df.dropna(subset=essential_cols, inplace=True)

         # Sıralama ve sayı seçimi gibi diğer işlemler için sütun adlarının tutarlı olduğundan emin olun
         # Örneğin, rank sütununu kullanmak isterseniz 'rank' olarak adlandırıldığından emin olun.
         # df.rename(columns={'rank': 'cmcRank'}, inplace=True) # Gerekirse yeniden adlandırın


    except requests.exceptions.RequestException as e:
        st.error(f"CoinMarketCap'e bağlanırken hata oluştu: {e}")
        return pd.DataFrame() # Bağlantı hatasında boş DataFrame döndür
    except json.JSONDecodeError as e:
        st.error(f"API yanıtı JSON olarak ayrıştırılamadı: {e}")
        st.text(cmc.text[:500] + "...") # Hata ayıklama için ham yanıtın bir kısmını göster
        return pd.DataFrame() # JSON hatasında boş DataFrame döndür
    except Exception as e: # Diğer beklenmedik hataları yakala
        st.error(f"Veri yüklenirken beklenmedik bir hata oluştu: {e}")
        import traceback
        st.error(traceback.format_exc()) # Hata ayıklama için tam traceback'i yazdır
        return pd.DataFrame()

    # 'currency_price_unit' seçimine göre fiyatları ayarlama (bu kısım zaten kodunuzda mevcut olabilir)
    # Eğer BTC fiyatlarını göstermek istiyorsanız benzer bir mantıkla BTC fiyatını seçmeniz gerekir.
    # Örneğin:
    # if currency_price_unit == 'BTC' and btc_quote:
    #     price = btc_quote.get("price")
    #     # BTC için diğer değişim yüzdelerini de almanız gerekebilir
    # elif currency_price_unit == 'USD' and usd_quote:
    #     price = usd_quote.get("price")
    # else: # Varsayılan USD
    #     price = usd_quote.get("price") if usd_quote else None


    return df

df = load_data()

# Add a check here to ensure df is not empty before proceeding
if df is None or df.empty:
    st.error("Veri yüklenemediği için uygulama devam edemiyor.")
    st.stop() # Stop execution if data loading failed

## Sidebar - Cryptocurrency selections
# Check if 'coin_symbol' column exists before sorting/selecting
if "coin_symbol" in df.columns:
    sorted_coin = sorted(df["coin_symbol"].unique()) # Use unique symbols
    selected_coin = col1.multiselect("Cryptocurrency", sorted_coin, sorted_coin) # Default to all
    df_selected_coin = df[(df["coin_symbol"].isin(selected_coin))]  # Filtering data
else:
    st.warning("'coin_symbol' sütunu DataFrame'de bulunamadı.")
    selected_coin = [] # Set selected_coin to empty list
    df_selected_coin = pd.DataFrame() # Use empty DataFrame

## Sidebar - Number of coins to display
# Ensure df_selected_coin is not empty before slicing
if not df_selected_coin.empty:
    num_coin = col1.slider("Kaç Coin Gösterilsin", 1, len(df_selected_coin), min(100, len(df_selected_coin))) # Adjust max/default based on available coins
    df_coins = df_selected_coin[:num_coin]
else:
    num_coin = 0
    df_coins = pd.DataFrame()


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

# Display dataframe only if it's not empty
if not df_coins.empty:
    col2.dataframe(df_coins)
else:
    col2.write("Gösterilecek veri yok.")


# Download CSV data
# https://discuss.streamlit.io/t/how-to-download-file-in-streamlit/1806
def filedownload(data):
    """download csv file"""
    if data.empty:
        return "İndirilecek veri yok."
    csv = data.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    return f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'


col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

# ---------------------------------#
# Preparing data for Bar plot of % Price change
col2.subheader("Table of % Price Change")

# Check if df_coins is empty before creating df_change
if not df_coins.empty and "coin_symbol" in df_coins.columns:
    # Ensure all required percentage columns exist before concatenation
    required_cols = [
        "coin_symbol",
        "percent_change_1h", "percent_change_24h", "percent_change_7d",
        "percent_change_30d", "percent_change_60d", "percent_change_90d",
        "percent_change_1y", "percent_change_ytd"
    ]
    available_cols = [col for col in required_cols if col in df_coins.columns]
    missing_cols = set(required_cols) - set(available_cols)
    if missing_cols:
        st.warning(f"Grafik için eksik sütunlar: {', '.join(missing_cols)}")

    if "coin_symbol" in available_cols: # Need at least coin_symbol
        df_change = df_coins[available_cols].copy() # Use copy to avoid SettingWithCopyWarning
        df_change = df_change.set_index("coin_symbol")

        # Create boolean columns only for available percentage columns
        for col in available_cols:
            if col != "coin_symbol":
                # Ensure column is numeric before comparison
                df_change[col] = pd.to_numeric(df_change[col], errors='coerce')
                # Check if column conversion was successful before creating boolean col
                if pd.api.types.is_numeric_dtype(df_change[col]):
                    df_change[f"positive_{col}"] = df_change[col] > 0
                else:
                    # Handle cases where conversion failed (e.g., column remains object type)
                    # Maybe fill positive col with False or skip it
                    df_change[f"positive_{col}"] = False # Or None, or skip

        col2.dataframe(df_change)
    else:
        df_change = pd.DataFrame() # Create empty df_change if coin_symbol is missing
        col2.write("Değişim tablosu için veri yok ('coin_symbol' eksik).")

else:
    df_change = pd.DataFrame() # Create empty df_change if df_coins is empty
    col2.write("Değişim tablosu için veri yok.")


# Conditional creation of Bar plot (time frame)
col3.subheader("Bar plot of % Price Change")

# Check if df_change is empty or the selected timeframe column exists
if not df_change.empty and selected_percent_timeframe in df_change.columns:
    plot_col = selected_percent_timeframe
    positive_col = f"positive_{plot_col}"

    # Ensure the positive column exists and the plot column is numeric
    if positive_col in df_change.columns and pd.api.types.is_numeric_dtype(df_change[plot_col]):
        df_plot = df_change[[plot_col, positive_col]].dropna(subset=[plot_col]) # Drop NaNs for plotting

        if not df_plot.empty:
            if sort_values == "Yes":
                df_plot = df_plot.sort_values(by=[plot_col])

            col3.write(f"*{percent_timeframe} period*")
            # Use try-except for plotting as a final safeguard
            try:
                fig, ax = plt.subplots(figsize=(5, max(1, len(df_plot) * 0.3))) # Adjust height
                fig.subplots_adjust(left=0.3, top=1, bottom=0.1) # Adjust margins for labels
                df_plot[plot_col].plot(
                    kind="barh",
                    color=df_plot[positive_col].map({True: "g", False: "r"}),
                    ax=ax # Pass axis to plot
                )
                ax.set_ylabel("") # Remove y-axis label if needed
                col3.pyplot(fig) # Pass the figure object
                plt.close(fig) # Close the figure to free memory
            except Exception as plot_err:
                col3.error(f"Grafik çizilirken hata oluştu: {plot_err}")
        else:
            col3.write(f"'{plot_col}' için çizilecek geçerli veri yok.")
    else:
         col3.write(f"'{plot_col}' için grafik çizilemiyor (veri eksik veya numerik değil).")

else:
    col3.write("Grafik için veri yok veya seçilen zaman aralığı sütunu eksik.")


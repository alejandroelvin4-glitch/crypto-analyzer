import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(page_title="Crypto Analyzer", layout="wide")

st.title("🚀 Crypto Analyzer")

@st.cache_data(ttl=300)
def get_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }

    response = requests.get(url, params=params)
    return response.json()

if st.button("🔄 Actualizar análisis"):

    try:

        coins = get_data()

        results = []

        for coin in coins:

            change = coin.get("price_change_percentage_24h", 0)

            score = 50

            if change > 0:
                score += min(change, 30)

            if change > 5:
                score += 10

            if change < -10:
                score -= 20

            score = max(0, min(100, score))

            results.append({
                "Moneda": coin["symbol"].upper(),
                "Precio": coin["current_price"],
                "Cambio 24h %": round(change, 2),
                "Market Cap": coin["market_cap"],
                "Score": round(score, 1)
            })

        df = pd.DataFrame(results)

        df = df.sort_values(
            by="Score",
            ascending=False
        )

        st.dataframe(
            df,
            use_container_width=True
        )

        st.subheader("📊 Top 10")

        st.bar_chart(
            df.head(10)
            .set_index("Moneda")["Score"]
        )

    except Exception as e:
        st.error(str(e))

st.caption(
    "Última actualización: "
    + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
)

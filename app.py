import streamlit as st
import requests

st.title("Prueba de Datos")

try:
    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1
    }

    data = requests.get(url, params=params).json()

    st.success("Conexión exitosa")

    for coin in data:
        st.write(
            coin["symbol"].upper(),
            coin["current_price"]
        )

except Exception as e:
    st.error(str(e))

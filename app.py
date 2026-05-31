import streamlit as st
import requests

st.title("Prueba Binance Futures")

try:

    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"

    data = requests.get(url, timeout=10).json()

    symbols = []

    for s in data["symbols"]:
        if (
            s["contractType"] == "PERPETUAL"
            and s["symbol"].endswith("USDT")
        ):
            symbols.append(s["symbol"])

    st.success(f"Contratos encontrados: {len(symbols)}")

    st.write(symbols[:50])

except Exception as e:
    st.error(str(e))

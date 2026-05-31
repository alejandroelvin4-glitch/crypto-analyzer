import streamlit as st
import pandas as pd
import numpy as np
from binance.um_futures import UMFutures
from datetime import datetime

st.set_page_config(
    page_title="Crypto Analyzer Pro",
    layout="wide"
)

st.title("🚀 Binance Futures Analyzer Pro")

client = UMFutures()


def calculate_rsi(series, period=14):
    delta = series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + rs))

    return rsi


def analyze_symbol(symbol):

    klines = client.klines(
        symbol=symbol,
        interval="4h",
        limit=150
    )

    df = pd.DataFrame(
        klines,
        columns=[
            'open_time',
            'open',
            'high',
            'low',
            'close',
            'volume',
            'close_time',
            'quote_asset_volume',
            'trades',
            'taker_buy_base',
            'taker_buy_quote',
            'ignore'
        ]
    )

    numeric_cols = [
        'open',
        'high',
        'low',
        'close',
        'volume'
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])

    df["EMA20"] = df["close"].ewm(span=20).mean()
    df["EMA50"] = df["close"].ewm(span=50).mean()

    df["RSI"] = calculate_rsi(df["close"])

    price = df["close"].iloc[-1]

    change10 = (
        (price - df["close"].iloc[-10])
        / df["close"].iloc[-10]
        * 100
    )

    rsi = df["RSI"].iloc[-1]

    ema20 = df["EMA20"].iloc[-1]
    ema50 = df["EMA50"].iloc[-1]

    score = 50

    if ema20 > ema50:
        score += 15

    if price > ema20:
        score += 10

    if change10 > 0:
        score += min(change10, 15)

    if 50 <= rsi <= 70:
        score += 10

    if rsi > 80:
        score -= 15

    score = max(0, min(score, 100))

    return {
        "Símbolo": symbol,
        "Precio": round(price, 5),
        "RSI": round(rsi, 1),
        "EMA20": round(ema20, 5),
        "EMA50": round(ema50, 5),
        "Cambio 10 velas %": round(change10, 2),
        "Score Long": round(score, 1)
    }


if st.button("🔄 Actualizar análisis"):

    with st.spinner("Analizando mercado..."):

        results = []

        try:

            exchange_info = client.exchange_info()

            symbols = [
                s["symbol"]
                for s in exchange_info["symbols"]
                if s["status"] == "TRADING"
                and s["contractType"] == "PERPETUAL"
                and s["symbol"].endswith("USDT")
            ]

            symbols = symbols[:50]

            progress = st.progress(0)

            for i, symbol in enumerate(symbols):

                try:
                    result = analyze_symbol(symbol)
                    results.append(result)

                except:
                    pass

                progress.progress((i + 1) / len(symbols))

            if results:

                df = pd.DataFrame(results)

                df = df.sort_values(
                    by="Score Long",
                    ascending=False
                )

                st.subheader("🏆 Mejores oportunidades")

                st.dataframe(
                    df,
                    use_container_width=True
                )

                st.subheader("📊 Top 10")

                chart = (
                    df.head(10)
                    .set_index("Símbolo")["Score Long"]
                )

                st.bar_chart(chart)

                mejores = df.head(5)

                st.subheader("🔥 Top 5")

                st.table(mejores)

            else:
                st.warning(
                    "No se encontraron señales."
                )

        except Exception as e:
            st.error(str(e))

st.caption(
    "Última carga: "
    + datetime.now().strftime("%d/%m/%Y %H:%M:%S")
)
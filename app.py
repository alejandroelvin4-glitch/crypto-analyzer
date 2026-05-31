import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Crypto Radar V1",
    layout="wide"
)

st.title("🚀 Crypto Radar V1")

@st.cache_data(ttl=300)
def get_market_data():

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


if st.button("🔄 Escanear Mercado"):

    try:

        data = get_market_data()

        resultados = []

        for coin in data:

            cambio = coin.get(
                "price_change_percentage_24h",
                0
            )

            volumen = coin.get(
                "total_volume",
                0
            )

            market_cap = coin.get(
                "market_cap",
                1
            )

            volumen_ratio = volumen / market_cap

            pump_score = min(
                100,
                max(
                    0,
                    cambio * 4 + volumen_ratio * 100
                )
            )

            dump_score = min(
                100,
                max(
                    0,
                    abs(min(cambio, 0)) * 5
                )
            )

            explosividad = min(
                100,
                abs(cambio) * 3
                + volumen_ratio * 200
            )

            if cambio > 3:
                sesgo = "LONG"

            elif cambio < -3:
                sesgo = "SHORT"

            else:
                sesgo = "NEUTRO"

            confianza = min(
                100,
                abs(cambio) * 5
            )

            resultados.append({

                "Activo":
                coin["symbol"].upper(),

                "Precio":
                coin["current_price"],

                "Sesgo":
                sesgo,

                "Confianza":
                round(confianza, 1),

                "Pump":
                round(pump_score, 1),

                "Dump":
                round(dump_score, 1),

                "Explosividad":
                round(explosividad, 1)
            })
        
        df = pd.DataFrame(resultados)

        st.subheader("🔥 Ranking General")

        st.dataframe(
            df.sort_values(
                "Explosividad",
                ascending=False
            ),
            use_container_width=True
        )

        st.subheader("🚀 Posibles Pumps")

        st.dataframe(
            df.sort_values(
                "Pump",
                ascending=False
            ).head(10),
            use_container_width=True
        )

        st.subheader("💥 Posibles Dumps")

        st.dataframe(
            df.sort_values(
                "Dump",
                ascending=False
            ).head(10),
            use_container_width=True
        )

    except Exception as e:

        st.error(str(e))

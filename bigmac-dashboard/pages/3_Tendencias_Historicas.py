"""Página: Tendências históricas de preços (2010-2025)."""

from __future__ import annotations

import streamlit as st

from src.data_loader import load_historical_df
from src.charts import historical_line_chart
from src.styling import load_css

st.set_page_config(page_title="Tendências | Big Mac Index", page_icon="📈", layout="wide")
load_css()

st.title("📈 Tendências Históricas de Preços (2010–2025)")

st.info(
    "⚠️ A série histórica exibida aqui é **ilustrativa**, construída a partir do preço "
    "mais recente de cada país com uma trajetória de crescimento plausível — não são os "
    "valores exatos publicados pelo The Economist em cada semestre. Para dados históricos "
    "reais e completos desde 2000, substitua `data/historical_prices.csv` pelo dataset bruto em "
    "[TheEconomist/big-mac-data](https://github.com/TheEconomist/big-mac-data).",
    icon="⚠️",
)

hist_df = load_historical_df()
all_countries = sorted(hist_df["name"].unique())

default_selection = [c for c in ["United States", "Switzerland", "Japan", "Brazil"] if c in all_countries]

selected_countries = st.multiselect(
    "Selecione os países para comparar", options=all_countries, default=default_selection or all_countries[:4]
)

if not selected_countries:
    st.warning("Selecione ao menos um país para visualizar o gráfico.")
else:
    st.plotly_chart(historical_line_chart(hist_df, selected_countries), use_container_width=True)

    st.divider()
    st.subheader("Dados da série selecionada")
    table = hist_df[hist_df["name"].isin(selected_countries)].pivot(
        index="year", columns="name", values="price_usd"
    )
    st.dataframe(table, use_container_width=True)

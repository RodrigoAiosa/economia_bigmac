"""Página: Tendências históricas de preços, via GET /history da API (com fallback local)."""

from __future__ import annotations

import streamlit as st

from src.charts import historical_line_chart
from src.data_loader import get_data_source, load_countries_df, load_fallback_country_list, load_historical_df
from src.styling import load_css

st.set_page_config(page_title="Tendências | Big Mac Index", page_icon="📈", layout="wide")
load_css()

st.title("📈 Tendências Históricas de Preços")

source = get_data_source()

if source == "api":
    st.success(
        "🟢 Exibindo histórico ao vivo via **GET /history** da API do bigmacindex.com.",
        icon="🟢",
    )
    df = load_countries_df()
    name_to_iso2 = dict(zip(df["name"], df["iso2"]))
    all_countries = sorted(name_to_iso2.keys())
else:
    st.warning(
        "🟡 Nenhuma API key configurada (ou a API está indisponível no momento) — exibindo uma "
        "série **ilustrativa** de referência. Configure `BIGMAC_API_KEY` para ver o histórico real. "
        "Veja as instruções no README.",
        icon="🟡",
    )
    all_countries = load_fallback_country_list()
    name_to_iso2 = {}

default_selection = [c for c in ["United States", "Switzerland", "Japan", "Brazil"] if c in all_countries]

col1, col2 = st.columns([3, 1])
with col1:
    selected_countries = st.multiselect(
        "Selecione os países para comparar",
        options=all_countries,
        default=default_selection or all_countries[:4],
    )
with col2:
    days = st.selectbox("Janela de tempo", options=[30, 90, 180, 365], index=3, format_func=lambda d: f"{d} dias")

if not selected_countries:
    st.warning("Selecione ao menos um país para visualizar o gráfico.")
else:
    if source == "api":
        countries_map = {name: name_to_iso2[name] for name in selected_countries}
        hist_df = load_historical_df(countries_map, days=days)
    else:
        # No modo fallback, o CSV local já contém todos os países disponíveis;
        # chamamos load_historical_df com um dict vazio de mapeamento ISO-2 para
        # forçar o uso do caminho de fallback por nome, dentro da própria função.
        hist_df = load_historical_df({name: "" for name in selected_countries}, days=days)

    if hist_df.empty:
        st.error("Não foi possível obter dados históricos para os países selecionados.")
    else:
        st.plotly_chart(historical_line_chart(hist_df, selected_countries), use_container_width=True)

        st.divider()
        st.subheader("Dados da série selecionada")
        table = hist_df.pivot_table(index="date", columns="name", values="price_usd")
        st.dataframe(table, use_container_width=True)

        csv_bytes = table.to_csv().encode("utf-8")
        st.download_button(
            "⬇️ Baixar série em CSV", data=csv_bytes, file_name="big_mac_index_historico.csv", mime="text/csv"
        )

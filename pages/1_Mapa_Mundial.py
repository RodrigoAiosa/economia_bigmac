"""Página: Mapa Mundial detalhado, com filtros por região e faixa de preço."""

from __future__ import annotations

import streamlit as st

from src.data_loader import load_countries_df, region_label_map
from src.maps import build_price_choropleth, build_diff_choropleth
from src.metrics import add_valuation_column
from src.styling import load_css

st.set_page_config(page_title="Mapa Mundial | Big Mac Index", page_icon="🗺️", layout="wide")
load_css()

st.title("🗺️ Mapa Mundial do Big Mac Index")
st.caption("Filtre por região e faixa de preço para explorar o mapa interativo.")

df = load_countries_df()
df = add_valuation_column(df)
region_labels = region_label_map()

# --------------------------------------------------------------------------
# Filtros (sidebar)
# --------------------------------------------------------------------------
with st.sidebar:
    st.header("Filtros")

    regions_pt = sorted(region_labels.values())
    selected_regions_pt = st.multiselect(
        "Região", options=regions_pt, default=regions_pt
    )
    inv_region_labels = {v: k for k, v in region_labels.items()}
    selected_regions = [inv_region_labels[r] for r in selected_regions_pt]

    price_min, price_max = float(df["price_usd"].min()), float(df["price_usd"].max())
    price_range = st.slider(
        "Faixa de preço (US$)",
        min_value=round(price_min, 2),
        max_value=round(price_max, 2),
        value=(round(price_min, 2), round(price_max, 2)),
    )

    map_mode = st.radio("Colorir mapa por", ["Preço (US$)", "Variação % vs. base"])

filtered = df[
    df["region"].isin(selected_regions)
    & df["price_usd"].between(price_range[0], price_range[1])
]

st.markdown(f"**{len(filtered)}** países exibidos de **{len(df)}** no total.")

if filtered.empty:
    st.warning("Nenhum país corresponde aos filtros selecionados.")
else:
    if map_mode == "Preço (US$)":
        st.plotly_chart(build_price_choropleth(filtered), use_container_width=True)
    else:
        st.plotly_chart(build_diff_choropleth(filtered), use_container_width=True)

    st.divider()
    st.subheader("Tabela de dados filtrados")
    display_df = filtered[
        ["rank", "flag", "name", "region", "currency_code", "local_price", "price_usd", "diff_percent", "valuation"]
    ].rename(
        columns={
            "rank": "#",
            "flag": "",
            "name": "País",
            "region": "Região",
            "currency_code": "Moeda",
            "local_price": "Preço local",
            "price_usd": "Preço (US$)",
            "diff_percent": "Diferença (%)",
            "valuation": "Classificação",
        }
    )
    display_df["Região"] = display_df["Região"].map(region_labels).fillna(display_df["Região"])
    st.dataframe(display_df, use_container_width=True, hide_index=True)

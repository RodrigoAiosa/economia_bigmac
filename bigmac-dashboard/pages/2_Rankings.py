"""Página: Rankings completos com seleção de moeda-base e gráficos de extremos."""

from __future__ import annotations

import streamlit as st

from src.data_loader import load_countries_df, region_label_map
from src.metrics import recompute_base_currency, add_valuation_column, top_n
from src.charts import ranking_bar_chart, extremes_bar_chart, region_box_plot
from src.styling import load_css

st.set_page_config(page_title="Rankings | Big Mac Index", page_icon="📊", layout="wide")
load_css()

st.title("📊 Rankings Completos do Big Mac Index")

df = load_countries_df()
region_labels = region_label_map()

# --------------------------------------------------------------------------
# Seleção de moeda-base
# --------------------------------------------------------------------------
base_options = df[["code", "name", "flag"]].copy()
base_options["label"] = base_options["flag"] + " " + base_options["name"]
default_idx = int(base_options.index[base_options["code"] == "USA"][0])

selected_label = st.selectbox(
    "Comparar preços em relação a:", options=base_options["label"], index=default_idx
)
base_code = base_options.loc[base_options["label"] == selected_label, "code"].iloc[0]

df_base = recompute_base_currency(df, base_code)
df_base = add_valuation_column(df_base, diff_col="diff_percent_base")

st.caption(
    f"Todos os valores abaixo estão recalculados usando **{selected_label}** como referência (0%)."
)

# --------------------------------------------------------------------------
# Filtro por região
# --------------------------------------------------------------------------
regions_pt = sorted(region_labels.values())
tabs = st.tabs(["Todos"] + regions_pt)

inv_region_labels = {v: k for k, v in region_labels.items()}

for tab, region_pt in zip(tabs, ["Todos"] + regions_pt):
    with tab:
        if region_pt == "Todos":
            sub = df_base
        else:
            sub = df_base[df_base["region"] == inv_region_labels[region_pt]]

        st.plotly_chart(ranking_bar_chart(sub), use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
# Extremos: mais caros vs. mais baratos
# --------------------------------------------------------------------------
st.subheader("🔝 Top 10 mais caros vs. Top 10 mais baratos")
n = st.slider("Quantidade em cada grupo", min_value=5, max_value=20, value=10)
cheapest = top_n(df_base, n=n, ascending=True)
priciest = top_n(df_base, n=n, ascending=False)
st.plotly_chart(extremes_bar_chart(cheapest, priciest), use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
# Distribuição por região
# --------------------------------------------------------------------------
st.subheader("📦 Distribuição de preços por região")
st.plotly_chart(region_box_plot(df_base, region_labels), use_container_width=True)

st.divider()

# --------------------------------------------------------------------------
# Tabela completa
# --------------------------------------------------------------------------
st.subheader("📋 Tabela completa")
table_df = df_base[
    ["rank", "flag", "name", "region", "currency_code", "local_price", "price_base", "diff_percent_base", "valuation"]
].rename(
    columns={
        "rank": "#",
        "flag": "",
        "name": "País",
        "region": "Região",
        "currency_code": "Moeda",
        "local_price": "Preço local",
        "price_base": f"Preço (em {selected_label.split(' ', 1)[1]})",
        "diff_percent_base": "Diferença (%)",
        "valuation": "Classificação",
    }
)
table_df["Região"] = table_df["Região"].map(region_labels).fillna(table_df["Região"])
st.dataframe(table_df, use_container_width=True, hide_index=True)

csv_bytes = table_df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Baixar tabela em CSV", data=csv_bytes, file_name="big_mac_index_ranking.csv", mime="text/csv")

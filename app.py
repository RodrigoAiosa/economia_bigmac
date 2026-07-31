"""
app.py
------
Página inicial (Home) do Big Mac Index Dashboard.

Fonte de dados: API do bigmacindex.com (https://bigmacindex.com/api),
com fallback automático para um snapshot local caso a API key não esteja
configurada ou o serviço esteja indisponível.

Estrutura do projeto:
    app.py                  <- este arquivo (ponto de entrada do Streamlit)
    pages/                  <- páginas adicionais (multipage app)
    src/                    <- lógica de dados (API + fallback), métricas, mapas e gráficos
    data/                   <- dados de fallback offline (JSON + CSV)
    assets/                 <- CSS customizado
    .streamlit/config.toml  <- tema visual

Execução local:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from src.data_loader import get_data_source, load_countries_df, load_meta, region_label_map
from src.metrics import summary_stats, add_valuation_column
from src.maps import build_price_choropleth, build_diff_choropleth
from src.styling import load_css, kpi_card, render_kpi_row

st.set_page_config(
    page_title="Big Mac Index Dashboard",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

# --------------------------------------------------------------------------
# Cabeçalho
# --------------------------------------------------------------------------
meta = load_meta()
source = get_data_source()

hero_html = (
    '<div class="hero-banner">'
    "<h1>🍔 Big Mac Index Dashboard</h1>"
    "<p>Paridade do poder de compra (PPP) e valorização cambial em "
    f"{meta['total_countries']} países, com base nos dados do "
    "<b>bigmacindex.com</b>. Última atualização dos dados: "
    f"{meta['data_date']}.</p>"
    "</div>"
)
st.markdown(hero_html, unsafe_allow_html=True)

if source == "api":
    st.success("🟢 Dados ao vivo via API (bigmacindex.com).", icon="🟢")
else:
    st.warning(
        "🟡 Nenhuma API key configurada (ou a API está indisponível) — exibindo um "
        "**snapshot offline** de referência. Veja no README como configurar `BIGMAC_API_KEY` "
        "para habilitar os dados ao vivo.",
        icon="🟡",
    )

# --------------------------------------------------------------------------
# Dados
# --------------------------------------------------------------------------
df = load_countries_df()
df = add_valuation_column(df)
stats = summary_stats(df)
region_labels = region_label_map()

# --------------------------------------------------------------------------
# Indicadores (KPIs)
# --------------------------------------------------------------------------
cards = [
    kpi_card("Países cobertos", str(stats["n_countries"]), help_text="Fonte: bigmacindex.com API"),
    kpi_card("Preço médio global", f"US$ {stats['avg_price']:.2f}"),
    kpi_card(
        "Mais caro",
        stats["most_expensive_name"],
        delta=f"US$ {stats['most_expensive_price']:.2f}",
    ),
    kpi_card(
        "Mais barato",
        stats["cheapest_name"],
        delta=f"US$ {stats['cheapest_price']:.2f}",
    ),
    kpi_card("Diferença de poder de compra", f"{stats['spread_ratio']:.1f}x", help_text="Mais caro ÷ mais barato"),
]
render_kpi_row(cards)

col_a, col_b = st.columns(2)
col_a.metric("Moedas sobrevalorizadas (vs. USD)", stats["n_overvalued"])
col_b.metric("Moedas subvalorizadas (vs. USD)", stats["n_undervalued"])

st.divider()

# --------------------------------------------------------------------------
# Mapas
# --------------------------------------------------------------------------
st.subheader("🌍 Mapa Mundial Interativo")

tab_price, tab_diff = st.tabs(["💵 Preço em USD", "📊 Variação % vs. base (USD)"])

with tab_price:
    st.plotly_chart(build_price_choropleth(df), use_container_width=True)
    st.caption("Passe o mouse sobre um país para ver o preço do Big Mac em dólares.")

with tab_diff:
    st.plotly_chart(build_diff_choropleth(df), use_container_width=True)
    st.caption(
        "Verde = moeda subvalorizada (Big Mac mais barato que nos EUA). "
        "Vermelho = moeda sobrevalorizada (Big Mac mais caro que nos EUA)."
    )

st.divider()

# --------------------------------------------------------------------------
# Navegação para outras páginas
# --------------------------------------------------------------------------
st.subheader("📑 Explore mais")
nav_cols = st.columns(3)
nav_cols[0].page_link("pages/1_Mapa_Mundial.py", label="🗺️ Mapa Mundial detalhado", icon="🗺️")
nav_cols[1].page_link("pages/2_Rankings.py", label="📊 Rankings completos", icon="📊")
nav_cols[2].page_link("pages/3_Tendencias_Historicas.py", label="📈 Tendências históricas", icon="📈")
nav_cols2 = st.columns(3)
nav_cols2[0].page_link("pages/4_Calculadora_PPP.py", label="🧮 Calculadora de PPP", icon="🧮")

footer_html = (
    '<div class="footer-note">'
    "Dados: bigmacindex.com API (bigmacindex.com/api) · "
    "Fallback offline: The Economist Big Mac Index · "
    "Uso educacional — não constitui recomendação de investimento."
    "</div>"
)
st.markdown(footer_html, unsafe_allow_html=True)

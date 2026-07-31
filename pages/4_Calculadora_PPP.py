"""Página: Calculadora de Paridade do Poder de Compra (PPP) usando o Big Mac Index."""

from __future__ import annotations

import streamlit as st

from src.data_loader import load_countries_df
from src.styling import load_css

st.set_page_config(page_title="Calculadora PPP | Big Mac Index", page_icon="🧮", layout="wide")
load_css()

st.title("🧮 Calculadora de Paridade do Poder de Compra")
st.caption(
    "Converta um valor de um país para outro usando a taxa de câmbio implícita "
    "pelo preço do Big Mac, e compare com a taxa de câmbio de mercado."
)

df = load_countries_df()
options = (df["flag"] + " " + df["name"]).tolist()
code_by_label = dict(zip(options, df["code"]))

col1, col2, col3 = st.columns([2, 1, 2])

with col1:
    origin_label = st.selectbox("País de origem", options, index=options.index(
        [o for o in options if "United States" in o][0]
    ))
with col3:
    dest_label = st.selectbox("País de destino", options, index=options.index(
        [o for o in options if "Japan" in o][0]
    ) if any("Japan" in o for o in options) else 0)
with col2:
    st.markdown("<div style='text-align:center; padding-top:2rem;'>➡️</div>", unsafe_allow_html=True)

amount = st.number_input("Valor a converter (na moeda do país de origem)", min_value=0.0, value=100.0, step=10.0)

origin = df.loc[df["code"] == code_by_label[origin_label]].iloc[0]
dest = df.loc[df["code"] == code_by_label[dest_label]].iloc[0]

# Taxa implícita pelo Big Mac: quantas unidades da moeda de destino equivalem
# a 1 unidade da moeda de origem, com base na paridade de poder de compra do Big Mac.
implied_rate = dest["local_price"] / origin["local_price"]
market_rate = dest["dollar_ex"] / origin["dollar_ex"]

converted_ppp = amount * implied_rate
converted_market = amount * market_rate

st.divider()

c1, c2 = st.columns(2)
with c1:
    st.metric(
        f"Conversão pela PPP do Big Mac ({dest['currency_code']})",
        f"{dest['currency_symbol']} {converted_ppp:,.2f}",
    )
    st.caption("Quanto o valor 'deveria' equivaler, se as moedas estivessem em paridade de poder de compra.")
with c2:
    st.metric(
        f"Conversão pela taxa de câmbio de mercado ({dest['currency_code']})",
        f"{dest['currency_symbol']} {converted_market:,.2f}",
    )
    st.caption("Quanto o valor equivale hoje, usando a taxa de câmbio efetiva do dataset.")

gap_percent = ((market_rate - implied_rate) / implied_rate) * 100 if implied_rate else 0
st.info(
    f"A taxa de câmbio de mercado está **{abs(gap_percent):.1f}% "
    f"{'acima' if gap_percent > 0 else 'abaixo'}** da taxa implícita pela paridade do Big Mac. "
    f"Isso sugere que a moeda de **{dest['name']}** está "
    f"{'subvalorizada' if gap_percent > 0 else 'sobrevalorizada'} frente à de **{origin['name']}**, "
    "segundo esta metodologia."
)

with st.expander("Como funciona esse cálculo?"):
    st.markdown(
        """
        1. Pegamos o preço local do Big Mac em cada país (na moeda local).
        2. A **taxa implícita PPP** é `preço_destino / preço_origem` — ou seja,
           quantas unidades da moeda de destino comprariam o mesmo Big Mac que
           uma unidade da moeda de origem compra em seu próprio país.
        3. Comparamos essa taxa implícita com a **taxa de câmbio de mercado**
           real entre as duas moedas.
        4. A diferença percentual entre as duas taxas é uma estimativa de
           quanto uma moeda está super ou subvalorizada frente à outra —
           a essência da metodologia do Big Mac Index criada pela *The Economist*.
        """
    )

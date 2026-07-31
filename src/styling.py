"""
styling.py
----------
Funções utilitárias para injetar o CSS customizado (assets/style.css)
e montar os "cartões" de indicadores (KPIs) do topo do dashboard.
"""

from __future__ import annotations

from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
CSS_PATH = BASE_DIR / "assets" / "style.css"


def load_css(path: Path = CSS_PATH) -> None:
    """Lê o arquivo .css e injeta no app via markdown/unsafe_allow_html."""
    if not path.exists():
        return
    with open(path, encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str | None = None, help_text: str | None = None) -> str:
    """Monta o HTML de um cartão de indicador (KPI) estilizado."""
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    help_html = f'<div class="kpi-help">{help_text}</div>' if help_text else ""
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
        {help_html}
    </div>
    """


def render_kpi_row(cards_html: list[str]) -> None:
    """Renderiza uma linha de cartões KPI lado a lado."""
    row_html = '<div class="kpi-row">' + "".join(cards_html) + "</div>"
    st.markdown(row_html, unsafe_allow_html=True)

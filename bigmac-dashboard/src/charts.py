"""
charts.py
---------
Gráficos auxiliares (barras, linhas, dispersão) usados nas páginas
de Rankings e Tendências Históricas.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def ranking_bar_chart(df: pd.DataFrame, base_country: str = "United States") -> go.Figure:
    """Gráfico de barras horizontal comparando preços, com cor por acima/abaixo da base."""
    plot_df = df.sort_values("price_usd", ascending=True).copy()
    plot_df["color"] = plot_df["diff_percent"].apply(
        lambda v: "Mais caro que a base" if v >= 0 else "Mais barato que a base"
    )
    fig = px.bar(
        plot_df,
        x="price_usd",
        y="name",
        orientation="h",
        color="color",
        color_discrete_map={
            "Mais caro que a base": "#e74c3c",
            "Mais barato que a base": "#2ecc71",
        },
        labels={"price_usd": "Preço (US$)", "name": "País", "color": ""},
        hover_data={"diff_percent": ":.1f"},
    )
    fig.update_layout(
        height=max(500, 18 * len(plot_df)),
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f5f5f5"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def extremes_bar_chart(cheapest: pd.DataFrame, priciest: pd.DataFrame) -> go.Figure:
    """Gráfico comparando os países mais baratos vs. mais caros lado a lado."""
    combined = pd.concat(
        [
            cheapest.assign(group="Mais baratos"),
            priciest.assign(group="Mais caros"),
        ]
    )
    fig = px.bar(
        combined,
        x="price_usd",
        y="name",
        color="group",
        orientation="h",
        color_discrete_map={"Mais baratos": "#2ecc71", "Mais caros": "#e74c3c"},
        labels={"price_usd": "Preço (US$)", "name": "", "group": ""},
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f5f5f5"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=500,
    )
    fig.update_yaxes(categoryorder="total ascending")
    return fig


def historical_line_chart(hist_df: pd.DataFrame, countries: list[str]) -> go.Figure:
    """Linha do tempo de preços (USD) para os países selecionados."""
    plot_df = hist_df[hist_df["name"].isin(countries)]
    fig = px.line(
        plot_df,
        x="year",
        y="price_usd",
        color="name",
        markers=True,
        labels={"year": "Ano", "price_usd": "Preço (US$)", "name": "País"},
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f5f5f5"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=480,
    )
    return fig


def region_box_plot(df: pd.DataFrame, region_labels: dict[str, str]) -> go.Figure:
    """Distribuição de preços por região (boxplot)."""
    plot_df = df.copy()
    plot_df["region_pt"] = plot_df["region"].map(region_labels).fillna(plot_df["region"])
    fig = px.box(
        plot_df,
        x="region_pt",
        y="price_usd",
        color="region_pt",
        points="all",
        labels={"region_pt": "Região", "price_usd": "Preço (US$)"},
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f5f5f5"),
        showlegend=False,
        height=460,
    )
    return fig

"""
maps.py
-------
Construção dos mapas interativos (Plotly) usados no dashboard:
- Mapa coroplético mundial por preço do Big Mac (USD)
- Mapa coroplético por variação percentual (sobre/subvalorização)
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


def build_price_choropleth(df: pd.DataFrame, color_scale: str = "YlOrRd") -> go.Figure:
    """Mapa mundial colorido pelo preço do Big Mac em USD."""
    fig = go.Figure(
        data=go.Choropleth(
            locations=df["code"],
            z=df["price_usd"],
            locationmode="ISO-3",
            colorscale=color_scale,
            marker_line_color="#1a1a1a",
            marker_line_width=0.5,
            colorbar_title="US$",
            hovertemplate=(
                "<b>%{customdata[0]} %{text}</b><br>"
                "Preço: US$ %{z:.2f}<br>"
                "vs. Base: %{customdata[1]:+.1f}%<extra></extra>"
            ),
            text=df["name"],
            customdata=df[["flag", "diff_percent"]],
        )
    )
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#444",
            projection_type="natural earth",
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f5f5f5"),
        height=520,
    )
    return fig


def build_diff_choropleth(df: pd.DataFrame, diff_col: str = "diff_percent") -> go.Figure:
    """Mapa mundial colorido pela variação % em relação ao país-base (verde=barato, vermelho=caro)."""
    max_abs = max(abs(df[diff_col].min()), abs(df[diff_col].max()))
    fig = go.Figure(
        data=go.Choropleth(
            locations=df["code"],
            z=df[diff_col],
            locationmode="ISO-3",
            colorscale="RdYlGn_r",
            zmin=-max_abs,
            zmax=max_abs,
            marker_line_color="#1a1a1a",
            marker_line_width=0.5,
            colorbar_title="% vs base",
            hovertemplate=(
                "<b>%{customdata[0]} %{text}</b><br>"
                "Diferença: %{z:+.1f}%<extra></extra>"
            ),
            text=df["name"],
            customdata=df[["flag"]],
        )
    )
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#444",
            projection_type="natural earth",
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f5f5f5"),
        height=520,
    )
    return fig

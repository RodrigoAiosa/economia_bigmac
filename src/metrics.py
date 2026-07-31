"""
metrics.py
----------
Cálculos e indicadores derivados do Big Mac Index:
- conversão de base de comparação (USD, EUR, GBP, JPY, CNY...)
- estatísticas agregadas (médias, extremos, dispersão)
- classificação de valorização/desvalorização cambial
"""

from __future__ import annotations

import pandas as pd


def recompute_base_currency(df: pd.DataFrame, base_code: str) -> pd.DataFrame:
    """
    Recalcula 'price_usd' e 'diff_percent' usando outro país como referência
    (ex.: comparar tudo contra o preço do Big Mac na Zona do Euro).

    O dataset original sempre usa USD como base. Para trocar a base,
    convertemos todos os preços para a "moeda" do país selecionado,
    tratando seu price_usd como o novo referencial 1:1.
    """
    if base_code not in df["code"].values:
        return df

    base_row = df.loc[df["code"] == base_code].iloc[0]
    base_price = base_row["price_usd"]

    out = df.copy()
    out["price_base"] = out["price_usd"] / base_price
    out["diff_percent_base"] = ((out["price_usd"] - base_price) / base_price) * 100
    out["base_country"] = base_row["name"]
    out["base_currency"] = base_row["currency_code"]
    return out


def summary_stats(df: pd.DataFrame) -> dict[str, float | str]:
    """Estatísticas resumidas para os cartões de indicadores no topo do dashboard."""
    most_expensive = df.loc[df["price_usd"].idxmax()]
    cheapest = df.loc[df["price_usd"].idxmin()]
    return {
        "n_countries": len(df),
        "avg_price": df["price_usd"].mean(),
        "median_price": df["price_usd"].median(),
        "std_price": df["price_usd"].std(),
        "most_expensive_name": f"{most_expensive['flag']} {most_expensive['name']}",
        "most_expensive_price": most_expensive["price_usd"],
        "cheapest_name": f"{cheapest['flag']} {cheapest['name']}",
        "cheapest_price": cheapest["price_usd"],
        "spread_ratio": most_expensive["price_usd"] / cheapest["price_usd"],
        "n_overvalued": int((df["diff_percent"] > 0).sum()),
        "n_undervalued": int((df["diff_percent"] < 0).sum()),
    }


def valuation_label(diff_percent: float) -> str:
    """Classifica o grau de sobre/subvalorização cambial implícita pelo índice."""
    if diff_percent >= 20:
        return "Muito sobrevalorizada"
    if diff_percent >= 5:
        return "Sobrevalorizada"
    if diff_percent > -5:
        return "Próxima da paridade"
    if diff_percent > -30:
        return "Subvalorizada"
    return "Muito subvalorizada"


def add_valuation_column(df: pd.DataFrame, diff_col: str = "diff_percent") -> pd.DataFrame:
    out = df.copy()
    out["valuation"] = out[diff_col].apply(valuation_label)
    return out


def top_n(df: pd.DataFrame, n: int = 10, ascending: bool = False) -> pd.DataFrame:
    """Retorna os N países mais caros (ascending=False) ou mais baratos (ascending=True)."""
    return df.sort_values("price_usd", ascending=ascending).head(n)

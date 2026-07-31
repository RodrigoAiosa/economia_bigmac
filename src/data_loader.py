"""
data_loader.py
--------------
Responsável por carregar, validar e cachear os dados do Big Mac Index
(dados oficiais do The Economist, replicados em data/countries.json)
e o histórico ilustrativo usado na página de tendências.

Fonte oficial dos dados: https://github.com/TheEconomist/big-mac-data
Réplica utilizada como referência de layout: https://bigmacindex.app/
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
COUNTRIES_JSON = DATA_DIR / "countries.json"
HISTORICAL_CSV = DATA_DIR / "historical_prices.csv"


@st.cache_data(show_spinner=False)
def load_raw_json() -> dict[str, Any]:
    """Lê o arquivo countries.json do disco."""
    with open(COUNTRIES_JSON, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_countries_df() -> pd.DataFrame:
    """
    Retorna um DataFrame com uma linha por país, contendo:
    rank, code (ISO-3), slug, name, flag, region, currency_code,
    currency_symbol, local_price, dollar_ex, price_usd, diff_percent.
    """
    raw = load_raw_json()
    rows = []
    for c in raw["countries"]:
        rows.append(
            {
                "rank": c["rank"],
                "code": c["code"],
                "slug": c["slug"],
                "name": c["name"],
                "flag": c["flag"],
                "region": c["region"],
                "currency_code": c["currency"]["code"],
                "currency_symbol": c["currency"]["symbol"],
                "local_price": c["local_price"],
                "dollar_ex": c["dollar_ex"],
                "price_usd": c["price_usd"],
                "diff_percent": c["diff_percent"],
            }
        )
    df = pd.DataFrame(rows).sort_values("rank").reset_index(drop=True)
    return df


@st.cache_data(show_spinner=False)
def load_meta() -> dict[str, Any]:
    """Retorna os metadados do dataset (data de atualização, país-base etc.)."""
    raw = load_raw_json()
    return raw["meta"]


@st.cache_data(show_spinner=False)
def load_historical_df() -> pd.DataFrame:
    """
    Carrega a série histórica (2010-2025) usada na página de tendências.

    Nota: esta série é ILUSTRATIVA, construída a partir do preço atual de
    cada país com uma trajetória plausível de crescimento. Para uma análise
    rigorosa, substitua data/historical_prices.csv pelos dados brutos e
    completos disponíveis em https://github.com/TheEconomist/big-mac-data
    """
    df = pd.read_csv(HISTORICAL_CSV)
    return df.sort_values(["code", "year"]).reset_index(drop=True)


def region_label_map() -> dict[str, str]:
    """Mapeia os códigos internos de região para rótulos em português."""
    return {
        "europe": "Europa",
        "americas": "Américas",
        "asia": "Ásia",
        "oceania": "Oceania",
        "middle-east": "Oriente Médio",
        "africa": "África",
    }

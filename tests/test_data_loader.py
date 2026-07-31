"""
Testes simples para src/data_loader.py e src/metrics.py.
Executar com: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json

import pandas as pd

from src.data_loader import DATA_DIR


def _load_countries_df_no_cache() -> pd.DataFrame:
    """Versão sem cache do streamlit, para rodar em ambiente de teste puro."""
    with open(DATA_DIR / "countries.json", encoding="utf-8") as f:
        raw = json.load(f)
    rows = []
    for c in raw["countries"]:
        rows.append(
            {
                "rank": c["rank"],
                "code": c["code"],
                "name": c["name"],
                "region": c["region"],
                "price_usd": c["price_usd"],
                "diff_percent": c["diff_percent"],
            }
        )
    return pd.DataFrame(rows)


def test_countries_json_exists():
    assert (DATA_DIR / "countries.json").exists()


def test_countries_df_has_expected_columns():
    df = _load_countries_df_no_cache()
    expected = {"rank", "code", "name", "region", "price_usd", "diff_percent"}
    assert expected.issubset(set(df.columns))


def test_countries_df_not_empty():
    df = _load_countries_df_no_cache()
    assert len(df) > 0


def test_usa_is_base_country():
    df = _load_countries_df_no_cache()
    usa_row = df.loc[df["code"] == "USA"].iloc[0]
    assert usa_row["diff_percent"] == 0


def test_price_usd_is_positive():
    df = _load_countries_df_no_cache()
    assert (df["price_usd"] > 0).all()

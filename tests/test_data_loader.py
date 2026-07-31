"""
Testes unitários para src/data_loader.py, src/enrich.py e src/api_client.py.

Estes testes rodam sem API key configurada, portanto exercitam
principalmente o caminho de fallback (dataset local offline) — que é
justamente o comportamento que garante que o dashboard nunca quebre.

Executar com: pytest
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import FALLBACK_COUNTRIES_JSON, FALLBACK_HISTORICAL_CSV, _df_from_fallback
from src.enrich import currency_symbol_for, flag_emoji, iso2_to_iso3, region_for, slugify


def test_fallback_countries_json_exists():
    assert FALLBACK_COUNTRIES_JSON.exists()


def test_fallback_historical_csv_exists():
    assert FALLBACK_HISTORICAL_CSV.exists()


def test_fallback_df_has_expected_columns():
    df = _df_from_fallback()
    expected = {"rank", "code", "iso2", "name", "region", "currency_code", "price_usd", "diff_percent"}
    assert expected.issubset(set(df.columns))


def test_fallback_df_not_empty():
    df = _df_from_fallback()
    assert len(df) > 0


def test_usa_is_base_country_in_fallback():
    df = _df_from_fallback()
    usa_row = df.loc[df["code"] == "USA"].iloc[0]
    assert usa_row["diff_percent"] == 0


def test_price_usd_is_positive_in_fallback():
    df = _df_from_fallback()
    assert (df["price_usd"] > 0).all()


# ---------------------------------------------------------------------------
# src/enrich.py
# ---------------------------------------------------------------------------


def test_iso2_to_iso3():
    assert iso2_to_iso3("ch") == "CHE"
    assert iso2_to_iso3("br") == "BRA"
    assert iso2_to_iso3("us") == "USA"


def test_flag_emoji_switzerland():
    assert flag_emoji("ch") == "🇨🇭"


def test_flag_emoji_invalid_code_returns_placeholder():
    assert flag_emoji("xx-invalid") == "🏳️"


def test_region_for_known_countries():
    assert region_for("de") == "europe"
    assert region_for("br") == "americas"
    assert region_for("jp") == "asia"
    assert region_for("au") == "oceania"
    assert region_for("za") == "africa"


def test_region_for_middle_east_override():
    assert region_for("ae") == "middle-east"
    assert region_for("sa") == "middle-east"


def test_currency_symbol_known_and_unknown():
    assert currency_symbol_for("USD") == "$"
    assert currency_symbol_for("EUR") == "€"
    assert currency_symbol_for("XYZ") == "XYZ"


def test_slugify():
    assert slugify("United States") == "united-states"
    assert slugify("Costa Rica") == "costa-rica"

"""
data_loader.py
--------------
Camada de dados do dashboard. Fonte primária: a API pública do
bigmacindex.com (https://bigmacindex.com/api). Se nenhuma API key estiver
configurada, ou se a API estiver indisponível, o app cai automaticamente
para um dataset local de fallback (data/fallback_countries.json), que
reflete uma captura do The Economist Big Mac Index — para que o dashboard
nunca fique fora do ar.

Todas as funções públicas devolvem os dados já normalizados no mesmo
formato de DataFrame, independentemente da fonte usada, para que o resto
do app (páginas, gráficos, mapas) não precise saber de onde os dados vieram.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

import pandas as pd
import streamlit as st

from src import api_client
from src.enrich import currency_symbol_for, flag_emoji, iso2_to_iso3, region_for, slugify

import pycountry

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FALLBACK_COUNTRIES_JSON = DATA_DIR / "fallback_countries.json"
FALLBACK_HISTORICAL_CSV = DATA_DIR / "fallback_historical_prices.csv"

DataSource = Literal["api", "fallback"]


def _iso3_to_iso2(code_iso3: str) -> str:
    """Converte ISO alpha-3 (ex.: 'CHE') em ISO alpha-2 (ex.: 'ch'). Usado só no fallback."""
    try:
        country = pycountry.countries.get(alpha_3=code_iso3.upper())
        if country:
            return country.alpha_2.lower()
    except (LookupError, AttributeError):
        pass
    return code_iso3.lower()[:2]


# ---------------------------------------------------------------------------
# Países (snapshot atual) — /latest da API, com fallback local
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def _load_fallback_raw() -> dict[str, Any]:
    with open(FALLBACK_COUNTRIES_JSON, encoding="utf-8") as f:
        return json.load(f)


def _df_from_fallback() -> pd.DataFrame:
    raw = _load_fallback_raw()
    rows = []
    for c in raw["countries"]:
        rows.append(
            {
                "rank": c["rank"],
                "code": c["code"],
                "iso2": _iso3_to_iso2(c["code"]),
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
    return pd.DataFrame(rows).sort_values("rank").reset_index(drop=True)


def _df_from_api(payload: dict[str, Any]) -> pd.DataFrame:
    """Normaliza a resposta de GET /latest no mesmo esquema de colunas do fallback."""
    rows = []
    for c in payload.get("countries", []):
        iso2 = c.get("countryId") or c.get("countryCode", "")
        currency_code = c.get("currency", "")
        local_price = c.get("localPrice")
        usd_price = c.get("usdPrice")
        market_fx = c.get("marketFxRate")
        diff_percent = c.get("valuationPct", c.get("rawPppIndex", 0))

        rows.append(
            {
                "code": iso2_to_iso3(iso2),
                "iso2": iso2.lower(),
                "slug": slugify(c.get("countryName", iso2)),
                "name": c.get("countryName", iso2.upper()),
                "flag": flag_emoji(iso2),
                "region": region_for(iso2),
                "currency_code": currency_code,
                "currency_symbol": currency_symbol_for(currency_code),
                "local_price": local_price,
                "dollar_ex": market_fx,
                "price_usd": usd_price,
                "diff_percent": diff_percent,
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        raise api_client.ApiError("A API retornou uma lista de países vazia.")
    df = df.sort_values("price_usd", ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    return df


@st.cache_data(show_spinner=False)
def load_countries_df() -> pd.DataFrame:
    """
    Retorna o DataFrame com uma linha por país (rank, code ISO-3, slug, name,
    flag, region, currency_code, currency_symbol, local_price, dollar_ex,
    price_usd, diff_percent).

    Tenta a API ao vivo primeiro; em caso de falta de chave, erro ou
    indisponibilidade, cai para o dataset local de fallback.
    """
    try:
        payload = api_client.get_latest()
        return _df_from_api(payload)
    except api_client.ApiError:
        return _df_from_fallback()


@st.cache_data(show_spinner=False)
def get_data_source() -> DataSource:
    """
    Indica qual fonte de dados está realmente em uso ('api' ou 'fallback'),
    para exibir um aviso na interface. Não lança exceção.
    """
    try:
        api_client.get_latest()
        return "api"
    except api_client.ApiError:
        return "fallback"


@st.cache_data(show_spinner=False)
def load_meta() -> dict[str, Any]:
    """Metadados do dataset (data de atualização, país-base, nº de países, fonte)."""
    source = get_data_source()
    if source == "api":
        try:
            payload = api_client.get_latest()
            df = load_countries_df()
            return {
                "data_date": payload.get("date", "—"),
                "base_country": "us",
                "base_price_usd": payload.get("usBasePrice"),
                "source": "bigmacindex.com API (live)",
                "source_url": "https://bigmacindex.com/api",
                "total_countries": len(df),
            }
        except api_client.ApiError:
            pass

    raw = _load_fallback_raw()
    meta = dict(raw["meta"])
    meta["source"] = "The Economist Big Mac Index (offline snapshot)"
    return meta


# ---------------------------------------------------------------------------
# Histórico — /history da API (por país), com fallback local por CSV
# ---------------------------------------------------------------------------


@st.cache_data(show_spinner=False)
def load_historical_df(countries_iso2: dict[str, str], days: int = 365) -> pd.DataFrame:
    """
    Monta um DataFrame histórico (year/date, code, name, region, price_usd)
    para os países selecionados, chamando GET /history por país.

    countries_iso2: dict {nome_exibido: codigo_iso2}, ex.: {"Switzerland": "ch"}.
    Países cuja chamada à API falhar (sem chave, erro, etc.) usam o CSV de
    fallback para aquele país específico, se disponível ali.
    """
    frames = []
    fallback_df = None

    for name, iso2 in countries_iso2.items():
        if iso2:
            try:
                payload = api_client.get_history(country=iso2, days=days)
                rows = [
                    {
                        "date": d["date"],
                        "name": payload.get("countryName", name),
                        "code": iso2_to_iso3(iso2),
                        "price_usd": d["usdPrice"],
                    }
                    for d in payload.get("data", [])
                ]
                if rows:
                    frames.append(pd.DataFrame(rows))
                    continue
            except api_client.ApiError:
                pass

        # Fallback: tenta achar este país no CSV local ilustrativo
        if fallback_df is None:
            fallback_df = pd.read_csv(FALLBACK_HISTORICAL_CSV)
        sub = fallback_df[fallback_df["name"] == name].copy()
        if not sub.empty:
            sub["date"] = sub["year"].astype(str) + "-01-01"
            frames.append(sub[["date", "name", "code", "price_usd"]])

    if not frames:
        return pd.DataFrame(columns=["date", "name", "code", "price_usd"])

    result = pd.concat(frames, ignore_index=True)
    result["date"] = pd.to_datetime(result["date"])
    return result.sort_values(["name", "date"]).reset_index(drop=True)


@st.cache_data(show_spinner=False)
def load_fallback_country_list() -> list[str]:
    """Lista de nomes de país disponíveis no CSV histórico de fallback (para o seletor da UI)."""
    df = pd.read_csv(FALLBACK_HISTORICAL_CSV)
    return sorted(df["name"].unique())


def region_label_map() -> dict[str, str]:
    """Mapeia os códigos internos de região para rótulos em português."""
    return {
        "europe": "Europa",
        "americas": "Américas",
        "asia": "Ásia",
        "oceania": "Oceania",
        "middle-east": "Oriente Médio",
        "africa": "África",
        "other": "Outros",
    }

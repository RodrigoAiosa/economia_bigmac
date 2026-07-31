"""
api_client.py
--------------
Cliente para a API pública do bigmacindex.com
(https://bigmacindex.com/api).

Base URL: https://bigmacindex.com/api/v1/burger

Endpoints usados neste projeto:
    /countries    -> GET  sem chave           -> diretório de países
    /market/current -> GET sem chave          -> status do pipeline de dados
    /latest       -> GET  requer chave        -> snapshot de preços por país
    /history      -> GET  requer chave        -> histórico diário por país
    /rankings     -> GET  requer chave        -> ranking por métrica
    /currencies   -> GET  requer chave        -> câmbio + sinal de valorização
    /fx/history   -> GET  requer chave        -> histórico cambial
    /global       -> GET  requer chave        -> tendência global

Autenticação:
    Authorization: Bearer <BIGMAC_API_KEY>

A chave é lida, em ordem de prioridade, de:
    1. st.secrets["BIGMAC_API_KEY"]           (.streamlit/secrets.toml)
    2. variável de ambiente BIGMAC_API_KEY

Se nenhuma chave estiver configurada, as funções que exigem autenticação
levantam ApiAuthError — e a camada de dados (data_loader.py) trata esse
erro caindo para o dataset local de fallback.
"""

from __future__ import annotations

import os
from typing import Any

import requests
import streamlit as st

BASE_URL = "https://bigmacindex.com/api/v1/burger"
TIMEOUT_SECONDS = 10
CACHE_TTL_SECONDS = 60 * 30  # 30 minutos — respeita o limite de 500 req/dia do plano free


class ApiError(Exception):
    """Erro genérico de comunicação com a API do Big Mac Index."""


class ApiAuthError(ApiError):
    """Levantado quando um endpoint exige chave e nenhuma chave válida foi encontrada."""


class ApiRateLimitError(ApiError):
    """Levantado quando o limite de requisições por minuto/dia foi excedido (HTTP 429)."""


def get_api_key() -> str | None:
    """
    Retorna a API key configurada, ou None se não houver nenhuma.
    Prioridade: st.secrets > variável de ambiente.
    """
    try:
        key = st.secrets.get("BIGMAC_API_KEY")
        if key:
            return str(key)
    except Exception:
        # st.secrets levanta exceção se secrets.toml não existir — está tudo bem, seguimos.
        pass
    return os.environ.get("BIGMAC_API_KEY")


def has_api_key() -> bool:
    return bool(get_api_key())


def _request(path: str, params: dict[str, Any] | None = None, require_key: bool = True) -> dict[str, Any]:
    """
    Faz uma requisição GET para a API e retorna o JSON já decodificado.
    Lança ApiAuthError / ApiRateLimitError / ApiError conforme o caso.
    """
    headers = {}
    if require_key:
        key = get_api_key()
        if not key:
            raise ApiAuthError(
                "Este endpoint exige uma API key gratuita. "
                "Crie a sua em https://bigmacindex.com/signup e configure "
                "BIGMAC_API_KEY em .streamlit/secrets.toml ou como variável de ambiente."
            )
        headers["Authorization"] = f"Bearer {key}"

    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, params=params or {}, headers=headers, timeout=TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise ApiError(f"Falha de rede ao chamar {url}: {exc}") from exc

    if response.status_code == 401:
        raise ApiAuthError("API key ausente ou inválida (HTTP 401).")
    if response.status_code == 429:
        raise ApiRateLimitError("Limite de requisições excedido (HTTP 429). Tente novamente em instantes.")
    if response.status_code == 404:
        raise ApiError(f"Recurso não encontrado (HTTP 404) em {url}.")
    if not response.ok:
        raise ApiError(f"A API retornou HTTP {response.status_code} para {url}.")

    try:
        return response.json()
    except ValueError as exc:
        raise ApiError(f"Resposta inválida (não é JSON) de {url}.") from exc


# ---------------------------------------------------------------------------
# Endpoints públicos (sem chave)
# ---------------------------------------------------------------------------


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def get_countries() -> dict[str, Any]:
    """GET /countries — diretório de países cobertos (sem autenticação)."""
    return _request("/countries", require_key=False)


@st.cache_data(ttl=60 * 5, show_spinner=False)
def get_market_status() -> dict[str, Any]:
    """GET /market/current — status do pipeline de dados (sem autenticação)."""
    return _request("/market/current", require_key=False)


# ---------------------------------------------------------------------------
# Endpoints autenticados (exigem API key)
# ---------------------------------------------------------------------------


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def get_latest(country: str | None = None, item: str = "bigmac") -> dict[str, Any]:
    """GET /latest — snapshot mais recente de preços/PPP para todos os países (ou um único)."""
    params: dict[str, Any] = {"item": item}
    if country:
        params["country"] = country
    return _request("/latest", params=params, require_key=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def get_history(country: str = "us", days: int = 30, item: str = "bigmac") -> dict[str, Any]:
    """GET /history — histórico diário de preços para um país."""
    params = {"country": country, "days": days, "item": item}
    return _request("/history", params=params, require_key=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def get_rankings(
    metric: str = "raw_ppp_index", order: str = "desc", limit: int = 50, item: str = "bigmac"
) -> dict[str, Any]:
    """GET /rankings — países ranqueados por uma métrica escolhida."""
    params = {"metric": metric, "order": order, "limit": limit, "item": item}
    return _request("/rankings", params=params, require_key=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def get_currencies(item: str = "bigmac") -> dict[str, Any]:
    """GET /currencies — câmbio de cada moeda vs. USD, com o sinal de valorização do Big Mac."""
    return _request("/currencies", params={"item": item}, require_key=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def get_fx_history(currency: str, days: int = 90) -> dict[str, Any]:
    """GET /fx/history — histórico cambial diário de uma moeda vs. USD."""
    return _request("/fx/history", params={"currency": currency, "days": days}, require_key=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def get_global(days: int = 365, item: str = "bigmac") -> dict[str, Any]:
    """GET /global — série da tendência global (preço médio + benchmark BMDI)."""
    return _request("/global", params={"days": days, "item": item}, require_key=True)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def get_compare(countries: list[str], item: str = "bigmac") -> dict[str, Any]:
    """GET /compare — compara 2 a 5 países (endpoint público, com preview limitado sem login)."""
    return _request("/compare", params={"countries": ",".join(countries), "item": item}, require_key=False)

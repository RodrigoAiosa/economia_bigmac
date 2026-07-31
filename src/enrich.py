"""
enrich.py
---------
Funções auxiliares para enriquecer os dados vindos da API do bigmacindex.com,
que trabalha com códigos ISO alpha-2 (ex.: "CH") e não traz região, bandeira
ou símbolo de moeda prontos. Este módulo deriva tudo isso localmente, sem
precisar de chamadas extras à API.
"""

from __future__ import annotations

import re

import pycountry
import pycountry_convert as pc

# Países onde a classificação geopolítica usual como "Oriente Médio" difere
# do continente geográfico "Ásia" retornado por pycountry_convert.
_MIDDLE_EAST_ISO2 = {
    "AE", "BH", "IL", "IQ", "IR", "JO", "KW", "LB", "OM", "PS", "QA", "SA", "SY", "YE",
}

_CONTINENT_TO_REGION = {
    "EU": "europe",
    "AS": "asia",
    "NA": "americas",
    "SA": "americas",
    "AF": "africa",
    "OC": "oceania",
}

# Símbolos de moeda mais comuns entre os países cobertos pelo Big Mac Index.
# Para moedas fora desta lista, usamos o próprio código ISO 4217 como símbolo.
_CURRENCY_SYMBOLS = {
    "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", "CNY": "¥", "CHF": "CHF",
    "BRL": "R$", "ARS": "$", "AUD": "$", "CAD": "$", "NZD": "$", "SGD": "S$",
    "HKD": "HK$", "INR": "₹", "KRW": "₩", "MXN": "$", "TRY": "₺", "SEK": "kr",
    "NOK": "kr", "DKK": "kr", "PLN": "zł", "THB": "฿", "VND": "₫", "ILS": "₪",
    "AED": "AED", "SAR": "SR", "TWD": "NT$", "PHP": "₱", "IDR": "Rp", "MYR": "RM",
    "ZAR": "R", "EGP": "E£", "CLP": "$", "COP": "$", "PEN": "S/", "CZK": "Kč",
    "HUF": "Ft", "RON": "lei", "UAH": "₴",
}


def iso2_to_iso3(code: str) -> str:
    """
    Converte um código ISO alpha-2 (ex.: 'ch') em ISO alpha-3 (ex.: 'CHE'),
    necessário para o mapa coroplético do Plotly (locationmode='ISO-3').
    Retorna o próprio código em maiúsculas se não for encontrado.
    """
    try:
        country = pycountry.countries.get(alpha_2=code.upper())
        if country:
            return country.alpha_3
    except (LookupError, AttributeError):
        pass
    return code.upper()


def region_for(code: str) -> str:
    """
    Classifica um país (ISO alpha-2) em uma das regiões usadas no dashboard:
    europe, americas, asia, oceania, middle-east, africa.
    """
    code_upper = code.upper()
    if code_upper in _MIDDLE_EAST_ISO2:
        return "middle-east"
    try:
        continent_code = pc.country_alpha2_to_continent_code(code_upper)
        return _CONTINENT_TO_REGION.get(continent_code, "other")
    except KeyError:
        return "other"


def flag_emoji(code: str) -> str:
    """
    Gera o emoji de bandeira a partir de um código ISO alpha-2, combinando
    os dois "Regional Indicator Symbols" correspondentes às letras do código.
    Ex.: 'ch' -> 🇨🇭. Não depende de nenhuma lista externa de bandeiras.
    """
    code_upper = code.upper()
    if len(code_upper) != 2 or not code_upper.isalpha():
        return "🏳️"
    return "".join(chr(0x1F1E6 + ord(letter) - ord("A")) for letter in code_upper)


def currency_symbol_for(currency_code: str) -> str:
    """Retorna o símbolo comum de uma moeda, ou o próprio código ISO 4217 se desconhecido."""
    return _CURRENCY_SYMBOLS.get(currency_code.upper(), currency_code.upper())


def slugify(name: str) -> str:
    """Gera um slug simples e amigável para URL a partir do nome do país."""
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")

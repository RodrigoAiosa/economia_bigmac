/*
 * GET /api/latest
 *
 * Busca o snapshot mais recente em GET /latest do bigmacindex.com e devolve
 * os dados no mesmo formato de data/fallback_countries.json, para que a
 * página use uma única estrutura, venha o dado da API ou do arquivo offline.
 */

const { callApi, lookup, flagEmoji, currencySymbol, sendJson, sendError } = require("./_shared");

const num = v => (v === null || v === undefined || v === "" ? null : Number(v));

module.exports = async function handler(req, res) {
    try {
        const payload = await callApi("/latest", { item: "bigmac" });

        const countries = (payload.countries || [])
            .map(c => {
                const iso2 = String(c.countryId || c.countryCode || "").toLowerCase();
                const [code, region] = lookup(iso2);
                const currency = c.currency || "";
                return {
                    code,
                    iso2,
                    name: c.countryName || iso2.toUpperCase(),
                    flag: flagEmoji(iso2),
                    region,
                    currency: { code: currency, symbol: currencySymbol(currency) },
                    local_price: num(c.localPrice),
                    dollar_ex: num(c.marketFxRate),
                    price_usd: num(c.usdPrice),
                    diff_percent: num(c.valuationPct ?? c.rawPppIndex ?? 0)
                };
            })
            .filter(c => c.price_usd !== null && c.local_price !== null)
            .sort((a, b) => b.price_usd - a.price_usd)
            .map((c, i) => Object.assign({ rank: i + 1 }, c));

        if (!countries.length) {
            return sendJson(res, 502, { error: "A API retornou uma lista de países vazia." }, 0);
        }

        sendJson(res, 200, {
            meta: {
                source: "api",
                data_date: payload.date || null,
                base_country: (payload.metadata && payload.metadata.baseCountry) || "us",
                base_price_usd: num(payload.usBasePrice),
                total_countries: countries.length,
                fetched_at: new Date().toISOString()
            },
            countries
        }, 3600);
    } catch (err) {
        sendError(res, err);
    }
};

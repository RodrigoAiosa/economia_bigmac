/*
 * GET /api/history?country=ch&days=365
 *
 * Histórico diário de preços de um país, via GET /history do bigmacindex.com.
 * Os parâmetros são validados aqui para que a função não sirva de proxy
 * aberto para outros endpoints ou valores arbitrários.
 */

const { callApi, sendJson, sendError } = require("./_shared");

const ALLOWED_DAYS = new Set([30, 90, 180, 365]);

module.exports = async function handler(req, res) {
    try {
        const url = new URL(req.url, "http://localhost");
        const country = String(url.searchParams.get("country") || "").toLowerCase();
        const days = Number(url.searchParams.get("days") || 365);

        if (!/^[a-z]{2}$/.test(country)) {
            return sendJson(res, 400, { error: "Parâmetro 'country' deve ser um código ISO alpha-2 (ex.: ch)." }, 0);
        }
        if (!ALLOWED_DAYS.has(days)) {
            return sendJson(res, 400, { error: "Parâmetro 'days' deve ser 30, 90, 180 ou 365." }, 0);
        }

        const payload = await callApi("/history", { country, days, item: "bigmac" });
        const data = (payload.data || [])
            .filter(d => d && d.date && d.usdPrice !== null && d.usdPrice !== undefined)
            .map(d => ({ date: d.date, usd_price: Number(d.usdPrice), local_price: d.localPrice ?? null }))
            .sort((a, b) => (a.date < b.date ? -1 : 1));

        sendJson(res, 200, {
            country,
            name: payload.countryName || country.toUpperCase(),
            currency: payload.currency || null,
            days,
            data
        }, 3600);
    } catch (err) {
        sendError(res, err);
    }
};

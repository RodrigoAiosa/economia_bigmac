/*
 * Utilidades compartilhadas pelas funções da API (não vira endpoint: arquivos
 * com "_" no início são ignorados pela Vercel).
 *
 * A chave da API do bigmacindex.com é lida da variável de ambiente
 * BIGMAC_API_KEY, configurada no painel da Vercel. Ela nunca chega ao navegador.
 */

const BASE_URL = "https://bigmacindex.com/api/v1/burger";
const TIMEOUT_MS = 10000;

// ISO alpha-2 -> [ISO alpha-3, região do dashboard]. Gerado com pycountry +
// pycountry_convert, com a mesma regra de src/enrich.py (Oriente Médio separado).
const ISO = {"AW":["ABW","americas"],"AF":["AFG","asia"],"AO":["AGO","africa"],"AI":["AIA","americas"],"AX":["ALA","europe"],"AL":["ALB","europe"],"AD":["AND","europe"],"AE":["ARE","middle-east"],"AR":["ARG","americas"],"AM":["ARM","asia"],"AS":["ASM","oceania"],"AQ":["ATA","other"],"TF":["ATF","other"],"AG":["ATG","americas"],"AU":["AUS","oceania"],"AT":["AUT","europe"],"AZ":["AZE","asia"],"BI":["BDI","africa"],"BE":["BEL","europe"],"BJ":["BEN","africa"],"BQ":["BES","americas"],"BF":["BFA","africa"],"BD":["BGD","asia"],"BG":["BGR","europe"],"BH":["BHR","middle-east"],"BS":["BHS","americas"],"BA":["BIH","europe"],"BL":["BLM","americas"],"BY":["BLR","europe"],"BZ":["BLZ","americas"],"BM":["BMU","americas"],"BO":["BOL","americas"],"BR":["BRA","americas"],"BB":["BRB","americas"],"BN":["BRN","asia"],"BT":["BTN","asia"],"BV":["BVT","other"],"BW":["BWA","africa"],"CF":["CAF","africa"],"CA":["CAN","americas"],"CC":["CCK","asia"],"CH":["CHE","europe"],"CL":["CHL","americas"],"CN":["CHN","asia"],"CI":["CIV","africa"],"CM":["CMR","africa"],"CD":["COD","africa"],"CG":["COG","africa"],"CK":["COK","oceania"],"CO":["COL","americas"],"KM":["COM","africa"],"CV":["CPV","africa"],"CR":["CRI","americas"],"CU":["CUB","americas"],"CW":["CUW","americas"],"CX":["CXR","asia"],"KY":["CYM","americas"],"CY":["CYP","asia"],"CZ":["CZE","europe"],"DE":["DEU","europe"],"DJ":["DJI","africa"],"DM":["DMA","americas"],"DK":["DNK","europe"],"DO":["DOM","americas"],"DZ":["DZA","africa"],"EC":["ECU","americas"],"EG":["EGY","africa"],"ER":["ERI","africa"],"EH":["ESH","other"],"ES":["ESP","europe"],"EE":["EST","europe"],"ET":["ETH","africa"],"FI":["FIN","europe"],"FJ":["FJI","oceania"],"FK":["FLK","americas"],"FR":["FRA","europe"],"FO":["FRO","europe"],"FM":["FSM","oceania"],"GA":["GAB","africa"],"GB":["GBR","europe"],"GE":["GEO","asia"],"GG":["GGY","europe"],"GH":["GHA","africa"],"GI":["GIB","europe"],"GN":["GIN","africa"],"GP":["GLP","americas"],"GM":["GMB","africa"],"GW":["GNB","africa"],"GQ":["GNQ","africa"],"GR":["GRC","europe"],"GD":["GRD","americas"],"GL":["GRL","americas"],"GT":["GTM","americas"],"GF":["GUF","americas"],"GU":["GUM","oceania"],"GY":["GUY","americas"],"HK":["HKG","asia"],"HM":["HMD","other"],"HN":["HND","americas"],"HR":["HRV","europe"],"HT":["HTI","americas"],"HU":["HUN","europe"],"ID":["IDN","asia"],"IM":["IMN","europe"],"IN":["IND","asia"],"IO":["IOT","asia"],"IE":["IRL","europe"],"IR":["IRN","middle-east"],"IQ":["IRQ","middle-east"],"IS":["ISL","europe"],"IL":["ISR","middle-east"],"IT":["ITA","europe"],"JM":["JAM","americas"],"JE":["JEY","europe"],"JO":["JOR","middle-east"],"JP":["JPN","asia"],"KZ":["KAZ","asia"],"KE":["KEN","africa"],"KG":["KGZ","asia"],"KH":["KHM","asia"],"KI":["KIR","oceania"],"KN":["KNA","americas"],"KR":["KOR","asia"],"KW":["KWT","middle-east"],"LA":["LAO","asia"],"LB":["LBN","middle-east"],"LR":["LBR","africa"],"LY":["LBY","africa"],"LC":["LCA","americas"],"LI":["LIE","europe"],"LK":["LKA","asia"],"LS":["LSO","africa"],"LT":["LTU","europe"],"LU":["LUX","europe"],"LV":["LVA","europe"],"MO":["MAC","asia"],"MF":["MAF","americas"],"MA":["MAR","africa"],"MC":["MCO","europe"],"MD":["MDA","europe"],"MG":["MDG","africa"],"MV":["MDV","asia"],"MX":["MEX","americas"],"MH":["MHL","oceania"],"MK":["MKD","europe"],"ML":["MLI","africa"],"MT":["MLT","europe"],"MM":["MMR","asia"],"ME":["MNE","europe"],"MN":["MNG","asia"],"MP":["MNP","oceania"],"MZ":["MOZ","africa"],"MR":["MRT","africa"],"MS":["MSR","americas"],"MQ":["MTQ","americas"],"MU":["MUS","africa"],"MW":["MWI","africa"],"MY":["MYS","asia"],"YT":["MYT","africa"],"NA":["NAM","africa"],"NC":["NCL","oceania"],"NE":["NER","africa"],"NF":["NFK","oceania"],"NG":["NGA","africa"],"NI":["NIC","americas"],"NU":["NIU","oceania"],"NL":["NLD","europe"],"NO":["NOR","europe"],"NP":["NPL","asia"],"NR":["NRU","oceania"],"NZ":["NZL","oceania"],"OM":["OMN","middle-east"],"PK":["PAK","asia"],"PA":["PAN","americas"],"PN":["PCN","other"],"PE":["PER","americas"],"PH":["PHL","asia"],"PW":["PLW","oceania"],"PG":["PNG","oceania"],"PL":["POL","europe"],"PR":["PRI","americas"],"KP":["PRK","asia"],"PT":["PRT","europe"],"PY":["PRY","americas"],"PS":["PSE","middle-east"],"PF":["PYF","oceania"],"QA":["QAT","middle-east"],"RE":["REU","africa"],"RO":["ROU","europe"],"RU":["RUS","europe"],"RW":["RWA","africa"],"SA":["SAU","middle-east"],"SD":["SDN","africa"],"SN":["SEN","africa"],"SG":["SGP","asia"],"GS":["SGS","americas"],"SH":["SHN","africa"],"SJ":["SJM","europe"],"SB":["SLB","oceania"],"SL":["SLE","africa"],"SV":["SLV","americas"],"SM":["SMR","europe"],"SO":["SOM","africa"],"PM":["SPM","americas"],"RS":["SRB","europe"],"SS":["SSD","africa"],"ST":["STP","africa"],"SR":["SUR","americas"],"SK":["SVK","europe"],"SI":["SVN","europe"],"SE":["SWE","europe"],"SZ":["SWZ","africa"],"SX":["SXM","other"],"SC":["SYC","africa"],"SY":["SYR","middle-east"],"TC":["TCA","americas"],"TD":["TCD","africa"],"TG":["TGO","africa"],"TH":["THA","asia"],"TJ":["TJK","asia"],"TK":["TKL","oceania"],"TM":["TKM","asia"],"TL":["TLS","other"],"TO":["TON","oceania"],"TT":["TTO","americas"],"TN":["TUN","africa"],"TR":["TUR","asia"],"TV":["TUV","oceania"],"TW":["TWN","asia"],"TZ":["TZA","africa"],"UG":["UGA","africa"],"UA":["UKR","europe"],"UM":["UMI","other"],"UY":["URY","americas"],"US":["USA","americas"],"UZ":["UZB","asia"],"VA":["VAT","other"],"VC":["VCT","americas"],"VE":["VEN","americas"],"VG":["VGB","americas"],"VI":["VIR","americas"],"VN":["VNM","asia"],"VU":["VUT","oceania"],"WF":["WLF","oceania"],"WS":["WSM","oceania"],"YE":["YEM","middle-east"],"ZA":["ZAF","africa"],"ZM":["ZMB","africa"],"ZW":["ZWE","africa"]};

// Agregados que não são países ISO (ex.: Zona do Euro).
const EXTRA = { EU: ["EUZ", "europe"], EZ: ["EUZ", "europe"], EA: ["EUZ", "europe"] };

const CURRENCY_SYMBOLS = {
    USD: "$", EUR: "€", GBP: "£", JPY: "¥", CNY: "¥", CHF: "CHF",
    BRL: "R$", ARS: "$", AUD: "$", CAD: "$", NZD: "$", SGD: "S$",
    HKD: "HK$", INR: "₹", KRW: "₩", MXN: "$", TRY: "₺", SEK: "kr",
    NOK: "kr", DKK: "kr", PLN: "zł", THB: "฿", VND: "₫", ILS: "₪",
    AED: "AED", SAR: "SR", TWD: "NT$", PHP: "₱", IDR: "Rp", MYR: "RM",
    ZAR: "R", EGP: "E£", CLP: "$", COP: "$", PEN: "S/", CZK: "Kč",
    HUF: "Ft", RON: "lei", UAH: "₴"
};

class ApiError extends Error {
    constructor(message, status) {
        super(message);
        this.status = status;
    }
}

function lookup(iso2) {
    const k = String(iso2 || "").toUpperCase();
    return EXTRA[k] || ISO[k] || [k, "other"];
}

function flagEmoji(iso2) {
    const k = String(iso2 || "").toUpperCase();
    if (!/^[A-Z]{2}$/.test(k)) return "🏳️";
    return String.fromCodePoint(...[...k].map(ch => 0x1f1e6 + ch.charCodeAt(0) - 65));
}

function currencySymbol(code) {
    const k = String(code || "").toUpperCase();
    return CURRENCY_SYMBOLS[k] || k;
}

async function callApi(path, params = {}) {
    const key = process.env.BIGMAC_API_KEY;
    if (!key) throw new ApiError("BIGMAC_API_KEY não configurada no projeto.", 503);

    const url = new URL(BASE_URL + path);
    Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, String(v));
    });

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
    let response;
    try {
        response = await fetch(url, {
            headers: { Authorization: `Bearer ${key}`, Accept: "application/json" },
            signal: controller.signal
        });
    } catch (err) {
        throw new ApiError("Falha de rede ao chamar a API do Big Mac Index.", 502);
    } finally {
        clearTimeout(timer);
    }

    if (!response.ok) {
        const map = { 401: "Chave da API ausente ou inválida.", 404: "Recurso não encontrado na API.", 429: "Limite de requisições da API excedido." };
        throw new ApiError(map[response.status] || `A API retornou HTTP ${response.status}.`, response.status === 429 ? 429 : 502);
    }
    try {
        return await response.json();
    } catch (err) {
        throw new ApiError("Resposta inválida da API (não é JSON).", 502);
    }
}

// Cache na CDN da Vercel: os dados mudam no máximo uma vez por dia e o plano
// gratuito da API permite 500 requisições/dia, então a CDN absorve o tráfego.
function sendJson(res, status, body, cacheSeconds) {
    res.statusCode = status;
    res.setHeader("Content-Type", "application/json; charset=utf-8");
    res.setHeader(
        "Cache-Control",
        cacheSeconds
            ? `public, max-age=0, s-maxage=${cacheSeconds}, stale-while-revalidate=86400`
            : "no-store"
    );
    res.end(JSON.stringify(body));
}

function sendError(res, err) {
    const status = err instanceof ApiError ? err.status : 500;
    sendJson(res, status, { error: err instanceof ApiError ? err.message : "Erro interno." }, 0);
}

module.exports = { ApiError, callApi, lookup, flagEmoji, currencySymbol, sendJson, sendError };

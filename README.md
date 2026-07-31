# 🍔 Big Mac Index Dashboard

Dashboard interativo em **Python + Streamlit** para explorar o *Big Mac
Index* — o indicador de paridade do poder de compra (PPP) inspirado no
conceito criado pela *The Economist* em 1986. O projeto consome a
**[API do bigmacindex.com](https://bigmacindex.com/api)** em tempo real e
traz mapa mundial interativo, rankings por país, tendências históricas de
preços e uma calculadora de PPP.

---

## Sumário

1. [Visão geral](#visão-geral)
2. [Fonte de dados: API do bigmacindex.com](#fonte-de-dados-api-do-bigmacindexcom)
3. [Funcionalidades](#funcionalidades)
4. [Estrutura do projeto](#estrutura-do-projeto)
5. [Pré-requisitos](#pré-requisitos)
6. [Configurando a API key](#configurando-a-api-key)
7. [Instalação e execução local](#instalação-e-execução-local)
8. [Deploy no Streamlit Community Cloud](#deploy-no-streamlit-community-cloud)
9. [Modo offline / fallback](#modo-offline--fallback)
10. [Testes automatizados](#testes-automatizados)
11. [Limites de uso da API](#limites-de-uso-da-api)
12. [Tecnologias utilizadas](#tecnologias-utilizadas)
13. [Roadmap / próximos passos](#roadmap--próximos-passos)
14. [Contribuindo](#contribuindo)
15. [Licença](#licença)

---

## Visão geral

O **Big Mac Index** compara o preço do Big Mac em dezenas de países para
estimar se uma moeda está super ou subvalorizada frente ao dólar, partindo
da teoria da paridade do poder de compra (PPP): no longo prazo, taxas de
câmbio deveriam se ajustar até que uma mesma cesta de bens — neste caso,
um hambúrguer — custe o mesmo em qualquer lugar do mundo.

Este dashboard consome dados **ao vivo** e apresenta-os de forma visual e
interativa, permitindo:

- comparar preços entre dezenas de países num mapa mundial;
- reclassificar o ranking usando **qualquer país como moeda-base**, não
  apenas o dólar;
- visualizar a evolução histórica de preços por país, dia a dia;
- converter valores entre duas moedas usando a taxa implícita pelo Big Mac.

---

## Fonte de dados: API do bigmacindex.com

Toda a camada de dados (`src/api_client.py` + `src/data_loader.py`) consome
a **[Big Mac Index API](https://bigmacindex.com/api)**, um serviço REST
independente (não afiliado ao McDonald's nem à The Economist) com os
seguintes endpoints:

| Endpoint | Uso no projeto | Requer chave? |
|---|---|---|
| `GET /countries` | Diretório de países cobertos | Não |
| `GET /market/current` | Status do pipeline de dados | Não |
| `GET /latest` | Snapshot atual de preços/PPP por país (usado na Home, Mapa e Rankings) | **Sim** |
| `GET /history` | Histórico diário de preços por país (página Tendências) | **Sim** |
| `GET /rankings` | Ranking por métrica (referência; o app recalcula localmente para trocar a moeda-base) | **Sim** |
| `GET /currencies` | Câmbio + sinal de valorização por moeda | **Sim** |
| `GET /fx/history` | Histórico cambial de uma moeda vs. USD | **Sim** |
| `GET /global` | Tendência global (preço médio + benchmark BMDI) | **Sim** |

> A maioria dos endpoints de dados exige uma **API key gratuita** (Bearer
> token). Veja a seção [Configurando a API key](#configurando-a-api-key)
> abaixo. Sem uma chave configurada, o dashboard funciona normalmente em
> **modo offline/fallback** (veja a seção correspondente), usando um
> snapshot local para nunca ficar fora do ar.

---

## Funcionalidades

| Página | Descrição |
|---|---|
| 🏠 **Home** (`app.py`) | Cartões de indicadores (KPIs), mapa mundial resumido, badge indicando se os dados são ao vivo ou offline |
| 🗺️ **Mapa Mundial** | Mapa coroplético interativo (Plotly) com filtros por região e faixa de preço; alterna entre "preço em USD" e "variação % vs. base" |
| 📊 **Rankings** | Ranking completo com seletor de moeda-base (USD, EUR, GBP, JPY, CNY...), gráfico de extremos (mais caros vs. mais baratos) e distribuição de preços por região |
| 📈 **Tendências Históricas** | Série diária de preços por país via `GET /history`, com seleção múltipla de países e janela de tempo ajustável (30 a 365 dias) |
| 🧮 **Calculadora de PPP** | Converte um valor entre dois países usando a taxa de câmbio implícita pelo Big Mac Index, comparando com a taxa de câmbio de mercado |

Recursos adicionais:

- 🟢/🟡 Badge de status indicando se os dados vêm da API ao vivo ou do fallback offline
- 🎨 Tema visual customizado via CSS próprio (`assets/style.css`)
- ⬇️ Exportação de tabelas e séries filtradas em CSV
- ✅ Testes unitários com `pytest`
- 🧩 Código organizado em módulos reutilizáveis (`src/`)

---

## Estrutura do projeto

```
bigmac-dashboard/
├── app.py                          # Ponto de entrada do Streamlit (página Home)
├── requirements.txt                 # Dependências do projeto (sem versões fixas)
├── README.md                        # Este arquivo
├── LICENSE                          # Licença MIT
├── .gitignore                       # Arquivos/pastas ignorados pelo Git (inclui secrets.toml)
│
├── .streamlit/
│   ├── config.toml                  # Tema visual (cores, layout, servidor)
│   └── secrets.toml.example         # Modelo para configurar BIGMAC_API_KEY
│
├── data/
│   ├── fallback_countries.json      # Snapshot local usado quando a API está indisponível
│   └── fallback_historical_prices.csv  # Série histórica ilustrativa de fallback
│
├── src/
│   ├── __init__.py
│   ├── api_client.py                # Cliente HTTP da API bigmacindex.com (auth, cache, erros)
│   ├── enrich.py                    # ISO2↔ISO3, região, bandeira, símbolo de moeda, slug
│   ├── data_loader.py               # Orquestra API + fallback e normaliza os dados
│   ├── metrics.py                   # Troca de moeda-base, estatísticas, classificação de valorização
│   ├── maps.py                      # Construção dos mapas coropléticos (Plotly)
│   ├── charts.py                    # Gráficos de barras, linhas e boxplot
│   └── styling.py                   # Injeção do CSS customizado e cartões de KPI
│
├── assets/
│   └── style.css                    # Estilo visual customizado do dashboard
│
├── pages/
│   ├── 1_Mapa_Mundial.py            # Mapa mundial detalhado com filtros
│   ├── 2_Rankings.py                # Rankings completos + seletor de moeda-base
│   ├── 3_Tendencias_Historicas.py   # Séries históricas via GET /history
│   └── 4_Calculadora_PPP.py         # Calculadora de conversão via PPP
│
└── tests/
    └── test_data_loader.py          # Testes unitários (pytest)
```

---

## Pré-requisitos

- Python 3.10 ou superior
- `pip` atualizado
- Uma **API key gratuita** do bigmacindex.com (opcional, mas recomendada — veja abaixo)
- Git (opcional, para versionamento e deploy via GitHub)

---

## Configurando a API key

1. Crie uma conta gratuita em **[bigmacindex.com/signup](https://bigmacindex.com/signup)**.
2. Gere uma chave em **[bigmacindex.com/account](https://bigmacindex.com/account)**.
3. Configure a chave de uma das duas formas:

   **Opção A — arquivo de secrets do Streamlit (recomendado):**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
   Depois edite `.streamlit/secrets.toml` e cole sua chave:
   ```toml
   BIGMAC_API_KEY = "sua-chave-aqui"
   ```
   Esse arquivo já está no `.gitignore` — ele nunca será commitado.

   **Opção B — variável de ambiente:**
   ```bash
   export BIGMAC_API_KEY="sua-chave-aqui"      # Linux/Mac
   set BIGMAC_API_KEY=sua-chave-aqui           # Windows
   ```

Sem chave configurada, o app continua funcionando normalmente, mas em
**modo offline/fallback** (veja a seção dedicada mais abaixo).

---

## Instalação e execução local

```bash
# 1. Clonar o repositório
git clone https://github.com/SEU-USUARIO/bigmac-dashboard.git
cd bigmac-dashboard

# 2. Criar e ativar um ambiente virtual (recomendado)
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. (Opcional, mas recomendado) Configurar a API key — veja a seção acima

# 5. Rodar o dashboard
streamlit run app.py
```

O aplicativo abrirá automaticamente em `http://localhost:8501`. As demais
páginas aparecem na barra lateral, detectadas automaticamente pelo
Streamlit a partir da pasta `pages/`.

---

## Deploy no Streamlit Community Cloud

1. Suba este projeto para um repositório no GitHub (mantendo a estrutura de
   pastas — veja a dica abaixo).
2. Acesse [share.streamlit.io](https://share.streamlit.io/) e conecte sua
   conta do GitHub.
3. Clique em **New app** e selecione:
   - **Repository**: seu repositório `bigmac-dashboard`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Antes (ou depois) de publicar, configure o segredo da API em
   **App settings → Secrets**, colando:
   ```toml
   BIGMAC_API_KEY = "sua-chave-aqui"
   ```
5. Clique em **Deploy**.

> 💡 Como o `requirements.txt` não fixa versões, o Streamlit Cloud sempre
> instalará as versões mais recentes compatíveis das bibliotecas no momento
> do deploy.

> ⚠️ **Dica de upload:** ao subir arquivos pela interface web do GitHub
> ("Add file → Upload files"), arraste a **pasta inteira** do projeto — se
> você arrastar os arquivos individualmente, o GitHub os coloca todos soltos
> na raiz, perdendo a estrutura de `src/`, `pages/`, `data/` etc.

---

## Modo offline / fallback

Se a `BIGMAC_API_KEY` não estiver configurada, se a chave for inválida, ou
se a API estiver temporariamente fora do ar, o dashboard **não quebra**:
ele detecta a falha automaticamente (`src/api_client.py` levanta
`ApiAuthError` / `ApiRateLimitError` / `ApiError`) e a camada de dados
(`src/data_loader.py`) recorre a um snapshot local:

- `data/fallback_countries.json` — preços por país (captura estática)
- `data/fallback_historical_prices.csv` — série histórica **ilustrativa**,
  construída a partir do preço mais recente de cada país com uma
  trajetória de crescimento plausível (não são valores reais dia a dia)

Um badge amarelo 🟡 aparece no topo do app sempre que ele estiver operando
neste modo, e some assim que uma chave válida é configurada.

---

## Testes automatizados

```bash
pip install pytest
pytest
```

Os testes cobrem, entre outras coisas:

- existência e integridade dos arquivos de fallback;
- normalização do DataFrame de países (colunas esperadas, EUA como base);
- as funções auxiliares de `src/enrich.py`: conversão ISO2→ISO3, geração de
  bandeira por emoji, classificação de região (incluindo o caso especial
  do Oriente Médio) e símbolo de moeda.

Como os testes não dependem de uma API key, eles exercitam principalmente
o caminho de fallback — o que também serve como garantia de que esse
caminho sempre funciona.

---

## Limites de uso da API

De acordo com a documentação oficial ([bigmacindex.com/api](https://bigmacindex.com/api)):

| Plano | Limite | Observações |
|---|---|---|
| **Free** | 20 req/min · 500 req/dia · 1 chave | Todos os endpoints de dados; exports em massa exigem login |
| **Commercial** | 1.000 req/min · 1M req/dia · 10 chaves | White-label, licença de redistribuição |
| **Enterprise** | 10M+/dia | SLA, on-premise, sob consulta |

Para respeitar o limite do plano gratuito, todas as chamadas em
`src/api_client.py` usam `st.cache_data` com TTL de 30 minutos (dados de
preço) ou 5 minutos (status do pipeline), evitando requisições repetidas
desnecessárias a cada interação do usuário.

---

## Tecnologias utilizadas

- [Streamlit](https://streamlit.io/) — framework do dashboard e das páginas
- [Pandas](https://pandas.pydata.org/) — manipulação e transformação de dados
- [Plotly](https://plotly.com/python/) — mapas coropléticos e gráficos interativos
- [Requests](https://docs.python-requests.org/) — cliente HTTP para a API do bigmacindex.com
- [pycountry](https://github.com/pycountry/pycountry) — conversão ISO alpha-2 ↔ alpha-3
- [pycountry-convert](https://pypi.org/project/pycountry-convert/) — mapeamento país → continente
- [NumPy](https://numpy.org/) — suporte a cálculos numéricos
- [pytest](https://docs.pytest.org/) — testes unitários

---

## Roadmap / próximos passos

- [ ] Consumir `GET /currencies` e `GET /fx/history` para uma página dedicada de câmbio
- [ ] Usar `GET /global` para o gráfico de tendência mundial (BMDI) na Home
- [ ] Exibir o preview de `GET /compare` como um comparador rápido de 2 países
- [ ] Adicionar página de metodologia (Raw Index vs. Income-Adjusted Index)
- [ ] Internacionalização (EN / ES / PT)

---

## Contribuindo

Contribuições são bem-vindas! Para propor uma mudança:

1. Faça um fork do repositório
2. Crie uma branch para a sua feature (`git checkout -b feature/minha-feature`)
3. Faça commit das suas alterações (`git commit -m "Adiciona minha feature"`)
4. Envie para o seu fork (`git push origin feature/minha-feature`)
5. Abra um Pull Request

Ao contribuir, procure manter o padrão de organização em `src/` (lógica) e
`pages/` (interface), além de adicionar testes quando aplicável.

---

## Licença

Este projeto é disponibilizado sob a licença **MIT** (veja o arquivo
`LICENSE`). Os dados consumidos pertencem ao **bigmacindex.com** e estão
sujeitos aos termos de uso da própria API; o dataset de fallback reflete
uma captura estática do The Economist Big Mac Index, usada apenas como
rede de segurança offline.

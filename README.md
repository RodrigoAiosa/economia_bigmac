# 🍔 Big Mac Index Dashboard

Dashboard interativo em **Python + Streamlit** para explorar o *Big Mac
Index* — o indicador de paridade do poder de compra (PPP) criado pela
*The Economist* em 1986. O projeto traz mapa mundial interativo, rankings
por país, tendências históricas de preços e uma calculadora de PPP.

Inspirado no layout e na estrutura de dados do site
[bigmacindex.app](https://bigmacindex.app/).

---

## Sumário

1. [Visão geral](#visão-geral)
2. [Funcionalidades](#funcionalidades)
3. [Demonstração das páginas](#demonstração-das-páginas)
4. [Estrutura do projeto](#estrutura-do-projeto)
5. [Pré-requisitos](#pré-requisitos)
6. [Instalação e execução local](#instalação-e-execução-local)
7. [Deploy no Streamlit Community Cloud](#deploy-no-streamlit-community-cloud)
8. [Testes automatizados](#testes-automatizados)
9. [Fonte e limitações dos dados](#fonte-e-limitações-dos-dados)
10. [Tecnologias utilizadas](#tecnologias-utilizadas)
11. [Roadmap / próximos passos](#roadmap--próximos-passos)
12. [Contribuindo](#contribuindo)
13. [Licença](#licença)

---

## Visão geral

O **Big Mac Index** compara o preço do Big Mac em dezenas de países para
estimar se uma moeda está super ou subvalorizada frente ao dólar, partindo
da teoria da paridade do poder de compra (PPP): no longo prazo, taxas de
câmbio deveriam se ajustar até que uma mesma cesta de bens — neste caso,
um hambúrguer — custe o mesmo em qualquer lugar do mundo.

Este dashboard consome o dataset oficial publicado pela *The Economist* e
apresenta os dados de forma visual e interativa, permitindo:

- comparar preços entre 54 países num mapa mundial;
- reclassificar o ranking usando **qualquer país como moeda-base**, não
  apenas o dólar;
- visualizar a evolução histórica de preços por país;
- converter valores entre duas moedas usando a taxa implícita pelo Big Mac.

---

## Funcionalidades

| Página | Descrição |
|---|---|
| 🏠 **Home** (`app.py`) | Cartões de indicadores (KPIs), mapa mundial resumido e navegação para as demais páginas |
| 🗺️ **Mapa Mundial** | Mapa coroplético interativo (Plotly) com filtros por região e faixa de preço; alterna entre "preço em USD" e "variação % vs. base" |
| 📊 **Rankings** | Ranking completo com seletor de moeda-base (USD, EUR, GBP, JPY, CNY...), gráfico de extremos (mais caros vs. mais baratos) e distribuição de preços por região |
| 📈 **Tendências Históricas** | Série de preços por país entre 2010 e 2025, com seleção múltipla de países para comparação |
| 🧮 **Calculadora de PPP** | Converte um valor entre dois países usando a taxa de câmbio implícita pelo Big Mac Index, comparando com a taxa de câmbio de mercado |

Recursos adicionais:

- 🎨 Tema visual customizado via CSS próprio (`assets/style.css`)
- ⬇️ Exportação de tabelas filtradas em CSV
- ✅ Testes unitários com `pytest`
- 🧩 Código organizado em módulos reutilizáveis (`src/`)

---

## Demonstração das páginas

```
Home  ──────────────▶  KPIs gerais + mapa resumido
  │
  ├── 🗺️  Mapa Mundial          → filtros de região/preço, dois modos de cor
  ├── 📊  Rankings              → troca de moeda-base, top 10, boxplot por região
  ├── 📈  Tendências Históricas → linha do tempo 2010-2025 por país
  └── 🧮  Calculadora de PPP    → conversão entre duas moedas via PPP
```

---

## Estrutura do projeto

```
bigmac-dashboard/
├── app.py                        # Ponto de entrada do Streamlit (página Home)
├── requirements.txt               # Dependências do projeto (sem versões fixas)
├── README.md                      # Este arquivo
├── LICENSE                        # Licença MIT
├── .gitignore                     # Arquivos/pastas ignorados pelo Git
│
├── .streamlit/
│   └── config.toml                # Tema visual (cores, layout, servidor)
│
├── data/
│   ├── countries.json             # Dataset oficial: 54 países (The Economist Big Mac Index)
│   └── historical_prices.csv      # Série histórica ilustrativa (2010-2025)
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py             # Carregamento, validação e cache dos dados
│   ├── metrics.py                 # Cálculos: troca de moeda-base, estatísticas, classificação de valorização
│   ├── maps.py                    # Construção dos mapas coropléticos (Plotly)
│   ├── charts.py                  # Gráficos de barras, linhas e boxplot
│   └── styling.py                 # Injeção do CSS customizado e cartões de KPI
│
├── assets/
│   └── style.css                  # Estilo visual customizado do dashboard
│
├── pages/
│   ├── 1_Mapa_Mundial.py          # Mapa mundial detalhado com filtros
│   ├── 2_Rankings.py              # Rankings completos + seletor de moeda-base
│   ├── 3_Tendencias_Historicas.py # Séries históricas de preços
│   └── 4_Calculadora_PPP.py       # Calculadora de conversão via PPP
│
└── tests/
    └── test_data_loader.py        # Testes unitários (pytest)
```

---

## Pré-requisitos

- Python 3.10 ou superior
- `pip` atualizado
- Git (opcional, para versionamento e deploy via GitHub)

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

# 4. Rodar o dashboard
streamlit run app.py
```

O aplicativo abrirá automaticamente em `http://localhost:8501`. As demais
páginas (Mapa Mundial, Rankings, Tendências Históricas, Calculadora de PPP)
aparecem na barra lateral, detectadas automaticamente pelo Streamlit a
partir da pasta `pages/`.

---

## Deploy no Streamlit Community Cloud

1. Suba este projeto para um repositório público (ou privado) no GitHub.
2. Acesse [share.streamlit.io](https://share.streamlit.io/) e conecte sua
   conta do GitHub.
3. Clique em **New app** e selecione:
   - **Repository**: seu repositório `bigmac-dashboard`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Clique em **Deploy**.

O Streamlit Cloud instala automaticamente as dependências listadas em
`requirements.txt` e publica o app com uma URL pública.

> 💡 Como o `requirements.txt` não fixa versões, o Streamlit Cloud sempre
> instalará as versões mais recentes compatíveis das bibliotecas no momento
> do deploy.

---

## Testes automatizados

O projeto inclui testes unitários básicos para a camada de dados
(`src/data_loader.py`) usando `pytest`.

```bash
pip install pytest
pytest
```

Os testes verificam, entre outras coisas:

- se o arquivo `data/countries.json` existe e é válido;
- se o DataFrame de países contém as colunas esperadas;
- se os Estados Unidos aparecem como país-base (`diff_percent == 0`);
- se todos os preços em USD são positivos.

---

## Fonte e limitações dos dados

| Dado | Fonte | Observações |
|---|---|---|
| Preços do Big Mac por país | [The Economist Big Mac Index](https://www.economist.com/big-mac-index) via [TheEconomist/big-mac-data](https://github.com/TheEconomist/big-mac-data) | Dataset oficial, replicado em `data/countries.json` |
| Estrutura/layout de referência | [bigmacindex.app](https://bigmacindex.app/) | Inspiração visual e de organização das seções |
| Série histórica (`historical_prices.csv`) | Gerada de forma **ilustrativa** a partir do preço mais recente de cada país | **Não representa valores exatos** publicados semestralmente pela The Economist. Para dados históricos reais e completos desde 2000, baixe o dataset bruto do repositório oficial e substitua este arquivo |

⚠️ **Aviso importante**: os dados são fornecidos apenas para fins
educacionais e de referência. O Big Mac Index é descrito pela própria
The Economist como um guia "descontraído" sobre valorização cambial — **não
constitui recomendação de investimento**.

---

## Tecnologias utilizadas

- [Streamlit](https://streamlit.io/) — framework do dashboard e das páginas
- [Pandas](https://pandas.pydata.org/) — manipulação e transformação de dados
- [Plotly](https://plotly.com/python/) — mapas coropléticos e gráficos interativos
- [NumPy](https://numpy.org/) — suporte a cálculos numéricos
- [Requests](https://docs.python-requests.org/) — reservado para futura integração com fontes de dados ao vivo
- [pytest](https://docs.pytest.org/) — testes unitários

---

## Roadmap / próximos passos

- [ ] Integrar taxas de câmbio em tempo real (modo "Live Rates")
- [ ] Substituir a série histórica ilustrativa pelo dataset bruto completo do GitHub oficial
- [ ] Adicionar página de metodologia (Raw Index vs. GDP-Adjusted Index)
- [ ] Internacionalização (EN / ES / PT)
- [ ] Cache/local storage para preferências do usuário (moeda-base padrão, região favorita)

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
`LICENSE`). Os dados do Big Mac Index pertencem à *The Economist* e estão
sujeitos aos termos de uso da fonte original.

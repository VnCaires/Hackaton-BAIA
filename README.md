# Calculadora de Orçamento Climático da Bahia

Distribui um orçamento público entre os **417 municípios da Bahia** de forma proporcional ao
risco climático de cada um. Não prevê o tempo: responde **onde investir** para reduzir
vulnerabilidade.

- **Metodologia completa:** [`docs/Plano.md`](docs/Plano.md) e [`docs/methodology.md`](docs/methodology.md)

## O problema

Recursos para adaptação climática são escassos e a alocação costuma ser política ou uniforme.
Falta um critério objetivo, reproduzível e auditável para responder: dado um orçamento, **quanto
cada município deve receber** segundo o risco climático que enfrenta.

## A solução

Um índice de vulnerabilidade climática construído a partir de 21 anos de dados do INMET, que vira
um peso por município (somando 1) e converte qualquer orçamento em uma alocação justificada.

| Indicador | Valor |
|---|---|
| Municípios cobertos | 417 (todos da Bahia) |
| Série histórica | 21 anos (INMET, 2000–2021) |
| Estações meteorológicas | 45 |
| Pesos de vulnerabilidade | normalizados, somam 1 |

## Como funciona

```
INMET (21 anos)
  -> sub-índices de seca, enchente e calor por estação
  -> PCA aprende a ameaça composta (não-supervisionado)
  -> IDW interpola as 45 estações para os 417 municípios
  -> IDHM entra como capacidade adaptativa
  -> peso per capita normalizado (Σ = 1)
  -> KMeans agrupa arquétipos + projeção de tendência até 2030
```

Todo o pipeline é **não-supervisionado e auditável**, sem dependência de LLM para gerar ou
justificar os resultados.

## O que o app entrega

- **Calculadora de Orçamento:** informe o valor total e veja a alocação por município, com pesos
  ajustáveis por tipo de risco e exportação em CSV.
- **Mapa de Risco:** mapa coroplético dos 417 municípios por camada (vulnerabilidade geral, seca,
  enchente, calor e projeção 2030).
- **Arquétipos & Projeção:** agrupamento KMeans dos perfis de vulnerabilidade e a tendência
  histórica projetada para 2026–2030.

## Como rodar

```bash
pip install -e ".[app]"
python scripts/build_scores.py   # gera data/processed/scores.csv a partir de examples/
streamlit run app.py             # abre a calculadora no navegador
```

O app e o build funcionam com os exemplos versionados em `examples/`, **sem precisar baixar o
dataset bruto**.

Para rodar os testes:

```bash
pip install -e ".[dev]"
pytest
```

## Dados e reprodutibilidade

O necessário já está no repositório (`examples/`): indicadores por estação, malha municipal,
população + IDHM e os scores finais. Por isso o app roda sem baixar nada.

O dataset bruto do INMET (CSV horário, 549 MB) não é versionado. Para regenerar tudo do zero:

```bash
python scripts/baixar_municipios_ibge.py   # IBGE + IDHM
python scripts/baixar_dataset_inmet.py      # CSV bruto (GitHub Release, fallback Google Drive)
python scripts/build_scores.py
```

- **GitHub Release:** [`dataset-v1`](https://github.com/VnCaires/Hackaton-BAIA/releases/tag/dataset-v1) (`clima_bahia.csv.gz`, ~122 MB)
- `data/sample/clima_bahia_2020.csv.gz`: recorte do último ano completo, para desenvolvimento local.

## Estrutura

```text
.
├── app.py                  # aplicação Streamlit (calculadora, mapa, arquétipos)
├── scripts/                # download de dados e geração de scores
├── src/municipios_score/   # pipeline: índices, PCA/IDW, arquétipos, projeção
├── examples/               # dados de exemplo versionados (app roda sem download)
├── data/                   # raw/interim/processed/sample (brutos não versionados)
├── docs/                   # metodologia, dicionário de dados e visão de produto
└── tests/                  # suíte de testes (pytest)
```

Documentação detalhada em [`docs/`](docs): [`methodology.md`](docs/methodology.md),
[`data_dictionary.md`](docs/data_dictionary.md) e [`project_overview.md`](docs/project_overview.md).

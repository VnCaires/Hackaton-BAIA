# Dicionario de Dados

Use este arquivo para registrar os datasets e indicadores usados no score.

## Datasets

| Dataset | Fonte | Atualizacao | Licenca | Chave municipal | Observacoes |
| --- | --- | --- | --- | --- | --- |
| INMET historico horario | INMET (Drive) | Estatico 2000-2021 | Dados publicos | via estacao -> IDW | 549 MB, local em `data/raw/`, nao versionado |
| Malha municipal BA | IBGE API v3 malhas | Anual | Dados publicos | `codarea` | GeoJSON dos 417 municipios |
| Populacao 2021 | IBGE SIDRA agregado 6579 | Anual | Dados publicos | `codigo` (7 digitos) | Estimativa 2021 |
| IDHM | Atlas Brasil / PNUD | 2010 | Dados publicos | `Codmun7` | Capacidade adaptativa |
| Previsao (opcional) | Open-Meteo | Tempo real | Free, sem chave | lat/lon do centroide | Alerta de chuva 7-16 dias |

## Indicadores

| Coluna | Descricao | Direcao | Peso inicial | Tratamento |
| --- | --- | --- | ---: | --- |
| seca | Aridez + dias secos consecutivos + deficit decada | negative (mais seco = pior) | PCA | normalizacao robusta p5-p95 |
| enchente | Rx1day + dias com chuva >= 50mm | positive (mais chuva extrema = pior) | PCA | normalizacao robusta p5-p95 |
| calor | TX90p (excedencia p90) + tendencia de temperatura | positive | PCA | baseline <=2010 vs >=2011 |
| ameaca | Componente principal (PCA) dos 3 sub-indices | positive | - | min-max para [0,1] |
| idhm | Indice de Desenvolvimento Humano Municipal (capacidade) | negative (menor IDHM = mais peso) | - | divisor do peso |
| peso | `ameaca / idhm` normalizado | - | - | soma = 1 entre municipios |

Saidas versionadas em `examples/` (amostras pequenas): `scores_municipios.csv`,
`estacoes_inmet_ba.csv`, `municipios_ba.csv`, `ba_municipios.geojson`.

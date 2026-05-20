# Hackaton BAIA

Repositorio colaborativo para desenvolver um algoritmo de score de municipios a partir de datasets publicos ou internos.

## Objetivo

Criar um pipeline reproduzivel que:

1. Carrega datasets de municipios.
2. Padroniza indicadores em uma escala comum.
3. Calcula um score ponderado por municipio.
4. Gera rankings e artefatos para analise.

## Estrutura

```text
.
|-- data/
|   |-- raw/          # datasets originais, nao versionados
|   |-- interim/      # dados intermediarios, nao versionados
|   |-- processed/    # dados finais, nao versionados
|   `-- README.md
|-- docs/             # dicionario de dados e decisoes do projeto
|-- examples/         # exemplos pequenos e seguros para versionar
|-- notebooks/        # exploracoes e analises
|-- src/
|   `-- municipios_score/
|-- tests/
|-- .github/
`-- requirements.txt
```

## Comeco rapido

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest
```

Para calcular scores com os arquivos de exemplo:

```bash
python -m municipios_score.cli examples/indicadores_exemplo.csv examples/config_score_exemplo.json outputs/scores.csv
```

## Fluxo de colaboracao

- Trabalhem em branches curtas, como `feature/normalizacao-dados` ou `fix/pesos-score`.
- Abram pull requests para `main`.
- Cada PR deve explicar o que mudou, como testar e se houve mudanca em datasets.
- Evitem commitar dados grandes, sensiveis ou proprietarios. Usem `data/` localmente e versionem apenas amostras pequenas em `examples/`.
- Registrem decisoes de metodologia em `docs/`.

## Metodologia inicial de score

O score base usa normalizacao min-max por indicador:

- `positive`: quanto maior o indicador, melhor o score.
- `negative`: quanto menor o indicador, melhor o score.

O score final e a media ponderada dos indicadores normalizados, em escala de 0 a 100.

Essa metodologia e propositalmente simples para servir como baseline. Durante o hackathon, documentem ajustes como tratamento de outliers, imputacao de nulos, pesos e validacao.

## Cuidados com dados

- Nunca suba arquivos brutos grandes para o Git.
- Inclua fonte, data de coleta, licenca e granularidade em `docs/data_dictionary.md`.
- Use nomes de colunas estaveis e documentados.
- Se for preciso compartilhar datasets grandes, use armazenamento externo e registre o link no README ou em `docs/`.

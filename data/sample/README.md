# Dataset de Desenvolvimento

Esta pasta guarda recortes pequenos o suficiente para versionamento no Git.

## `clima_bahia_2020.csv.gz`

Recorte do arquivo bruto `data/raw/clima_bahia_hackathon(1).csv`, contendo apenas o ultimo ano completo disponivel no dataset: 2020.

Resumo do recorte:

- Ano: 2020.
- Estacoes: 47.
- Linhas: 412.848.
- Cobertura por estacao: 8.784 registros, equivalente a 366 dias * 24 horas.
- Tamanho aproximado em CSV: 37,38 MB.
- Tamanho comprimido em gzip: 8,86 MB.

Por que versionar o `.csv.gz`:

- Fica bem abaixo do limite de 100 MB do GitHub.
- Evita carregar o CSV bruto completo de aproximadamente 549 MB.
- Permite que novos integrantes rodem e testem o pipeline sem baixar o dataset inteiro.
- `pandas.read_csv` le automaticamente arquivos `.csv.gz`.

Para analises finais, use o dataset completo em `data/raw/`, que nao deve ser commitado.


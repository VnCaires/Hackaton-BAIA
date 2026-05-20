# Guia de Contribuicao

## Branches

- `main`: versao estavel do projeto.
- `feature/nome-curto`: novas funcionalidades.
- `fix/nome-curto`: correcoes.
- `data/nome-curto`: tarefas de dados e indicadores.

## Pull requests

Antes de abrir um PR:

1. Rode `pytest`.
2. Confirme que nenhum dado bruto, grande ou sensivel foi adicionado.
3. Atualize `docs/data_dictionary.md` quando incluir novos datasets ou indicadores.
4. Explique no PR o impacto nos scores, se houver.

## Dados

Use `data/` apenas localmente. Para dados pequenos de exemplo, prefira `examples/`.

## Padrao de codigo

- Mantenha funcoes pequenas e testaveis.
- Separe regras de score de notebooks exploratorios.
- Adicione testes para novas regras de normalizacao, pesos ou ranking.


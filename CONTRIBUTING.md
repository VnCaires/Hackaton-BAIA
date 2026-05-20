# Guia de Contribuicao

## Branches

- `main`: versao estavel do projeto.
- `feature/nome-curto`: novas funcionalidades.
- `fix/nome-curto`: correcoes.
- `data/nome-curto`: tarefas de dados e indicadores.

Cada integrante deve trabalhar em sua propria branch e abrir pull request para integrar na `main`. Isso evita sobrescrever trabalho dos colegas, facilita revisao e deixa o historico do projeto mais claro.

Fluxo recomendado:

1. Atualize a `main`: `git checkout main && git pull`.
2. Crie uma branch curta: `git checkout -b feature/nome-da-tarefa`.
3. Faca commits pequenos e com mensagens objetivas.
4. Rode `pytest` antes de subir.
5. Envie a branch: `git push -u origin feature/nome-da-tarefa`.
6. Abra um pull request para `main`.
7. Peca revisao de pelo menos uma pessoa da equipe.

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

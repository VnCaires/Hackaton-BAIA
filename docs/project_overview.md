# Visao do Projeto para Desenvolvedores

Este documento traduz a proposta de produto em uma referencia tecnica para quem vai implementar, revisar ou evoluir o projeto.

## Tese do produto

Nao queremos prever se vai chover. Queremos responder onde o estado da Bahia deve investir cada real do orcamento de resiliencia climatica.

A solucao prioriza os 417 municipios baianos mais vulneraveis e com menor capacidade de se defenderem sozinhos. O resultado esperado e um indice de vulnerabilidade que vira uma calculadora de alocacao: dado um orcamento total, o sistema retorna quanto cada municipio deve receber.

## Contexto do desafio

A Bahia enfrenta extremos climaticos diferentes ao mesmo tempo:

- Secas severas no semiarido.
- Enchentes urbanas em areas densas e vulneraveis.
- Ondas de calor e impactos indiretos em saude, infraestrutura e economia local.

O problema publico concreto e a escassez de orcamento. Se nao ha verba para tudo, a pergunta principal vira: para onde mandar primeiro?

Muitas solucoes de IA ficam em previsao meteorologica de curto prazo. Este projeto parte de outra premissa: transformar dados climaticos historicos e indicadores municipais em uma recomendacao acionavel de investimento.

## Escopo inicial

O produto deve cobrir:

- 417 municipios da Bahia.
- Serie historica climatica de 2000 a 2021.
- Dados do INMET com 45 estacoes.
- Aproximadamente 5,2 milhoes de medicoes horarias.
- Indicadores municipais complementares, como vulnerabilidade social, infraestrutura, saude, renda, exposicao territorial e capacidade institucional.

Os numeros acima definem a narrativa e o alvo do produto. Cada dataset usado de fato deve ser registrado em `docs/data_dictionary.md` com fonte, periodo, licenca, chave municipal e tratamentos aplicados.

## Usuarios-alvo

### Governo

Precisa decidir onde alocar recursos limitados com criterio transparente, defensavel e baseado em dados.

### Defesa Civil

Precisa enxergar quais municipios estao em pior situacao, por tipo de risco e por capacidade de resposta.

### Iniciativa privada

Pode usar o indice para orientar investimento, mitigacao de risco, infraestrutura, seguros, credito e projetos de impacto.

## Componentes do produto

### 1. Indice de vulnerabilidade climatica

Cada municipio recebe um peso de vulnerabilidade. A soma dos pesos dos 417 municipios deve ser 1.

Exemplo conceitual:

```text
municipio_a: 0.021
municipio_b: 0.014
municipio_c: 0.008
...
soma: 1.000
```

Esse peso representa a parcela recomendada do orcamento total.

### 2. Calculadora de orcamento

Entrada:

- Orcamento total disponivel.
- Pesos de prioridade por tipo de risco, como seca, enchente e calor.

Saida:

- Tabela municipio por municipio.
- Valor em reais recomendado para cada municipio.
- Score total e decomposicao por categoria.
- Exportacao em CSV.

Formula base:

```text
valor_municipio = orcamento_total * peso_vulnerabilidade_municipio
```

### 3. Mapa de risco

Mapa coropletico dos 417 municipios da Bahia.

Requisitos esperados:

- Visualizar score total por municipio.
- Alternar camadas por categoria: seca, enchente, calor e capacidade de resposta.
- Clicar em um municipio e ver a decomposicao do risco.
- Comparar score atual com projecao ate 2030.

### 4. Arquetipos e projecao

Agrupar municipios em tipologias de vulnerabilidade, por exemplo:

- Seca estrutural com baixa capacidade fiscal.
- Enchente urbana com alta densidade populacional.
- Calor extremo com fragilidade em saude.
- Risco moderado, mas baixa capacidade de resposta.

A projecao ate 2030 deve ser tratada como tendencia, nao como previsao deterministica. O modelo precisa deixar claro quais variaveis sustentam a extrapolacao.

## Modelo de dados esperado

O pipeline deve convergir para uma tabela municipal consolidada.

Colunas minimas recomendadas:

| Coluna | Descricao |
| --- | --- |
| `codigo_municipio` | Codigo IBGE do municipio |
| `municipio` | Nome do municipio |
| `score_total` | Score final de vulnerabilidade |
| `peso_vulnerabilidade` | Peso normalizado, com soma igual a 1 |
| `score_seca` | Componente de risco de seca |
| `score_enchente` | Componente de risco de enchente |
| `score_calor` | Componente de risco de calor |
| `score_capacidade_resposta` | Componente de capacidade de defesa ou resposta |
| `arquetipo` | Grupo/tipologia atribuida ao municipio |
| `tendencia_2030` | Indicador ou score projetado |

## Principios tecnicos

- Reprodutibilidade: qualquer resultado apresentado deve poder ser recalculado.
- Transparencia: pesos, fontes e transformacoes devem estar documentados.
- Auditabilidade: cada PR que muda metodologia deve explicar impacto nos scores.
- Separacao de responsabilidades: notebooks podem explorar, mas a regra final deve ir para `src/`.
- Dados seguros: dados brutos, grandes ou sensiveis ficam fora do Git.
- Baseline primeiro: entregar uma versao simples, testada e explicavel antes de aumentar a complexidade.

## Metodologia inicial

O baseline atual usa normalizacao min-max e media ponderada, conforme `docs/methodology.md`.

Para evoluir o produto, a equipe deve separar os indicadores em dimensoes:

- Perigo climatico: historico de seca, chuva extrema, calor, anomalias e frequencia de eventos.
- Exposicao: populacao, densidade, area urbana, infraestrutura critica e atividades economicas expostas.
- Vulnerabilidade social: renda, saneamento, saude, moradia, idade e outros fatores sociais.
- Capacidade de resposta: receita municipal, equipamentos publicos, defesa civil, acesso a servicos e infraestrutura.

Uma convencao importante:

- Indicadores de risco entram como `positive` quando valores maiores aumentam vulnerabilidade.
- Indicadores de capacidade entram como `negative` quando valores maiores reduzem vulnerabilidade.

## Backlog tecnico sugerido

1. Definir schema oficial da tabela municipal consolidada.
2. Criar ingestao dos datasets climaticos do INMET.
3. Criar agregacoes por municipio e por categoria de risco.
4. Adicionar indicadores socioeconomicos e de infraestrutura.
5. Implementar calculo de `peso_vulnerabilidade` com soma igual a 1.
6. Implementar calculadora de orcamento.
7. Criar exportacao CSV para ranking e alocacao.
8. Criar visualizacao inicial do mapa.
9. Implementar arquetipos por clustering ou regras explicaveis.
10. Criar projecao ate 2030 com metodologia documentada.

## Definicao de pronto

Uma entrega deve ser considerada pronta quando:

- Tem dados ou exemplo minimo para reproduzir.
- Tem regra implementada em `src/` quando for comportamento de produto.
- Tem teste automatizado quando alterar calculo, score, ranking ou alocacao.
- Atualiza `docs/data_dictionary.md` se adicionar dataset ou indicador.
- Atualiza `docs/methodology.md` se alterar a metodologia.
- Passa na CI do GitHub.

## Perguntas que a equipe precisa responder

- Quais indicadores entram no MVP e quais ficam fora?
- Como mapear medicoes de estacoes INMET para municipios sem estacao propria?
- Como ponderar seca, enchente e calor de forma defensavel?
- Como medir capacidade de resposta municipal?
- Como explicar o score para uma pessoa nao tecnica?
- Qual e o nivel minimo de confianca para recomendar alocacao de verba?

## Narrativa curta

O projeto transforma historico climatico e vulnerabilidade municipal em uma recomendacao objetiva de alocacao de orcamento. Em vez de dizer apenas se vai chover, ele ajuda a decidir onde investir primeiro para reduzir dano, proteger pessoas e aumentar resiliencia climatica na Bahia.


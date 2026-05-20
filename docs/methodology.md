# Metodologia

## Score baseline

O baseline calcula um score ponderado em escala de 0 a 100.

1. Cada indicador e normalizado com min-max.
2. Indicadores `positive` preservam a direcao: maior valor gera maior score.
3. Indicadores `negative` invertem a direcao: menor valor gera maior score.
4. O score final e a media ponderada dos indicadores normalizados.

## Score climatico (trilha principal)

Alem do baseline generico, o projeto entrega um indice de vulnerabilidade climatica que vira uma
calculadora de orcamento. Framework IPCC: `vulnerabilidade ~ ameaca / capacidade adaptativa`.

1. Sub-indices por estacao INMET (seca, enchente, calor) com indices ETCCDI, `-9999` -> NaN.
2. PCA aprende os pesos da ameaca composta (nao-supervisionado).
3. IDW interpola as 45 estacoes para os 417 centroides municipais (malha IBGE).
4. Capacidade adaptativa = IDHM; peso per capita = `ameaca / IDHM`, normalizado para somar 1.
5. KMeans gera arquetipos; projecao temporal (tendencia linear 2000-2021) estima o risco em 2030.

Detalhes completos em `docs/Plano.md`. A IA de linguagem (Claude) apenas explica o score, nao o calcula.

## Decisoes a validar

- Tratamento de nulos (`-9999` do INMET tratado como NaN; ano exige >=55% de dias validos).
- Tratamento de outliers (normalizacao robusta p5-p95 nos sub-indices climaticos).
- Pesos por tema (PCA data-driven por padrao; sliders no app re-normalizam para somar 1).
- Validacao com metricas externas (cruzar com S2iD/Atlas de Desastres e Monitor de Secas da ANA).
- Empates no ranking.
- Capacidade adaptativa: hoje IDHM 2010; extensivel com desemprego/cobertura de saude/PIB.


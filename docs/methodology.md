# Metodologia

## Score baseline

O baseline calcula um score ponderado em escala de 0 a 100.

1. Cada indicador e normalizado com min-max.
2. Indicadores `positive` preservam a direcao: maior valor gera maior score.
3. Indicadores `negative` invertem a direcao: menor valor gera maior score.
4. O score final e a media ponderada dos indicadores normalizados.

## Decisoes a validar

- Tratamento de nulos.
- Tratamento de outliers.
- Pesos por tema.
- Validacao com especialistas ou metricas externas.
- Empates no ranking.


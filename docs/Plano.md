# Plano — Calculadora de Orçamento Climático da Bahia

Solução para o desafio **"Resiliência Climática e Cidades Inteligentes na Bahia: Antecipando o
Futuro com IA"**.

> **É uma calculadora de orçamento.** Você informa quanto o estado tem para resiliência climática
> e ela devolve quanto vai para cada um dos 417 municípios, priorizando os mais vulneráveis.

Apresentação visual: https://termometro-climatico-bahia.surge.sh

---

## 1. O Problema

A Bahia vive dois extremos climáticos opostos: **secas no semiárido** e **enchentes urbanas**. O
orçamento público de resiliência é limitado e a decisão de **onde investir** é hoje política e
pouco baseada em dados. A maioria das soluções de IA para num "vai chover amanhã?" que não diz o
que fazer com a informação.

Nossa pergunta: **dado um orçamento, quais municípios merecem prioridade?**

---

## 2. A Solução

Um **índice de vulnerabilidade climática** para os 417 municípios + uma **calculadora** que
distribui o orçamento proporcionalmente ao risco. App em Streamlit com:

1. **Calculadora de orçamento** (tela principal): orçamento total → tabela com o R$ de cada
   município, exportável. Sliders priorizam seca, enchente ou calor.
2. **Mapa de risco**: coroplético dos 417 municípios, camadas por categoria e projeção 2030.
3. **Arquétipos & projeção**: tipologias de vulnerabilidade e tendência histórica.

---

## 3. IA não-supervisionada (o score emerge dos dados)

Não há "score verdadeiro" rotulado, então o motor é **100% não-supervisionado**:

- **PCA** aprende o peso de cada risco a partir da variância (pesos data-driven, não chutados).
- **KMeans** agrupa os municípios em arquétipos de vulnerabilidade.
- **Projeção temporal** ajusta a tendência de 21 anos e projeta o risco para 2030.
- **Claude (Haiku)** traduz os números em linguagem e recomenda gasto. A IA **não calcula o
  score**, só explica — honesto e auditável.

Evitamos "IA falsa": slider rotulado de IA, sentimento de notícia, chatbot que alucina.

---

## 4. Metodologia do Score (framework IPCC)

`vulnerabilidade ~ ameaça climática / capacidade adaptativa`

### 4.1 Sub-índices climáticos por estação (45 estações INMET, 2000-2021)
De 5,2M medições horárias. `-9999` → NaN; ≥55% de dias válidos por ano; janela comum.

- **Seca**: aridez (chuva anual baixa) + dias secos consecutivos (CDD) + déficit década-a-década.
- **Enchente**: Rx1day (máxima diária anual, ETCCDI) + dias/ano com chuva ≥ 50 mm.
- **Calor**: TX90p (excedência do p90 do período-base = aquecimento) + tendência da temperatura.

Cada sub-índice normalizado a [0,1] por percentil robusto (p5–p95).

### 4.2 Ameaça composta (PCA)
PCA sobre os 3 sub-índices padronizados → 1ª componente principal = ameaça (pesos aprendidos),
normalizada a [0,1].

### 4.3 Interpolação espacial (45 → 417)
IDW (k=5 vizinhas, potência=2) sobre os centroides da malha IBGE (`codarea`). Incerteza maior no
sertão oeste, sub-amostrado.

### 4.4 Capacidade adaptativa e peso per capita
- Capacidade adaptativa = **IDHM** (Atlas Brasil/PNUD).
- **Peso**: `peso_i = (ameaça_i / IDHM_i)` normalizado para **somar 1**.
- **Sem população crua** e **inversamente proporcional ao IDHM**: município com baixa capacidade de
  resposta sobe; cidade rica e de baixo risco (Salvador) cai. A verba segue a gravidade e a
  vulnerabilidade, não o tamanho da cidade.

### 4.5 Calculadora
`R$_município = orçamento_total × peso_município`. A soma fecha no orçamento.

### Validação (saída real do pipeline)
- **Salvador**: ameaça ≈ 0,00 (litoral chuvoso), peso ≈ 0.
- Maiores pesos: municípios pobres do sertão (Pilão Arcado, Lamarão, Umburanas), alta ameaça e
  baixo IDHM.
- Slider SECA → topo no sertão; slider ENCHENTE → litoral / Região Metropolitana.

---

## 5. Dados (públicos, sem login)

| Dataset | Uso | Fonte |
| --- | --- | --- |
| INMET histórico horário | sub-índices climáticos | Drive (549 MB, local, não versionado) |
| IBGE Malhas (GeoJSON) | polígonos dos 417 municípios | API v3, chave `codarea` |
| IBGE SIDRA | população 2021 | API v3 agregado 6579 |
| Atlas Brasil / PNUD | IDHM por município | CSV (`Codmun7`) |
| Open-Meteo | alerta de chuva 7-16 dias (opcional) | API sem chave |

CSV bruto do INMET (Drive): `https://drive.google.com/drive/folders/1DruOvNchljoSbAJyzR4TP6pTmVzLjQr8`

---

## 6. Estrutura no repositório

```
src/municipios_score/
  scoring.py            baseline generico (mantido)
  indices_climaticos.py sub-indices por estacao (ETCCDI, -9999 -> NaN)
  vulnerabilidade.py    PCA + IDW + capacidade + peso per-capita + calculadora
  arquetipos.py         KMeans (tipologias)
  projecao.py           projecao temporal 2026-2030
  ia.py                 Claude explica/recomenda (fallback offline)
  io.py                 caminhos e carregadores (data/processed -> examples/ fallback)
scripts/                baixar_municipios_ibge.py, build_scores.py
app.py                  app Streamlit (calculadora, mapa, arquetipos)
examples/               amostras versionaveis (scores, estacoes, malha, municipios)
tests/                  testes sinteticos (sem dataset/rede)
```

Reproduzir: `python scripts/baixar_municipios_ibge.py` e `python scripts/build_scores.py`;
`streamlit run app.py` sobe o app (extra `.[app]`).

---

## 7. Limitações honestas

- IDHM é de 2010 (último censo municipal oficial). A capacidade adaptativa é extensível: pode
  incorporar desemprego, cobertura de saúde e PIB per capita (indicadores que já existem no
  baseline `scoring.py`) sem mudar a fórmula.
- 45 estações para 417 municípios: IDW é defensável, incerteza maior no sertão oeste.
- A projeção é tendência linear honesta, não um modelo climático físico.
- Validação externa futura: cruzar com S2iD/Atlas de Desastres e Monitor de Secas (ANA).

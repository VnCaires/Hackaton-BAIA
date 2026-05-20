"""Caminhos e carregadores de dados do pipeline de vulnerabilidade climatica."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
EXAMPLES = ROOT / "examples"
OUTPUTS = ROOT / "outputs"

CLIMA_CSV = DATA_RAW / "clima_bahia.csv"
NA_SENTINEL = -9999.0

COL_ESTACAO = "ESTACAO"
COL_DATA = "DATA (YYYY-MM-DD)"
COL_PRECIP = "PRECIPITACAO TOTAL HORARIO (mm)"
COL_TEMP = "TEMPERATURA DO AR - BULBO SECO, HORARIA (C)"


def _primeiro_existente(*candidatos: Path) -> Path:
    for c in candidatos:
        if c.exists():
            return c
    return candidatos[-1]


def load_clima(usecols: list[str] | None = None) -> pd.DataFrame:
    return pd.read_csv(CLIMA_CSV, usecols=usecols, na_values=[NA_SENTINEL])


def load_estacoes() -> pd.DataFrame:
    caminho = _primeiro_existente(
        DATA_PROCESSED / "estacoes.csv", EXAMPLES / "estacoes_inmet_ba.csv"
    )
    return pd.read_csv(caminho)


def load_municipios() -> pd.DataFrame:
    caminho = _primeiro_existente(
        DATA_PROCESSED / "municipios.csv", EXAMPLES / "municipios_ba.csv"
    )
    return pd.read_csv(caminho, dtype={"codigo": str})


def load_scores() -> pd.DataFrame:
    caminho = _primeiro_existente(
        DATA_PROCESSED / "scores.csv", EXAMPLES / "scores_municipios.csv"
    )
    return pd.read_csv(caminho, dtype={"codigo": str})


def load_malha_geojson() -> dict:
    caminho = _primeiro_existente(
        DATA_PROCESSED / "ba.geojson", EXAMPLES / "ba_municipios.geojson"
    )
    return json.loads(caminho.read_text())


def load_indicadores_estacao() -> pd.DataFrame:
    caminho = _primeiro_existente(
        DATA_PROCESSED / "indicadores_estacao.csv", EXAMPLES / "indicadores_estacao.csv"
    )
    return pd.read_csv(caminho)


def load_indicadores_anuais() -> pd.DataFrame:
    caminho = _primeiro_existente(
        DATA_PROCESSED / "indicadores_anuais.csv", EXAMPLES / "indicadores_anuais.csv"
    )
    return pd.read_csv(caminho)

"""Orquestra o pipeline climatico e gera data/processed/scores.csv.

Etapas: indicadores por estacao -> vulnerabilidade (PCA+IDW+peso) -> arquetipos -> projecao.
Pre-requisitos: data/raw/clima_bahia.csv e scripts/baixar_municipios_ibge.py ja rodado.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from municipios_score import arquetipos, indices_climaticos, io, projecao, vulnerabilidade


def _tem_indicadores() -> bool:
    return any(
        (base / "indicadores_estacao.csv").exists() for base in (io.DATA_PROCESSED, io.EXAMPLES)
    )


def main() -> None:
    # so recomputa do CSV bruto (549MB) se os indicadores nao existirem em lugar nenhum;
    # caso contrario usa os de data/processed ou o fallback versionado em examples/.
    if not _tem_indicadores():
        print("indicadores ausentes; computando do CSV horario (data/raw/clima_bahia.csv)...")
        ind, anual = indices_climaticos.construir()
        io.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
        ind.to_csv(io.DATA_PROCESSED / "indicadores_estacao.csv", index=False)
        anual.to_csv(io.DATA_PROCESSED / "indicadores_anuais.csv", index=False)

    df = vulnerabilidade.montar_scores()
    df = arquetipos.classificar(df, k=4)
    df = projecao.projetar(df)
    io.DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(io.DATA_PROCESSED / "scores.csv", index=False)

    assert abs(df["peso"].sum() - 1.0) < 1e-9, "pesos nao somam 1"
    assert len(df) == 417, f"esperado 417 municipios, veio {len(df)}"
    print(f"OK: {len(df)} municipios, soma pesos = {df['peso'].sum():.6f}")
    print("arquetipos:", df["arquetipo"].value_counts().to_dict())
    print("tendencia:", df["tendencia"].value_counts().to_dict())


if __name__ == "__main__":
    main()

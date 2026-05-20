import numpy as np
import pandas as pd

from municipios_score.arquetipos import classificar
from municipios_score.projecao import _proxy_anual, _rotulo


def _df_sintetico(n: int = 40) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    return pd.DataFrame({
        "codigo": [str(i) for i in range(n)],
        "seca": rng.random(n),
        "enchente": rng.random(n),
        "calor": rng.random(n),
        "capacidade": rng.random(n),
    })


def test_classificar_adiciona_arquetipo_unico_por_cluster() -> None:
    df = classificar(_df_sintetico(), k=4)
    assert "arquetipo" in df.columns and "cluster" in df.columns
    # cada cluster mapeia para exatamente um rotulo
    por_cluster = df.groupby("cluster")["arquetipo"].nunique()
    assert (por_cluster == 1).all()


def test_classificar_cobre_todos_os_municipios() -> None:
    df = classificar(_df_sintetico(30), k=3)
    assert df["arquetipo"].notna().all()


def test_rotulo_tendencia_por_slope() -> None:
    assert _rotulo(0.1) == "Agravando"
    assert _rotulo(-0.1) == "Melhorando"
    assert _rotulo(0.0) == "Estavel"


def test_proxy_anual_gera_coluna_proxy() -> None:
    anual = pd.DataFrame({
        "estacao": ["A"] * 5,
        "ano": [2016, 2017, 2018, 2019, 2020],
        "precip_total": [800, 700, 600, 500, 400],
        "rx1day": [90, 85, 80, 70, 60],
        "tmax_media": [30, 30.2, 30.5, 30.8, 31.0],
    })
    proxy = _proxy_anual(anual)
    assert "proxy" in proxy.columns and proxy["proxy"].notna().all()

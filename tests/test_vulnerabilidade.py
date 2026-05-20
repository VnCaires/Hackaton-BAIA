import pandas as pd

from municipios_score import alocar, peso_per_capita
from municipios_score.vulnerabilidade import (
    hazard_por_pesos,
    idw,
    normalizar_robusto,
    subindices_estacao,
)


def test_normalizar_robusto_fica_em_zero_um() -> None:
    s = pd.Series([0, 10, 20, 30, 40, 50, 100])
    r = normalizar_robusto(s)
    assert r.min() >= 0.0 and r.max() <= 1.0


def test_peso_per_capita_soma_um() -> None:
    ameaca = pd.Series([0.2, 0.5, 0.9])
    capacidade = pd.Series([0.1, 0.4, 0.6])
    pesos = peso_per_capita(ameaca, capacidade)
    assert abs(pesos.sum() - 1.0) < 1e-9


def test_menor_capacidade_aumenta_peso() -> None:
    # mesma ameaca: quem tem MENOR capacidade adaptativa (IDHM) pesa mais
    ameaca = pd.Series([0.5, 0.5])
    capacidade = pd.Series([0.5, 0.8])  # IDHM
    pesos = peso_per_capita(ameaca, capacidade)
    assert pesos.iloc[0] > pesos.iloc[1]


def test_sertao_pesa_mais_que_capital() -> None:
    # sertao: ameaca alta + baixa capacidade; capital: ameaca baixa + alta capacidade
    ameaca = pd.Series([0.95, 0.05])
    capacidade = pd.Series([0.5, 0.8])  # IDHM
    pesos = peso_per_capita(ameaca, capacidade)
    assert pesos.iloc[0] > pesos.iloc[1]


def test_idw_ponto_sobre_estacao_retorna_valor_dela() -> None:
    valores = pd.DataFrame({"x": [1.0, 0.0]}, index=["A", "B"])
    origem = pd.DataFrame({"estacao": ["A", "B"], "lat": [-12.0, -10.0], "lon": [-40.0, -42.0]})
    destino = pd.DataFrame({"codigo": ["m1"], "lat": [-12.0], "lon": [-40.0]})
    out = idw(valores, origem, destino, k=2)
    assert abs(out.loc[0, "x"] - 1.0) < 1e-6


def test_idw_interpola_entre_estacoes() -> None:
    valores = pd.DataFrame({"x": [1.0, 0.0]}, index=["A", "B"])
    origem = pd.DataFrame({"estacao": ["A", "B"], "lat": [0.0, 0.0], "lon": [0.0, 2.0]})
    destino = pd.DataFrame({"codigo": ["m1"], "lat": [0.0], "lon": [1.0]})
    out = idw(valores, origem, destino, k=2)
    assert 0.0 < out.loc[0, "x"] < 1.0


def test_hazard_por_pesos_renormaliza_e_isola_categoria() -> None:
    df = pd.DataFrame({
        "seca": [0.1, 0.9], "enchente": [0.9, 0.1], "calor": [0.5, 0.5], "ameaca": [0.5, 0.5],
    })
    so_seca = hazard_por_pesos(df, 1.0, 0.0, 0.0)
    assert so_seca.iloc[1] > so_seca.iloc[0]  # quem tem mais seca pesa mais


def test_hazard_pesos_zerados_usa_ameaca() -> None:
    df = pd.DataFrame({"seca": [0.3], "enchente": [0.3], "calor": [0.3], "ameaca": [0.7]})
    assert hazard_por_pesos(df, 0.0, 0.0, 0.0).iloc[0] == 0.7


def test_limiar_contemplacao_zera_baixo_risco() -> None:
    from municipios_score.vulnerabilidade import LIMIAR_CONTEMPLACAO

    abaixo = LIMIAR_CONTEMPLACAO / 2
    ameaca = pd.Series([abaixo, 0.9])  # primeiro abaixo do limiar -> nao contemplado
    capacidade = pd.Series([0.6, 0.6])
    pesos = peso_per_capita(ameaca, capacidade)
    assert pesos.iloc[0] == 0.0
    assert abs(pesos.sum() - 1.0) < 1e-9  # soma 1 entre os contemplados


def test_alocar_distribui_todo_orcamento() -> None:
    df = pd.DataFrame({
        "codigo": ["1", "2", "3"], "nome": ["A", "B", "C"], "populacao": [100, 200, 300],
        "idhm": [0.6, 0.7, 0.5], "ameaca": [0.2, 0.5, 0.9], "peso": [0.2, 0.3, 0.5],
    })
    aloc = alocar(df, 1_000_000)
    assert abs(aloc["valor_rs"].sum() - 1_000_000) < 1e-3
    assert aloc.iloc[0]["valor_rs"] >= aloc.iloc[-1]["valor_rs"]  # ordenado desc


def test_subindices_ficam_em_zero_um() -> None:
    ind = pd.DataFrame({
        "estacao": ["A", "B", "C", "D"],
        "precip_anual": [300, 800, 1500, 600],
        "cdd": [180, 60, 30, 120],
        "deficit_decada": [0.3, 0.1, 0.0, 0.2],
        "rx1day": [40, 90, 130, 60],
        "dias_chuva_forte": [1, 3, 6, 2],
        "dias_quentes_pct": [0.18, 0.12, 0.09, 0.14],
        "temp_trend": [0.4, 0.2, -0.1, 0.3],
    })
    sub = subindices_estacao(ind)
    for col in ("seca", "enchente", "calor"):
        assert sub[col].min() >= 0.0 and sub[col].max() <= 1.0

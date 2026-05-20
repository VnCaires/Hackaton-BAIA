import pandas as pd

from municipios_score.indices_climaticos import _max_dias_secos, tabela_anual


def test_max_dias_secos_conta_maior_sequencia() -> None:
    chuva = pd.Series([0.0, 0.0, 5.0, 0.0, 0.0, 0.0, 2.0])
    assert _max_dias_secos(chuva) == 3


def test_max_dias_secos_tudo_chuvoso() -> None:
    assert _max_dias_secos(pd.Series([2.0, 3.0, 1.5])) == 0


def test_tabela_anual_extrai_indicadores() -> None:
    datas = pd.date_range("2015-01-01", periods=300, freq="D")
    chuva = [0.0] * 300
    chuva[10] = 120.0  # Rx1day
    chuva[20] = 60.0   # dia de chuva forte (>=50)
    diario = pd.DataFrame({
        "estacao": "A", "data": datas, "ano": 2015,
        "precip": chuva, "tmax": [30.0] * 300, "tmedia": [25.0] * 300,
    })
    anual = tabela_anual(diario)
    linha = anual.iloc[0]
    assert linha["rx1day"] == 120.0
    assert linha["dias_chuva_forte"] == 2  # 120 e 60 mm


def test_tabela_anual_descarta_ano_incompleto() -> None:
    datas = pd.date_range("2015-01-01", periods=50, freq="D")  # < MIN_DIAS_VALIDOS
    diario = pd.DataFrame({
        "estacao": "A", "data": datas, "ano": 2015,
        "precip": [1.0] * 50, "tmax": [30.0] * 50, "tmedia": [25.0] * 50,
    })
    assert len(tabela_anual(diario)) == 0

import pandas as pd
import pytest

from municipios_score import ScoreIndicator, calculate_municipality_scores
from municipios_score.scoring import normalize_indicator


def test_normalize_positive_indicator() -> None:
    result = normalize_indicator(pd.Series([10, 20, 30]), "positive")

    assert result.tolist() == [0.0, 0.5, 1.0]


def test_normalize_negative_indicator() -> None:
    result = normalize_indicator(pd.Series([10, 20, 30]), "negative")

    assert result.tolist() == [1.0, 0.5, 0.0]


def test_calculate_scores_orders_best_municipality_first() -> None:
    data = pd.DataFrame(
        {
            "codigo_municipio": [1, 2],
            "municipio": ["A", "B"],
            "idhm": [0.8, 0.6],
            "taxa_desemprego": [5, 10],
        }
    )

    result = calculate_municipality_scores(
        data,
        indicators=[
            ScoreIndicator("idhm", 0.6, "positive"),
            ScoreIndicator("taxa_desemprego", 0.4, "negative"),
        ],
        id_col="codigo_municipio",
    )

    assert result.loc[0, "municipio"] == "A"
    assert result.loc[0, "score"] == 100.0
    assert result.loc[0, "rank"] == 1


def test_missing_columns_raise_clear_error() -> None:
    data = pd.DataFrame({"municipio": ["A"], "idhm": [0.8]})

    with pytest.raises(ValueError, match="missing columns: taxa_desemprego"):
        calculate_municipality_scores(
            data,
            indicators=[
                ScoreIndicator("idhm", 1.0),
                ScoreIndicator("taxa_desemprego", 1.0),
            ],
        )


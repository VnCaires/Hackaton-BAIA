from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

import numpy as np
import pandas as pd

Direction = Literal["positive", "negative"]


@dataclass(frozen=True)
class ScoreIndicator:
    column: str
    weight: float
    direction: Direction = "positive"


def normalize_indicator(series: pd.Series, direction: Direction = "positive") -> pd.Series:
    if direction not in {"positive", "negative"}:
        raise ValueError("direction must be 'positive' or 'negative'")

    numeric = pd.to_numeric(series, errors="coerce")
    min_value = numeric.min(skipna=True)
    max_value = numeric.max(skipna=True)

    if pd.isna(min_value) or pd.isna(max_value):
        return pd.Series(np.nan, index=series.index, dtype="float64")

    if min_value == max_value:
        normalized = pd.Series(1.0, index=series.index, dtype="float64")
    else:
        normalized = (numeric - min_value) / (max_value - min_value)

    if direction == "negative":
        normalized = 1 - normalized

    return normalized


def calculate_municipality_scores(
    data: pd.DataFrame,
    indicators: Iterable[ScoreIndicator],
    municipality_col: str = "municipio",
    id_col: str | None = None,
) -> pd.DataFrame:
    indicator_list = list(indicators)
    _validate_inputs(data, indicator_list, municipality_col, id_col)

    result = data.copy()
    total_weight = sum(indicator.weight for indicator in indicator_list)
    weighted_sum = pd.Series(0.0, index=result.index, dtype="float64")

    for indicator in indicator_list:
        normalized_col = f"{indicator.column}_score"
        result[normalized_col] = normalize_indicator(result[indicator.column], indicator.direction)
        weighted_sum += result[normalized_col].fillna(0) * indicator.weight

    result["score"] = (weighted_sum / total_weight * 100).round(2)
    result["rank"] = result["score"].rank(method="dense", ascending=False).astype(int)

    columns = []
    if id_col:
        columns.append(id_col)
    columns.extend([municipality_col, "score", "rank"])
    columns.extend(f"{indicator.column}_score" for indicator in indicator_list)

    return result[columns].sort_values(["rank", municipality_col]).reset_index(drop=True)


def _validate_inputs(
    data: pd.DataFrame,
    indicators: list[ScoreIndicator],
    municipality_col: str,
    id_col: str | None,
) -> None:
    if not indicators:
        raise ValueError("at least one indicator is required")

    required_columns = {municipality_col, *(indicator.column for indicator in indicators)}
    if id_col:
        required_columns.add(id_col)

    missing_columns = sorted(required_columns - set(data.columns))
    if missing_columns:
        raise ValueError(f"missing columns: {', '.join(missing_columns)}")

    invalid_weights = [indicator.column for indicator in indicators if indicator.weight <= 0]
    if invalid_weights:
        raise ValueError(f"weights must be positive: {', '.join(invalid_weights)}")

    invalid_directions = [
        indicator.column
        for indicator in indicators
        if indicator.direction not in {"positive", "negative"}
    ]
    if invalid_directions:
        raise ValueError(f"invalid directions: {', '.join(invalid_directions)}")


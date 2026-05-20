from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from municipios_score.scoring import ScoreIndicator, calculate_municipality_scores


def main() -> None:
    parser = argparse.ArgumentParser(description="Calcula scores de municipios.")
    parser.add_argument("input_csv", type=Path, help="CSV com indicadores municipais.")
    parser.add_argument("config_json", type=Path, help="JSON com indicadores, pesos e direcoes.")
    parser.add_argument("output_csv", type=Path, help="Destino do CSV com scores.")
    args = parser.parse_args()

    config = _load_config(args.config_json)
    data = pd.read_csv(args.input_csv)
    scores = calculate_municipality_scores(
        data,
        indicators=[
            ScoreIndicator(
                column=indicator["column"],
                weight=float(indicator["weight"]),
                direction=indicator.get("direction", "positive"),
            )
            for indicator in config["indicators"]
        ],
        municipality_col=config.get("municipality_col", "municipio"),
        id_col=config.get("id_col"),
    )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    scores.to_csv(args.output_csv, index=False)


def _load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    main()


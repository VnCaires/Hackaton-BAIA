from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cria um recorte comprimido do dataset climatico para desenvolvimento."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/clima_bahia_hackathon(1).csv"),
        help="CSV bruto baixado do Google Drive.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/sample/clima_bahia_2020.csv.gz"),
        help="Arquivo de saida versionavel.",
    )
    parser.add_argument("--year", type=int, default=2020, help="Ano completo a extrair.")
    parser.add_argument("--chunksize", type=int, default=250_000)
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(f"Arquivo bruto nao encontrado: {args.input}")

    args.output.parent.mkdir(parents=True, exist_ok=True)

    first_chunk = True
    rows = 0
    stations: set[str] = set()

    for chunk in pd.read_csv(args.input, chunksize=args.chunksize):
        dates = pd.to_datetime(chunk["DATA (YYYY-MM-DD)"], errors="coerce")
        sample = chunk[dates.dt.year == args.year]
        if sample.empty:
            continue

        sample.to_csv(
            args.output,
            index=False,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            compression="gzip",
        )
        first_chunk = False
        rows += len(sample)
        stations.update(sample["ESTACAO"].dropna().astype(str).unique())

    if rows == 0:
        raise ValueError(f"Nenhuma linha encontrada para o ano {args.year}")

    print(f"Arquivo criado: {args.output}")
    print(f"Ano: {args.year}")
    print(f"Linhas: {rows}")
    print(f"Estacoes: {len(stations)}")


if __name__ == "__main__":
    main()


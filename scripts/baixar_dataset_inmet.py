"""Baixa o CSV bruto do INMET (549 MB) usado para recomputar os indicadores.

NAO e necessario para rodar o app nem o build: os indicadores ja vem prontos em
`examples/`. Use so para reprocessar os sub-indices climaticos do zero.

Fontes (qualquer uma):
- GitHub Release (mirror zipado): release `dataset-v1`, asset `clima_bahia.csv.gz`
- Google Drive (oficial do hackathon): pasta 01_DADOS_OFICIAIS

Uso:
    python scripts/baixar_dataset_inmet.py            # tenta o release, cai pro Drive
    python scripts/baixar_dataset_inmet.py --drive    # forca o Drive (precisa de gdown)
"""
from __future__ import annotations

import gzip
import shutil
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINO = ROOT / "data" / "raw" / "clima_bahia.csv"
RELEASE_GZ = (
    "https://github.com/VnCaires/Hackaton-BAIA/releases/download/dataset-v1/clima_bahia.csv.gz"
)
DRIVE_FOLDER = "https://drive.google.com/drive/folders/1DruOvNchljoSbAJyzR4TP6pTmVzLjQr8"


def _baixar_release() -> bool:
    gz = DESTINO.with_suffix(".csv.gz")
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    try:
        print(f"baixando do GitHub Release...\n{RELEASE_GZ}")
        urllib.request.urlretrieve(RELEASE_GZ, gz)
        with gzip.open(gz, "rb") as f_in, DESTINO.open("wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
        gz.unlink()
        print(f"OK -> {DESTINO}")
        return True
    except Exception as e:
        print(f"release indisponivel ({e}); tentando o Drive...")
        return False


def _baixar_drive() -> None:
    try:
        import gdown
    except ImportError:
        sys.exit("instale gdown:  pip install gdown")
    gdown.download_folder(DRIVE_FOLDER, output=str(DESTINO.parent), quiet=False, use_cookies=False)
    print(f"baixado do Drive em {DESTINO.parent} (renomeie o CSV para clima_bahia.csv se preciso)")


def main() -> None:
    if "--drive" in sys.argv:
        _baixar_drive()
    elif not _baixar_release():
        _baixar_drive()


if __name__ == "__main__":
    main()

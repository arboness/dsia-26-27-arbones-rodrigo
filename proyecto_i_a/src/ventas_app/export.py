"""Escritura de resultados a disco."""
import json
from pathlib import Path
import pandas as pd

def export_to_csv(df: pd.DataFrame, path: Path | str) -> None:
    """Guarda ``df`` como CSV (sin índice), creando la carpeta si no existe."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def export_json(data: dict, path: Path | str) -> None:
    """Guarda ``data`` como JSON legible (UTF-8, indentado), creando la carpeta si no existe."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, mode="w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

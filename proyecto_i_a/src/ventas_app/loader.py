"""Carga de ficheros de ventas."""

from pathlib import Path

import pandas as pd

from ventas_app.constants import VALID_EXTENSIONS
from ventas_app.exceptions import DataLoadError


def load_file(route: Path | str) -> pd.DataFrame:
    """Carga un fichero tabular (CSV/TXT o JSON) en un DataFrame.

    Args:
        route: ruta al fichero.

    Returns:
        DataFrame con el contenido del fichero, sin transformar.

    Raises:
        DataLoadError: si la ruta está vacía, no existe, no es un fichero
            o su extensión no está en ``VALID_EXTENSIONS``.
    """
    if route is None or str(route).strip() == "":
        raise DataLoadError("The route is empty.")

    route = Path(route)

    if not route.is_file():
        raise DataLoadError(f"The route {route} is not valid.")

    suffix = route.suffix.lower()
    if suffix not in VALID_EXTENSIONS:
        raise DataLoadError(
            f"The extension {route.suffix} is not allowed. Allowed extensions: {sorted(VALID_EXTENSIONS)}."
        )

    if suffix == ".json":
        return pd.read_json(route)
    return pd.read_csv(route)

"""Carga de canciones guardadas de Spotify.

Acepta dos formatos:

- ``.json``: respuesta cruda del endpoint ``GET /me/tracks`` de la Web API
  (lista de ``{"added_at": ..., "track": {...}}``, o un dict con clave ``items``).
  Se aplana a una tabla con :func:`flatten_saved_tracks`.
- ``.csv``: la tabla ya aplanada (p. ej. ``data/saved_tracks.csv``).
"""

import json
from pathlib import Path

import pandas as pd

from spotify_app.constants import ARTIST_SEP, COLUMNS, VALID_EXTENSIONS
from spotify_app.exceptions import DataLoadError


def flatten_saved_tracks(items: list[dict]) -> pd.DataFrame:
    """Convierte la lista de la API en una tabla con una fila por canción.

    Solo se conservan metadatos del catálogo y la fecha de guardado
    (nada de datos del usuario). Los campos ausentes quedan como nulos para
    que el validador los detecte.
    """
    rows = []
    for item in items:
        track = item.get("track") or {}
        album = track.get("album") or {}
        artists = [a.get("name") for a in track.get("artists") or [] if a.get("name")]
        rows.append({
            "added_at": item.get("added_at"),
            "track_id": track.get("id"),
            "track_name": track.get("name"),
            "artists": ARTIST_SEP.join(artists) or None,
            "main_artist": artists[0] if artists else None,
            "album_name": album.get("name"),
            "album_type": album.get("album_type"),
            "release_date": album.get("release_date"),
            "release_date_precision": album.get("release_date_precision"),
            "duration_ms": track.get("duration_ms"),
            "explicit": track.get("explicit"),
            "is_local": track.get("is_local"),
        })
    return pd.DataFrame(rows, columns=COLUMNS)


def _read_json_items(route: Path) -> list[dict]:
    try:
        data = json.loads(route.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise DataLoadError(f"The file {route} is not valid JSON: {e.msg}.") from e

    if isinstance(data, dict) and "items" in data:
        data = data["items"]
    if not isinstance(data, list):
        raise DataLoadError(f"The file {route} must contain a list of saved tracks.")
    return data


def load_saved_tracks(route: Path | str) -> pd.DataFrame:
    """Carga canciones guardadas desde JSON de la API o CSV ya aplanado.

    Raises:
        DataLoadError: ruta vacía o inexistente, extensión no permitida,
            JSON mal formado o con una estructura inesperada.
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
        return flatten_saved_tracks(_read_json_items(route))
    return pd.read_csv(route)

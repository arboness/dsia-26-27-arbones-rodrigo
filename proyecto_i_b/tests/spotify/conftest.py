import json
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_CSV = PROJECT_ROOT / "data" / "saved_tracks.csv"


def api_item(track_id="t1", name="Song", artists=("Artist A",), added_at="2024-05-01T10:00:00Z",
             release_date="2020-01-15", duration_ms=200_000, explicit=False, is_local=False):
    """Un elemento con la forma de la respuesta de GET /me/tracks."""
    return {
        "added_at": added_at,
        "track": {
            "id": track_id,
            "name": name,
            "artists": [{"name": a} for a in artists],
            "album": {
                "name": "Album",
                "album_type": "album",
                "release_date": release_date,
                "release_date_precision": "day",
            },
            "duration_ms": duration_ms,
            "explicit": explicit,
            "is_local": is_local,
        },
    }


@pytest.fixture
def sample_csv():
    """Ruta a la muestra real versionada (solo para tests de integración)."""
    return SAMPLE_CSV


@pytest.fixture
def api_items():
    """4 canciones en formato API: 2 válidas, 1 duplicada y 1 local sin id."""
    return [
        api_item("t1", "Song 1", ("Artist A", "Artist B"), duration_ms=180_000, explicit=True),
        api_item("t2", "Song 2", ("Artist A",), added_at="2025-02-01T09:00:00Z", release_date="1999"),
        api_item("t1", "Song 1 again", ("Artist A",)),
        api_item(None, "Local file", ("Me",), is_local=True),
    ]


@pytest.fixture
def api_json(tmp_path, api_items):
    """``api_items`` guardado como JSON en una carpeta temporal."""
    path = tmp_path / "saved.json"
    path.write_text(json.dumps(api_items), encoding="utf-8")
    return path


@pytest.fixture
def tracks_df():
    """Tabla aplanada mínima con una canción válida."""
    return pd.DataFrame({
        "added_at": ["2024-05-01T10:00:00Z"],
        "track_id": ["t1"],
        "track_name": ["Song"],
        "artists": ["Artist A"],
        "main_artist": ["Artist A"],
        "album_name": ["Album"],
        "album_type": ["album"],
        "release_date": ["2020-01-15"],
        "release_date_precision": ["day"],
        "duration_ms": [200_000],
        "explicit": [False],
        "is_local": [False],
    })


@pytest.fixture
def valid_tracks():
    """Canciones ya validadas (con release_year y duration_min) para probar métricas."""
    return pd.DataFrame({
        "added_at": ["2023-01-10T00:00:00Z", "2023-06-01T00:00:00Z", "2024-02-02T00:00:00Z", "2024-03-03T00:00:00Z"],
        "track_id": ["a", "b", "c", "d"],
        "artists": ["X; Y", "X", "Z", "Y"],
        "explicit": [True, False, False, True],
        "release_year": [1995, 1999, 2012, 2018],
        "duration_min": [4.0, 3.0, 2.0, 5.0],
    })

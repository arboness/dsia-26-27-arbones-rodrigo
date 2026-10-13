"""Genera data/saved_tracks.csv a partir del JSON crudo descargado de la API.

Uso (desde proyecto_i_b/):
    python scripts/download_spotify.py      # 1. descarga spotify_data/ (requiere .env)
    python scripts/build_sample.py          # 2. aplana y guarda la muestra versionable

La muestra solo contiene metadatos públicos del catálogo (canción, artistas,
álbum, fechas, duración) y la fecha en que se guardó cada canción: ni email,
ni id de usuario, ni playlists.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spotify_app.export import export_to_csv  # noqa: E402
from spotify_app.loader import load_saved_tracks  # noqa: E402

RAW = ROOT / "spotify_data" / "canciones_guardadas.json"
SAMPLE = ROOT / "data" / "saved_tracks.csv"
MAX_ROWS = 5_000


def main() -> None:
    df = load_saved_tracks(RAW).head(MAX_ROWS)
    export_to_csv(df, SAMPLE)
    print(f"{len(df)} rows -> {SAMPLE}")


if __name__ == "__main__":
    main()

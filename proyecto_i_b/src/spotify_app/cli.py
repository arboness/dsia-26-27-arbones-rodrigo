"""Punto de entrada del pipeline de Spotify.

Uso:
    python -m spotify_app.cli --input data/saved_tracks.csv --output salida/saved_tracks_clean.csv

``--input`` puede ser el CSV de muestra o el JSON crudo de la API
(``spotify_data/canciones_guardadas.json``). En la carpeta de ``--output`` se
escriben también el informe de calidad, las filas inválidas y las métricas.
"""

import argparse
import sys
from pathlib import Path

from spotify_app.constants import (
    DECADES_FILE,
    INVALID_FILE,
    QUALITY_FILE,
    SAVES_PER_YEAR_FILE,
    TOP_ARTISTS_FILE,
)
from spotify_app.exceptions import SpotifyPipelineError
from spotify_app.export import export_json, export_to_csv
from spotify_app.loader import load_saved_tracks
from spotify_app.metrics import quality_report, saves_per_year, top_artists, tracks_by_decade
from spotify_app.validator import saved_tracks_validator


def build_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos del CLI."""
    parser = argparse.ArgumentParser(
        prog="spotify_app",
        description="Valida canciones guardadas de Spotify y calcula métricas de la biblioteca.",
    )
    parser.add_argument("--input", required=True, type=Path, help="CSV aplanado o JSON de la API")
    parser.add_argument("--output", required=True, type=Path, help="CSV limpio de salida")
    return parser


def run(input_path: Path, output_path: Path) -> dict:
    """Ejecuta el pipeline completo y devuelve el informe de calidad."""
    df = load_saved_tracks(input_path)
    valid, invalid = saved_tracks_validator(df)
    report = quality_report(df, valid, invalid)

    out_dir = output_path.parent
    export_to_csv(valid, output_path)
    export_to_csv(invalid, out_dir / INVALID_FILE)
    export_json(report, out_dir / QUALITY_FILE)
    export_to_csv(top_artists(valid), out_dir / TOP_ARTISTS_FILE)
    export_to_csv(saves_per_year(valid), out_dir / SAVES_PER_YEAR_FILE)
    export_to_csv(tracks_by_decade(valid), out_dir / DECADES_FILE)
    return report


def main(argv: list[str] | None = None) -> int:
    """Lee argumentos, ejecuta el pipeline y devuelve el código de salida (0 OK, 1 error de dominio)."""
    args = build_parser().parse_args(argv)

    try:
        report = run(args.input, args.output)
    except SpotifyPipelineError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(
        f"OK: {report['filas_validas']} valid tracks, {report['filas_invalidas']} invalid tracks "
        f"-> {args.output.parent}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

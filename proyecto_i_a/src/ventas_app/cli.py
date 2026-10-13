"""Punto de entrada del pipeline de ventas.

Uso:
    python -m ventas_app.cli --input Datos/ventas.csv --output salida/ventas_limpias.csv

Escribe el CSV limpio en ``--output`` y, en la misma carpeta, el informe de
calidad (JSON) y las métricas (CSV).
"""

import argparse
import sys
from pathlib import Path

from ventas_app.constants import (
    QUALITY_FILE,
    RECURRING_CLIENTS_FILE,
    REGION_FILE,
    TOP_PRODUCTS_FILE,
    WEEKLY_FILE,
)
from ventas_app.exceptions import SalesPipelineError
from ventas_app.export import export_json, export_to_csv
from ventas_app.loader import load_file
from ventas_app.metrics import (
    quality_report,
    recurring_clients,
    sales_by_region,
    top_products,
    weekly_sales,
)
from ventas_app.validator import sales_validator


def build_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos del CLI."""
    parser = argparse.ArgumentParser(
        prog="ventas_app",
        description="Valida un CSV de ventas y calcula métricas de negocio.",
    )
    parser.add_argument("--input", required=True, type=Path, help="CSV de entrada, p. ej. Datos/ventas.csv")
    parser.add_argument("--output", required=True, type=Path, help="CSV limpio de salida, p. ej. salida/ventas_limpias.csv")
    return parser


def run(input_path: Path, output_path: Path) -> dict:
    """Ejecuta el pipeline completo y devuelve el informe de calidad."""
    df = load_file(input_path)
    valid, invalid = sales_validator(df)

    out_dir = output_path.parent
    report = quality_report(df, valid, invalid)

    export_to_csv(valid, output_path)
    export_json(report, out_dir / QUALITY_FILE)
    export_to_csv(sales_by_region(valid), out_dir / REGION_FILE)
    export_to_csv(weekly_sales(valid), out_dir / WEEKLY_FILE)
    export_to_csv(top_products(valid), out_dir / TOP_PRODUCTS_FILE)
    export_to_csv(recurring_clients(valid), out_dir / RECURRING_CLIENTS_FILE)
    return report


def main(argv: list[str] | None = None) -> int:
    """Lee argumentos, ejecuta el pipeline y devuelve el código de salida.

    Returns:
        0 si todo va bien, 1 si hay un error de dominio (carga o validación).
        argparse sale con código 2 si faltan argumentos.
    """
    args = build_parser().parse_args(argv)

    try:
        report = run(args.input, args.output)
    except SalesPipelineError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(
        f"OK: {report['filas_validas']} valid rows, {report['filas_invalidas']} invalid rows "
        f"-> {args.output.parent}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

import json

import pandas as pd
import pytest

from ventas_app.cli import build_parser, main

EXPECTED_FILES = [
    "ventas_limpias.csv",
    "quality.json",
    "sales_by_region.csv",
    "weekly_sales.csv",
    "top_products.csv",
    "recurring_clients.csv",
]


def test_parser_reads_input_and_output():
    args = build_parser().parse_args(["--input", "a.csv", "--output", "out/b.csv"])
    assert args.input.name == "a.csv"
    assert args.output.parent.name == "out"


def test_parser_requires_arguments():
    with pytest.raises(SystemExit) as exc:
        build_parser().parse_args([])
    assert exc.value.code == 2


def test_main_smoke_writes_all_outputs(tmp_path, sales_csv, capsys):
    # Arrange
    out_dir = tmp_path / "salida"
    output = out_dir / "ventas_limpias.csv"
    # Act
    code = main(["--input", str(sales_csv), "--output", str(output)])
    # Assert
    assert code == 0
    for name in EXPECTED_FILES:
        assert (out_dir / name).is_file(), name
    assert len(pd.read_csv(output)) == 1
    assert "OK: 1 valid rows, 2 invalid rows" in capsys.readouterr().out


def test_main_returns_1_when_input_missing(tmp_path, capsys):
    code = main(["--input", str(tmp_path / "nope.csv"), "--output", str(tmp_path / "out.csv")])
    assert code == 1
    assert "Error" in capsys.readouterr().err


def test_main_returns_1_when_columns_missing(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text("fecha,region\n2026-01-01,Norte\n")
    assert main(["--input", str(bad), "--output", str(tmp_path / "out.csv")]) == 1


@pytest.mark.integration
def test_main_on_course_csv(tmp_path, course_csv):
    output = tmp_path / "ventas_limpias.csv"
    assert main(["--input", str(course_csv), "--output", str(output)]) == 0
    report = json.loads((tmp_path / "quality.json").read_text(encoding="utf-8"))
    assert report["filas_validas"] == 140
    assert report["filas_invalidas"] == 10

import pytest

from ventas_app.exceptions import DataLoadError
from ventas_app.loader import load_file
from ventas_app.validator import sales_validator


def test_loads_valid_csv(sales_csv, sales_mini):
    # Arrange: sales_csv es sales_mini guardado en tmp_path
    # Act
    df = load_file(sales_csv)
    # Assert
    assert df.shape == sales_mini.shape
    assert list(df.columns) == list(sales_mini.columns)


def test_accepts_path_as_string(sales_csv):
    df = load_file(str(sales_csv))
    assert len(df) == 3


def test_loads_json(tmp_path, sales_mini):
    path = tmp_path / "ventas.json"
    sales_mini.to_json(path, orient="records")
    df = load_file(path)
    assert len(df) == 3
    assert "precio_unitario" in df.columns


def test_missing_path_raises_data_load_error(tmp_path):
    with pytest.raises(DataLoadError, match="not valid"):
        load_file(tmp_path / "does_not_exist.csv")


@pytest.mark.parametrize("route", ["", "   ", None])
def test_empty_path_raises_data_load_error(route):
    with pytest.raises(DataLoadError, match="empty"):
        load_file(route)


def test_invalid_extension_raises_data_load_error(tmp_path):
    path = tmp_path / "ventas.xlsx"
    path.write_text("a,b\n1,2\n")
    with pytest.raises(DataLoadError, match="extension"):
        load_file(path)


@pytest.mark.integration
def test_course_csv_has_140_valid_and_10_invalid(course_csv):
    df = load_file(course_csv)
    valid, invalid = sales_validator(df)
    assert len(df) == 150
    assert len(valid) == 140
    assert len(invalid) == 10

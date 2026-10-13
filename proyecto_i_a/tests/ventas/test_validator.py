import pandas as pd
import pytest

from ventas_app.exceptions import ValidationError
from ventas_app.validator import SalesValidator, sales_validator


def make_sale(units, price):
    """Una sola venta con las unidades y el precio indicados."""
    return pd.DataFrame({
        "fecha": ["2026-01-01"],
        "region": ["Norte"],
        "producto": ["A"],
        "unidades": [units],
        "precio_unitario": [price],
        "cliente_id": ["C1"],
    })


def test_sales_mini_has_1_valid_row(sales_mini):
    valid, _ = sales_validator(sales_mini)
    assert len(valid) == 1


def test_sales_mini_has_2_invalid_rows(sales_mini):
    _, invalid = sales_validator(sales_mini)
    assert len(invalid) == 2


def test_no_rows_are_lost(sales_mini):
    valid, invalid = sales_validator(sales_mini)
    assert len(valid) + len(invalid) == len(sales_mini)


def test_amount_only_in_valid_rows(sales_mini):
    valid, invalid = sales_validator(sales_mini)
    assert valid["importe"].tolist() == [20.0]
    assert "importe" not in invalid.columns


def test_input_dataframe_is_not_modified(sales_mini):
    before = sales_mini.copy()
    sales_validator(sales_mini)
    pd.testing.assert_frame_equal(sales_mini, before)


def test_missing_column_raises_validation_error(sales_mini):
    with pytest.raises(ValidationError, match="precio_unitario"):
        sales_validator(sales_mini.drop(columns="precio_unitario"))


@pytest.mark.parametrize(
    ("price", "is_valid"),
    [
        (0, False),
        (-1, False),
        (None, False),
        ("abc", False),
        (1, True),
    ],
)
def test_price_edge_cases(price, is_valid):
    valid, invalid = sales_validator(make_sale(3, price))
    assert len(valid) == int(is_valid)
    assert len(invalid) == int(not is_valid)


@pytest.mark.parametrize(
    ("units", "is_valid"),
    [
        (0, False),
        (-2, False),
        (None, False),
        (1, True),
    ],
)
def test_units_edge_cases(units, is_valid):
    valid, _ = sales_validator(make_sale(units, 10.0))
    assert len(valid) == int(is_valid)


def test_valid_mask_marks_each_row(sales_mini):
    mask = SalesValidator().valid_mask(sales_mini)
    assert mask.tolist() == [True, False, False]

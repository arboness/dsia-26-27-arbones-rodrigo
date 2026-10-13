import pandas as pd

from ventas_app.metrics import (
    quality_report,
    recurring_clients,
    sales_by_region,
    top_products,
    weekly_sales,
)


def test_sales_by_region_sums_and_sorts_desc(valid_sales):
    # Act
    result = sales_by_region(valid_sales)
    # Assert: Norte 20+30, Sur 50+1, Este 20
    assert result["region"].tolist() == ["Sur", "Norte", "Este"]
    assert result["importe"].tolist() == [51.0, 50.0, 20.0]


def test_top_products_returns_n_best(valid_sales):
    result = top_products(valid_sales, n=2)
    assert result["producto"].tolist() == ["B", "A"]
    assert result["importe"].tolist() == [51.0, 50.0]


def test_weekly_sales_groups_by_week(valid_sales):
    result = weekly_sales(valid_sales)
    # Semana que acaba el 11-01: 20+50+30; semana que acaba el 18-01: 20+1
    assert result["importe_semanal"].tolist() == [100.0, 21.0]
    assert result["fecha"].dt.strftime("%Y-%m-%d").tolist() == ["2026-01-11", "2026-01-18"]


def test_weekly_sales_drops_bad_dates(valid_sales):
    data = valid_sales.copy()
    data.loc[0, "fecha"] = "no-es-fecha"
    assert weekly_sales(data)["importe_semanal"].sum() == 101.0


def test_recurring_clients_only_more_than_one_purchase(valid_sales):
    result = recurring_clients(valid_sales)
    assert result["cliente_id"].tolist() == ["C1", "C2"]
    assert result["n_compras"].tolist() == [2, 2]


def test_quality_report(sales_mini):
    valid = sales_mini.iloc[[0]].assign(importe=[20.0])
    invalid = sales_mini.iloc[[1, 2]]
    assert quality_report(sales_mini, valid, invalid) == {
        "filas_totales": 3,
        "filas_validas": 1,
        "filas_invalidas": 2,
        "importe_total": 20.0,
    }


def test_quality_report_without_valid_rows(sales_mini):
    report = quality_report(sales_mini, pd.DataFrame(), sales_mini)
    assert report["filas_validas"] == 0
    assert report["importe_total"] == 0.0

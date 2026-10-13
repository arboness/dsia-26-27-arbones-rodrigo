from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
COURSE_CSV = PROJECT_ROOT / "Datos" / "ventas.csv"


@pytest.fixture
def course_csv():
    """Ruta al ventas.csv real del curso (solo para tests de integración)."""
    return COURSE_CSV


@pytest.fixture
def sales_mini():
    """3 ventas: 1 válida, 1 con unidades nulas y 1 con precio negativo."""
    return pd.DataFrame({
        "fecha": ["2026-01-01", "2026-01-02", "2026-01-03"],
        "region": ["Norte", "Sur", "Norte"],
        "producto": ["A", "B", "A"],
        "unidades": [2, None, 5],
        "precio_unitario": [10.0, 20.0, -1.0],
        "cliente_id": ["C1", "C2", "C1"],
    })


@pytest.fixture
def valid_sales():
    """Ventas ya validadas, con importes conocidos para comprobar métricas."""
    return pd.DataFrame({
        "fecha": ["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-12", "2026-01-13"],
        "region": ["Norte", "Sur", "Norte", "Este", "Sur"],
        "producto": ["A", "B", "A", "C", "B"],
        "unidades": [2, 1, 3, 4, 1],
        "precio_unitario": [10.0, 50.0, 10.0, 5.0, 1.0],
        "cliente_id": ["C1", "C2", "C1", "C3", "C2"],
        "importe": [20.0, 50.0, 30.0, 20.0, 1.0],
    })


@pytest.fixture
def sales_csv(tmp_path, sales_mini):
    """``sales_mini`` guardado como CSV en una carpeta temporal."""
    path = tmp_path / "ventas.csv"
    sales_mini.to_csv(path, index=False)
    return path

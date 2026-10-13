"""Métricas de negocio sobre ventas ya validadas (con columna ``importe``)."""
import pandas as pd
from ventas_app.constants import AMOUNT_COLUMN, TOP_PRODUCTS_N


def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Importe total por región, ordenado de mayor a menor.

    Returns:
        DataFrame con columnas ``region`` e ``importe``.
    """
    return (
        df.groupby("region", as_index=False)[AMOUNT_COLUMN]
        .sum()
        .sort_values(AMOUNT_COLUMN, ascending=False, ignore_index=True)
    )


def top_products(df: pd.DataFrame, n: int = TOP_PRODUCTS_N) -> pd.DataFrame:
    """Los ``n`` productos con mayor importe total.

    Returns:
        DataFrame con columnas ``producto`` e ``importe``.
    """
    return (
        df.groupby("producto")[AMOUNT_COLUMN]
        .sum()
        .nlargest(n)
        .reset_index()
    )


def weekly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Importe total por semana (semanas cerradas en domingo).

    Las fechas no parseables se descartan.

    Returns:
        DataFrame con columnas ``fecha`` e ``importe_semanal``.
    """
    data = df.copy()
    data["fecha"] = pd.to_datetime(data["fecha"], format="ISO8601", errors="coerce")
    return (
        data.dropna(subset=["fecha"])
        .set_index("fecha")[AMOUNT_COLUMN]
        .resample("W")
        .sum()
        .reset_index()
        .rename(columns={AMOUNT_COLUMN: "importe_semanal"})
    )


def recurring_clients(df: pd.DataFrame) -> pd.DataFrame:
    """Clientes con más de una compra.

    Returns:
        DataFrame con columnas ``cliente_id`` y ``n_compras``, de más a menos compras.
    """
    counts = (
        df.groupby("cliente_id", as_index=False)
        .agg(n_compras=("cliente_id", "size"))
        .sort_values(["n_compras", "cliente_id"], ascending=[False, True], ignore_index=True)
    )
    return counts[counts["n_compras"] > 1].reset_index(drop=True)


def quality_report(df: pd.DataFrame, valid: pd.DataFrame, invalid: pd.DataFrame) -> dict:
    """Resumen de calidad del dataset.

    Returns:
        dict con ``filas_totales``, ``filas_validas``, ``filas_invalidas`` e ``importe_total``.
    """
    total_amount = float(valid[AMOUNT_COLUMN].sum()) if AMOUNT_COLUMN in valid else 0.0
    return {
        "filas_totales": int(len(df)),
        "filas_validas": int(len(valid)),
        "filas_invalidas": int(len(invalid)),
        "importe_total": round(total_amount, 2),
    }

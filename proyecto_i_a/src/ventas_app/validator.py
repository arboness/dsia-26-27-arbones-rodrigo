"""Validación de filas de ventas."""
import logging
import pandas as pd
from ventas_app.constants import AMOUNT_COLUMN, PRICE_COLUMN, UNITS_COLUMN
from ventas_app.exceptions import ValidationError

logger = logging.getLogger(__name__)


class SalesValidator:
    """Separa un DataFrame de ventas en filas válidas e inválidas.

    Regla: cada columna de ``positive_columns`` debe ser numérica y > 0.
    Los nulos y los textos no numéricos cuentan como inválidos.
    A las filas válidas se les añade ``importe = unidades * precio_unitario``.
    """

    def __init__(self, positive_columns: tuple[str, ...] = (UNITS_COLUMN, PRICE_COLUMN)):
        self.positive_columns = positive_columns

    def check_columns(self, df: pd.DataFrame) -> None:
        """Lanza ``ValidationError`` si falta alguna columna obligatoria."""
        missing = [c for c in self.positive_columns if c not in df.columns]
        if missing:
            raise ValidationError(f"Missing required columns: {missing}.")

    def valid_mask(self, df: pd.DataFrame) -> pd.Series:
        """Devuelve una máscara booleana: True si la fila cumple todas las reglas."""
        mask = pd.Series(True, index=df.index)
        for column in self.positive_columns:
            values = pd.to_numeric(df[column], errors="coerce")
            column_ok = values.gt(0) 
            n_bad = int((~column_ok).sum())
            if n_bad:
                logger.warning('%d rows with "%s" null, non-numeric or <= 0.', n_bad, column)
            mask &= column_ok
        return mask

    def validate(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Valida ``df`` y devuelve ``(valid, invalid)`` con índices reiniciados."""
        self.check_columns(df)
        mask = self.valid_mask(df)

        valid = df[mask].copy()
        units = pd.to_numeric(valid[UNITS_COLUMN])
        prices = pd.to_numeric(valid[PRICE_COLUMN])
        valid[AMOUNT_COLUMN] = units * prices

        invalid = df[~mask].copy()
        return valid.reset_index(drop=True), invalid.reset_index(drop=True)


def sales_validator(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Atajo funcional de ``SalesValidator().validate(df)``.

    Returns:
        (valid, invalid)

    Raises:
        ValidationError: si faltan las columnas ``unidades`` o ``precio_unitario``.
    """
    return SalesValidator().validate(df)

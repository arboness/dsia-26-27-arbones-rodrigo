"""Excepciones de dominio del pipeline de ventas.

Todas heredan de ``SalesPipelineError`` para que el CLI pueda capturarlas juntas,
y se registran en el log al crearse.
"""

import logging

logger = logging.getLogger(__name__)


class SalesPipelineError(Exception):
    """Error base del dominio. Se registra en el log al instanciarse."""

    default_message = "An error occurred in the sales pipeline."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)
        logger.error("%s: %s", type(self).__name__, self.message, stacklevel=2)


class DataLoadError(SalesPipelineError):
    """El fichero de entrada no se puede cargar (ruta vacía, inexistente o extensión no válida)."""

    default_message = "The file could not be loaded."


class ValidationError(SalesPipelineError):
    """El DataFrame no tiene la estructura mínima para validarse (p. ej. faltan columnas)."""

    default_message = "The dataframe is not valid."

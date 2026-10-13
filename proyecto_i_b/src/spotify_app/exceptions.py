"""Excepciones de dominio del pipeline de Spotify.

Misma idea que en ``ventas_app`` (una base + errores concretos), pero propias de
este paquete para no acoplar las dos partes.
"""

import logging

logger = logging.getLogger(__name__)


class SpotifyPipelineError(Exception):
    """Error base del dominio. Se registra en el log al instanciarse."""

    default_message = "An error occurred in the Spotify pipeline."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)
        logger.error("%s: %s", type(self).__name__, self.message, stacklevel=2)


class DataLoadError(SpotifyPipelineError):
    """El fichero no se puede cargar: ruta vacía o inexistente, extensión o JSON no válidos."""

    default_message = "The file could not be loaded."


class ValidationError(SpotifyPipelineError):
    """El DataFrame no tiene las columnas mínimas para validarse."""

    default_message = "The dataframe is not valid."

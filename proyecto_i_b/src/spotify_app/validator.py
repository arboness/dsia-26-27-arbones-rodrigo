"""Validación de canciones guardadas.

Cada regla devuelve una máscara booleana con True en las filas que la INCUMPLEN.
Una fila es válida si no incumple ninguna. Las inválidas salen con una columna
``motivo`` que lista las reglas incumplidas (p. ej. ``"duplicate_id; local_file"``).
"""

import logging
from collections.abc import Callable

import pandas as pd

from spotify_app.constants import (
    MAX_DURATION_MS,
    MIN_DURATION_MS,
    MIN_RELEASE_YEAR,
)
from spotify_app.exceptions import ValidationError

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = (
    "added_at",
    "track_id",
    "track_name",
    "artists",
    "release_date",
    "duration_ms",
    "is_local",
)

Rule = Callable[[pd.DataFrame], pd.Series]


def _blank(series: pd.Series) -> pd.Series:
    """True si el valor es nulo o una cadena vacía."""
    return series.isna() | series.astype(str).str.strip().eq("")


def _added_at(df: pd.DataFrame) -> pd.Series:
    return pd.to_datetime(df["added_at"], format="ISO8601", utc=True, errors="coerce")


def _release_year(df: pd.DataFrame) -> pd.Series:
    return pd.to_numeric(df["release_date"].astype(str).str[:4], errors="coerce")


def _is_true(series: pd.Series) -> pd.Series:
    return series.astype(str).str.strip().str.lower().isin({"true", "1"})


class SavedTracksValidator:
    """Aplica las reglas de calidad del dominio "biblioteca de Spotify"."""

    def __init__(self) -> None:
        self.rules: dict[str, Rule] = {
            "missing_id": lambda df: _blank(df["track_id"]),
            "duplicate_id": lambda df: df["track_id"].notna() & df["track_id"].duplicated(keep="first"),
            "missing_name": lambda df: _blank(df["track_name"]),
            "missing_artist": lambda df: _blank(df["artists"]),
            "local_file": lambda df: _is_true(df["is_local"]),
            "duration_out_of_range": self._bad_duration,
            "bad_added_at": lambda df: _added_at(df).isna(),
            "bad_release_date": self._bad_release_date,
        }

    @staticmethod
    def _bad_duration(df: pd.DataFrame) -> pd.Series:
        duration = pd.to_numeric(df["duration_ms"], errors="coerce")
        return ~duration.between(MIN_DURATION_MS, MAX_DURATION_MS)  

    @staticmethod
    def _bad_release_date(df: pd.DataFrame) -> pd.Series:
        year = _release_year(df)
        added_year = _added_at(df).dt.year
        
        too_late = added_year.notna() & (year > added_year + 1)
        return year.isna() | (year < MIN_RELEASE_YEAR) | too_late

    def check_columns(self, df: pd.DataFrame) -> None:
        """Lanza ``ValidationError`` si falta alguna columna obligatoria."""
        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValidationError(f"Missing required columns: {missing}.")

    def violations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Tabla booleana fila x regla (True = la fila incumple la regla)."""
        return pd.DataFrame({name: rule(df).fillna(True) for name, rule in self.rules.items()}, index=df.index)

    def validate(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Devuelve ``(valid, invalid)``.

        ``valid`` incluye columnas derivadas ``release_year`` y ``duration_min``.
        ``invalid`` incluye la columna ``motivo``.
        """
        self.check_columns(df)
        broken = self.violations(df)
        is_invalid = broken.any(axis=1)

        for rule, n in broken.sum().items():
            if n:
                logger.warning("%d rows break rule '%s'.", n, rule)

        valid = df[~is_invalid].copy()
        valid["release_year"] = _release_year(valid).astype("Int64")
        valid["duration_min"] = (pd.to_numeric(valid["duration_ms"]) / 60_000).round(2)

        invalid = df[is_invalid].copy()
        rule_names = broken.columns
        invalid["motivo"] = ["; ".join(rule_names[flags]) for flags in broken[is_invalid].to_numpy()]

        return valid.reset_index(drop=True), invalid.reset_index(drop=True)


def saved_tracks_validator(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Atajo funcional de ``SavedTracksValidator().validate(df)``."""
    return SavedTracksValidator().validate(df)

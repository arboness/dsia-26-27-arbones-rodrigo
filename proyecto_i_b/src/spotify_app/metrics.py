"""Métricas sobre canciones guardadas ya validadas."""

import pandas as pd

from spotify_app.constants import ARTIST_SEP, TOP_ARTISTS_N


def top_artists(df: pd.DataFrame, n: int = TOP_ARTISTS_N) -> pd.DataFrame:
    """Artistas con más canciones guardadas (cuenta también las colaboraciones).

    Returns:
        DataFrame con ``artist`` y ``n_tracks``; empates ordenados alfabéticamente.
    """
    artists = df["artists"].str.split(ARTIST_SEP).explode().str.strip()
    counts = artists.value_counts().rename_axis("artist").reset_index(name="n_tracks")
    return counts.sort_values(["n_tracks", "artist"], ascending=[False, True], ignore_index=True).head(n)


def saves_per_year(df: pd.DataFrame) -> pd.DataFrame:
    """Número de canciones guardadas cada año (según ``added_at``).

    Returns:
        DataFrame con ``year`` y ``n_saved``, en orden cronológico.
    """
    years = pd.to_datetime(df["added_at"], format="ISO8601", utc=True).dt.year
    return years.value_counts().sort_index().rename_axis("year").reset_index(name="n_saved")


def tracks_by_decade(df: pd.DataFrame) -> pd.DataFrame:
    """Canciones por década de lanzamiento y duración media.

    Returns:
        DataFrame con ``decade``, ``n_tracks`` y ``avg_duration_min``.
    """
    data = df.assign(decade=(df["release_year"] // 10 * 10).astype(int))
    return (
        data.groupby("decade", as_index=False)
        .agg(n_tracks=("track_id", "size"), avg_duration_min=("duration_min", "mean"))
        .round({"avg_duration_min": 2})
    )


def library_summary(df: pd.DataFrame) -> dict:
    """Resumen global de la biblioteca válida."""
    if df.empty:
        return {"n_tracks": 0, "n_artists": 0, "avg_duration_min": 0.0, "explicit_pct": 0.0}
    explicit = df["explicit"].astype(str).str.lower().eq("true")
    artists = df["artists"].str.split(ARTIST_SEP).explode().str.strip()
    return {
        "n_tracks": int(len(df)),
        "n_artists": int(artists.nunique()),
        "avg_duration_min": round(float(df["duration_min"].mean()), 2),
        "explicit_pct": round(float(explicit.mean() * 100), 1),
    }


def quality_report(df: pd.DataFrame, valid: pd.DataFrame, invalid: pd.DataFrame) -> dict:
    """Informe de calidad: recuento de filas y motivos de invalidez."""
    reasons: dict[str, int] = {}
    if "motivo" in invalid:
        exploded = invalid["motivo"].str.split("; ").explode()
        reasons = {k: int(v) for k, v in exploded.value_counts().sort_index().items()}
    return {
        "filas_totales": int(len(df)),
        "filas_validas": int(len(valid)),
        "filas_invalidas": int(len(invalid)),
        "motivos": reasons,
        "resumen": library_summary(valid),
    }

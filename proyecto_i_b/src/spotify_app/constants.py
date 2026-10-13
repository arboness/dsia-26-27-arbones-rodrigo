"""Constantes del dominio: canciones guardadas en una biblioteca de Spotify."""


COLUMNS = [
    "added_at",
    "track_id",
    "track_name",
    "artists",
    "main_artist",
    "album_name",
    "album_type",
    "release_date",
    "release_date_precision",
    "duration_ms",
    "explicit",
    "is_local",
]

ARTIST_SEP = "; "


MIN_DURATION_MS = 30_000  
MAX_DURATION_MS = 30 * 60_000 
MIN_RELEASE_YEAR = 1900

VALID_EXTENSIONS = {".csv", ".json"}

QUALITY_FILE = "quality.json"
INVALID_FILE = "invalid_tracks.csv"
TOP_ARTISTS_FILE = "top_artists.csv"
SAVES_PER_YEAR_FILE = "saves_per_year.csv"
DECADES_FILE = "tracks_by_decade.csv"

TOP_ARTISTS_N = 10

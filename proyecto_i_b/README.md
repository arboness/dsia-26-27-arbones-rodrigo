# Proyecto I — Parte B: pipeline de mi biblioteca de Spotify

[![CI](https://github.com/arboness/dsia-26-27-arbones-rodrigo/actions/workflows/ci.yml/badge.svg)](https://github.com/arboness/dsia-26-27-arbones-rodrigo/actions/workflows/ci.yml)

Mismo tipo de solución que la Parte A (**carga → validación → métricas → CLI → tests**), aplicado a la
**canciones guardadas ("Me gusta") de mi cuenta de Spotify**, descargadas con la Web API pública.
## Dataset

| | |
|---|---|
| **Origen** | Spotify Web API, endpoint [`GET /me/tracks`](https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks) (canciones guardadas del usuario autenticado) |
| **Condiciones de uso** | [Spotify Developer Terms](https://developer.spotify.com/terms) y [Developer Policy](https://developer.spotify.com/policy). Uso académico, no comercial. Los metadatos del catálogo pertenecen a Spotify y a sus licenciantes. |
| **Muestra en el repo** | `data/saved_tracks.csv`: 2045 filas |
| **Script de descarga** | `scripts/download_spotify.py` - `scripts/build_sample.py` |

**Por qué este dataset:** son datos reales y de mi interés con una estructura JSON anidada que obliga a un paso de aplanado que la Parte A no tenía.

**Privacidad:** la descarga cruda (`spotify_data/`, incluye perfil y email) y las credenciales (`.env`)
**no se suben** (están en `.gitignore`). La muestra solo contiene metadatos públicos del catálogo
(canción, artistas, álbum, fechas, duración) y la fecha en que guardé cada canción.

### Columnas de `data/saved_tracks.csv`

`added_at`, `track_id`, `track_name`, `artists` (separados por `; `), `main_artist`, `album_name`,
`album_type`, `release_date`, `release_date_precision`, `duration_ms`, `explicit`, `is_local`.

## Reglas de validación

Una canción es **inválida** si incumple alguna regla. Las inválidas se exportan con la columna `motivo`.

| Regla | Regla de invalidación|
|---|---|
| `missing_id` | `track_id` nulo o vacío (ej. ficheros locales) |
| `duplicate_id` | el `track_id` ya apareció antes (se queda la primera) |
| `missing_name` | `track_name` nulo o vacío |
| `missing_artist` | sin artistas |
| `local_file` | `is_local` es `True` (no está en el catálogo) |
| `duration_out_of_range` | duración fuera de **[30 s, 30 min]**: podcasts |
| `bad_added_at` | `added_at` no es una fecha ISO 8601 |
| `bad_release_date` | año ilegible, anterior a 1900 o posterior al año en que se guardó **+1** (pre-releases) |

A las válidas se les añaden `release_year` y `duration_min`.
Si faltan columnas obligatorias se lanza `ValidationError`.

**Checkpoint con la muestra:** 2045 filas → **2044 válidas y 1 inválida** (`duration_out_of_range`, un intro de 23 s).

## Métricas

| Fichero | Contenido |
|---|---|
| `top_artists.csv` | Top 10 artistas por nº de canciones guardadas (cuenta colaboraciones) |
| `saves_per_year.csv` | Canciones guardadas por año |
| `tracks_by_decade.csv` | Canciones y duración media por década de lanzamiento |
| `quality.json` | Filas totales/válidas/inválidas, recuento por motivo y resumen (nº artistas, duración media, % explícitas) |
| `invalid_tracks.csv` | Filas inválidas con `motivo` |

## Estructura

```
proyecto_i_b/
  src/spotify_app/
    loader.py       # load_saved_tracks(): JSON de la API (aplana) o CSV; DataLoadError
    validator.py    # SavedTracksValidator: reglas -> (válidas, inválidas con motivo)
    metrics.py      # top_artists, saves_per_year, tracks_by_decade, library_summary, quality_report
    export.py
    cli.py          # python -m spotify_app.cli
    exceptions.py   # SpotifyPipelineError -> DataLoadError, ValidationError
    constants.py
  scripts/
    download_spotify.py  # descarga con spotipy (requiere .env, no se usa en tests ni CI)
    build_sample.py      # spotify_data/canciones_guardadas.json -> data/saved_tracks.csv
  tests/spotify/         # test_loader, test_validator, test_metrics, test_cli
  data/saved_tracks.csv
  requirements.txt
  pyproject.toml
```

## Instalación

```bash
cd proyecto_i_b
uv sync                         
```

## Ejecutar el pipeline

```bash
python -m spotify_app.cli --input data/saved_tracks.csv --output salida/saved_tracks_clean.csv
```

También acepta directamente el JSON de la API: `--input spotify_data/canciones_guardadas.json`.
Con uv: `uv run python -m spotify_app.cli ...`. Con pip sin instalar el paquete, usa `PYTHONPATH=src`.

Códigos de salida: `0` OK · `1` error de carga/validación · `2` argumentos incorrectos.

### Volver a descargar los datos (opcional)

1. Crea una app en el [dashboard de Spotify](https://developer.spotify.com/dashboard) con la Redirect URI `http://127.0.0.1:8888/callback`.
2. Crea `proyecto_i_b/.env` con `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET` y `SPOTIPY_REDIRECT_URI`.
3. Ejecuta:

```bash
uv sync --extra download       
python scripts/download_spotify.py
python scripts/build_sample.py
```

## Tests

```bash
pytest -q
pytest -q -m "not integration"
pytest --cov=spotify_app --cov-report=term-missing --cov-fail-under=60
```

Los unitarios usan fixtures en memoria (JSON con la forma de la API) y `tmp_path`, sin red.
Los de integración (`@pytest.mark.integration`) leen `data/saved_tracks.csv`.

## CI

El mismo workflow del repo (`.github/workflows/ci.yml`) ejecuta las Partes A y B, cada una con `--cov-fail-under=60`.

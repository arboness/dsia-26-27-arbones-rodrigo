"""
Descarga tus datos de Spotify a JSON usando la Web API.

Requisitos (desde proyecto_i_b/):
    uv sync --extra download      # o: pip install spotipy python-dotenv

Antes de ejecutar:
    1. En el dashboard de tu app añade la Redirect URI: http://127.0.0.1:8888/callback
    2. Crea un fichero proyecto_i_b/.env (NUNCA se sube al repo) con:
         SPOTIPY_CLIENT_ID=...
         SPOTIPY_CLIENT_SECRET=...
         SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
    3. python scripts/download_spotify.py
    4. python scripts/build_sample.py   # genera data/saved_tracks.csv

La primera vez se abre el navegador para que autorices la app.
Los datos se guardan en la carpeta ./spotify_data/
"""

import json
from pathlib import Path

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()  # carga SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET y SPOTIPY_REDIRECT_URI desde .env

SCOPES = " ".join([
    "user-read-private",
    "user-read-email",
    "user-top-read",
    "user-library-read",
    "user-read-recently-played",
    "user-follow-read",
    "playlist-read-private",
    "playlist-read-collaborative",
])

OUT = Path(__file__).resolve().parents[1] / "spotify_data"
OUT.mkdir(exist_ok=True)

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPES, open_browser=True))


def save(name, data):
    path = OUT / f"{name}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    n = len(data) if isinstance(data, list) else 1
    print(f"  ✓ {name}: {n} elementos -> {path}")


def get_all(endpoint, params=None, key=None):
    """Recorre todas las páginas de un endpoint paginado."""
    page = sp._get(endpoint, **(params or {}))
    if key:
        page = page[key]
    items = list(page.get("items", []))
    while page.get("next"):
        page = sp.next(page)
        if key:
            page = page[key]
        items.extend(page.get("items", []))
    return items


def safe(name, fn):
    """Ejecuta un bloque y sigue aunque un endpoint falle (p. ej. 403 en Development Mode)."""
    try:
        save(name, fn())
    except spotipy.SpotifyException as e:
        print(f"  ✗ {name}: HTTP {e.http_status} - {e.msg}")


print("Descargando datos de Spotify...\n")

# Perfil
safe("perfil", lambda: sp._get("me"))

# Top artistas y canciones (4 semanas, 6 meses, ~1 año)
for rango in ["short_term", "medium_term", "long_term"]:
    safe(f"top_artistas_{rango}", lambda r=rango: get_all("me/top/artists", {"time_range": r, "limit": 50}))
    safe(f"top_canciones_{rango}", lambda r=rango: get_all("me/top/tracks", {"time_range": r, "limit": 50}))

# Biblioteca
safe("canciones_guardadas", lambda: get_all("me/tracks", {"limit": 50}))
safe("albumes_guardados", lambda: get_all("me/albums", {"limit": 50}))

# Últimas reproducciones (la API solo da las últimas 50)
safe("reproducidas_recientemente", lambda: sp._get("me/player/recently-played", limit=50)["items"])

# Artistas seguidos (paginación por cursor)
def artistas_seguidos():
    res = sp._get("me/following", type="artist", limit=50)["artists"]
    items = list(res["items"])
    while res.get("next"):
        res = sp.next(res)["artists"]
        items.extend(res["items"])
    return items

safe("artistas_seguidos", artistas_seguidos)

# Playlists y su contenido
def playlists_con_contenido():
    playlists = get_all("me/playlists", {"limit": 50})
    for pl in playlists:
        try:
            # Endpoint actual (/items); desde feb. 2026 sustituye a /tracks
            pl["contenido"] = get_all(f"playlists/{pl['id']}/items", {"limit": 50})
        except spotipy.SpotifyException as e:
            pl["contenido"] = None
            print(f"    · No se pudo leer '{pl.get('name')}': HTTP {e.http_status}")
    return playlists

safe("playlists", playlists_con_contenido)

print("\nListo.")
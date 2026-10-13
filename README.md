# dsia-26-27-arbones-rodrigo

[![CI](https://github.com/arboness/dsia-26-27-arbones-rodrigo/actions/workflows/ci.yml/badge.svg)](https://github.com/arboness/dsia-26-27-arbones-rodrigo/actions/workflows/ci.yml)


## Proyecto I

| Parte | Carpeta | Paquete | Datos |
|---|---|---|---|
| A — Pipeline de ventas | [`proyecto_i_a/`](proyecto_i_a/README.md) | `ventas_app` | `ventas.csv` del curso |
| B — Biblioteca de Spotify | [`proyecto_i_b/`](proyecto_i_b/README.md) | `spotify_app` | Canciones guardadas vía Spotify Web API |

Cada carpeta tiene su README con cómo ejecutar el CLI y los tests.
Un único workflow (`.github/workflows/ci.yml`) ejecuta los tests de ambas partes con `--cov-fail-under=60`.

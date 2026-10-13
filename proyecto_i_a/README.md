# Proyecto I — Parte A: pipeline de ventas

[![CI](https://github.com/arboness/dsia-26-27-arbones-rodrigo/actions/workflows/ci.yml/badge.svg)](https://github.com/arboness/dsia-26-27-arbones-rodrigo/actions/workflows/ci.yml)

Pipeline de calidad de datos sobre el `ventas.csv` del curso:
**carga → validación → métricas → exportación**, con CLI, tests (pytest) y CI (GitHub Actions).

## Estructura

```
proyecto_i_a/
  src/ventas_app/
    loader.py       # load_file(): CSV/TXT/JSON -> DataFrame; DataLoadError si la ruta no vale
    validator.py    # SalesValidator / sales_validator(): (válidas, inválidas) + columna importe
    metrics.py      # sales_by_region, top_products, weekly_sales, recurring_clients, quality_report
    export.py       # export_to_csv, export_json
    cli.py          # python -m ventas_app.cli
    exceptions.py   # SalesPipelineError -> DataLoadError, ValidationError
    constants.py
  tests/ventas/
    conftest.py     # fixtures en memoria (sales_mini, valid_sales) y tmp_path
    test_loader.py
    test_validator.py
    test_metrics.py
    test_cli.py
  Datos/ventas.csv  # dataset del curso (150 filas)
  requirements.txt
  pyproject.toml
```

## Reglas de validación

Una venta es **válida** si `unidades` y `precio_unitario` son numéricos y **> 0**.
Nulos, textos no numéricos, ceros y negativos son **inválidos**.
A las válidas se les añade `importe = unidades * precio_unitario`.
Si faltan esas columnas se lanza `ValidationError`.

Checkpoint con el CSV del curso: **140 válidas y 10 inválidas**.

## Instalación

Con [uv](https://docs.astral.sh/uv/):

```bash
cd proyecto_i_a
uv sync
```

O con pip (Python ≥ 3.12):

```bash
cd proyecto_i_a
pip install -r requirements.txt
```

## Ejecutar el pipeline

```bash
python -m ventas_app.cli --input Datos/ventas.csv --output salida/ventas_limpias.csv
```

Con uv: `uv run python -m ventas_app.cli ...` o `uv run ventas-app ...`.
Si usas pip sin instalar el paquete, ejecuta con `PYTHONPATH=src` (en PowerShell: `$env:PYTHONPATH="src"`).

Salida (en la carpeta de `--output`):

| Fichero | Contenido |
|---|---|
| `ventas_limpias.csv` | Filas válidas con `importe` |
| `quality.json` | `filas_totales`, `filas_validas`, `filas_invalidas`, `importe_total` |
| `sales_by_region.csv` | Importe total por región (desc) |
| `top_products.csv` | Top 3 productos por importe |
| `weekly_sales.csv` | Importe por semana |
| `recurring_clients.csv` | Clientes con más de una compra |

Códigos de salida: `0` OK · `1` error de carga/validación · `2` argumentos incorrectos.

## Tests

```bash
pytest -q                       
pytest -q -m "not integration"  
pytest --cov=ventas_app --cov-report=term-missing --cov-fail-under=60
```

Con uv, antepón `uv run` (p. ej. `uv run pytest -q`).

- **Unitarios**: fixtures en memoria y `tmp_path`, sin red ni rutas absolutas.
- **Integración** (`@pytest.mark.integration`): leen `Datos/ventas.csv` y comprueban 140/10.
- Conceptos: AAA + `assert`, `pytest.raises`, `@pytest.mark.parametrize`, fixtures.

## CI

`.github/workflows/ci.yml` (en la raíz del repo) se ejecuta en cada `push` a `main` y en cada `pull_request`:
checkout → Python 3.12 → `pip install -r requirements.txt` → `pytest --cov=ventas_app --cov-fail-under=60`.

Runs: [pestaña Actions](https://github.com/arboness/dsia-26-27-arbones-rodrigo/actions/workflows/ci.yml).

"""Constantes compartidas por el pipeline de ventas."""

# Columnas que deben existir y ser numéricas > 0 para que una venta sea válida.
UNITS_COLUMN = "unidades"
PRICE_COLUMN = "precio_unitario"
AMOUNT_COLUMN = "importe"

# Extensiones de fichero que acepta el loader.
VALID_EXTENSIONS = {".csv", ".txt", ".json"}

# Nombres de los ficheros que genera el CLI junto al CSV limpio.
QUALITY_FILE = "quality.json"
REGION_FILE = "sales_by_region.csv"
WEEKLY_FILE = "weekly_sales.csv"
TOP_PRODUCTS_FILE = "top_products.csv"
RECURRING_CLIENTS_FILE = "recurring_clients.csv"

TOP_PRODUCTS_N = 3

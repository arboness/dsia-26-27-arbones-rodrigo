# Decisiones de diseño — Parte A

## Single Responsibility
Cada módulo hace una sola cosa:

- `loader.load_file()` solo carga el fichero; no limpia ni transforma (evita el anti-patrón de cargar y preprocesar a la vez).
- `validator.SalesValidator` solo decide qué filas son válidas y calcula `importe`.
- `metrics` solo agrega; recibe datos ya validados.
- `export` solo escribe a disco.
- `cli` orquesta los pasos y traduce errores a códigos de salida.

## Excepciones de dominio
`SalesPipelineError` es la base; `DataLoadError` y `ValidationError` heredan de ella.
El CLI captura la base y devuelve `1`, sin acoplarse a cada caso concreto.

## OOP
`SalesValidator` encapsula las reglas (`positive_columns`) y separa
`check_columns` -> `valid_mask` -> `validate`. `sales_validator()` se mantiene como atajo funcional.

## Dependency inversion / testabilidad
- Los tests no dependen de red ni de rutas absolutas: usan fixtures en memoria y `tmp_path`.
- El CLI recibe `argv` (`main(argv)`) y escribe donde diga `--output`, así que se puede probar sin tocar `Datos/`.

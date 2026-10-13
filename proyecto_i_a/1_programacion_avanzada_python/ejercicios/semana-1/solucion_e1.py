import pandas as pd
from pathlib import Path
import os
import json

from constants import DATA_DIRECTORY, NAME_CSV, NAME_CSV_CLEAN

JSON_FILE_NAME = "calidad_datos.json"

def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    df_clean = pd.DataFrame(columns=frame.columns.tolist()) 
    df_errors = pd.DataFrame(columns=frame.columns.tolist()) 

    
    for i, fila in frame.iterrows():
        isClean = False
        unidades = pd.to_numeric(fila['unidades'], errors='coerce')
        precio_unitario = pd.to_numeric(fila['precio_unitario'], errors='coerce')
        if not pd.isna(unidades) and unidades > 0:
            if not pd.isna(precio_unitario) and precio_unitario > 0:
                isClean = True
                
        if isClean:
            df_clean.loc[len(df_clean)] = fila
            df_clean.loc[len(df_clean)-1, 'importe'] = unidades * precio_unitario
        else:
            df_errors.loc[len(df_errors)] = fila
            
    return (df_clean, df_errors)

def cargar(ruta_csv: str) -> pd.DataFrame: 
    df = pd.read_csv(ruta_csv)
    return df

            
def exportar_json(ruta: str, diccionario):           
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(diccionario, f, indent=2, ensure_ascii=False)    

def agregar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

    semanal = (
        df.dropna(subset=["fecha"])
          .set_index("fecha")["importe"]
          .resample("W")
          .sum()
          .reset_index()
          .rename(columns={"importe": "importe_semanal"})
    )
    return semanal


df = cargar(Path(os.getcwd()) / DATA_DIRECTORY/  NAME_CSV)

df.shape
df.dtypes

print(f"\nNulos {df.isna().sum()}")

df_clean, df_errors = validar_ventas(df)

print(f"\nFilas limpias: {len(df_clean)}")
print(f"\nFilas erróneas: {len(df_errors)}")

print(f"\nImporte por región: {df_clean['importe'].groupby(df_clean['region']).sum().sort_values(ascending=False)}")

print(f"\nTop 3 productos: {df_clean.groupby("producto")["importe"].sum().nlargest(3)}")

unidades = pd.to_numeric(df_clean["unidades"], errors="coerce")
clientes = df_clean.loc[unidades > 1, "cliente_id"].unique()
print(f"\nClientes con más de una compra: {clientes}")


df_clean.to_csv(Path(DATA_DIRECTORY) / NAME_CSV_CLEAN, index=False)

calidad = {
    "filas_totales": int(len(df)),
    "filas_validas": int(len(df_clean)),
    "filas_invalidas": int(len(df) - len(df_clean)),
    "importe_total": float(df_clean["importe"].sum()),
}

exportar_json(Path(DATA_DIRECTORY) / JSON_FILE_NAME, calidad )
    
            

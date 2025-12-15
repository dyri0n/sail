import sys
import time

import pandas as pd
import requests
from sqlalchemy import create_engine

# Configuración de conexión (puedes usar variables de entorno o sys.argv)
# DB_URI = "postgresql+psycopg2://user:pass@host:port/staging_db"
# Para el ejemplo asumo que pasas la string de conexión como argumento
if len(sys.argv) > 1:
    DB_URI = sys.argv[1]
else:
    print("Error: Falta Connection String")
    sys.exit(1)

engine = create_engine(DB_URI)


def extraer_feriados(anio_inicio, anio_fin):
    todos_los_feriados = []

    print(f"--- Iniciando extracción de feriados Chile ({anio_inicio}-{anio_fin}) ---")

    for anio in range(anio_inicio, anio_fin + 1):
        url = f"https://api.boostr.cl/feriados/{anio}.json"
        try:
            print(f"Descargando {anio}...")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json().get("data", [])

            for item in data:
                # Aplanamos la data para el DataFrame
                todos_los_feriados.append(
                    {
                        "fecha": item["date"],  # Formato YYYY-MM-DD
                        "nombre": item["title"],
                        "tipo": item["type"],
                        "irrenunciable": item.get("inalienable", False),  # Boolean
                    }
                )

            # Pausa pequeña para ser gentiles con la API pública
            time.sleep(0.5)

        except Exception as e:
            print(f"Error extrayendo {anio}: {e}")

    # Convertir a DataFrame
    df = pd.DataFrame(todos_los_feriados)

    # Validaciones básicas
    if not df.empty:
        df["fecha"] = pd.to_datetime(df["fecha"])
        print(f"Total extraído: {len(df)} feriados.")

        # Guardar en Staging (Reemplazamos la tabla completa cada vez)
        df.to_sql(
            "stg_feriados_chile",
            con=engine,
            if_exists="replace",
            index=False,
            schema="staging",
        )
        print("Carga en Staging exitosa.")
    else:
        print("No se encontraron datos.")


if __name__ == "__main__":
    # Rango: 2010 a 2028 (ajusta según necesidad)
    extraer_feriados(2010, 2028)

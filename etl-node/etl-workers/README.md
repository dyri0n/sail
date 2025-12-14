# 🔨 ETL-WORKERS: El Músculo de Cómputo

Estos contenedores son workers de Python dedicados a tareas de cómputo intensivas, principalmente la **Ingesta de Datos (Paso 1)**.

## Archivos Clave

* **`Dockerfile`**: Construye la imagen del worker, instalando librerías como Pandas, OpenPyXL, y librerías de conexión a la base de datos (e.g., Psycopg2).
* **`/scripts`**: Contiene la lógica Python de ingesta.

## Directorio `/scripts`

* **`excel_to_staging.py`**: Script central que lee archivos `.xlsx` de `/input_data`, aplica una validación/limpieza mínima, y carga los datos masivamente a la capa Staging.
* **`common_db.py`**: Módulo de utilidad para manejar las conexiones y transacciones con la base de datos.

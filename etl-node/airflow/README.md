# 🌬️ Airflow: El Cerebro del ETL

Airflow es el orquestador principal del proyecto.

## Archivos Clave

* **`Dockerfile`**: Define la imagen de Airflow, instalando dependencias (e.g., psycopg2, librerías de conexión).
* **`docker-compose.yml`**: Configuración para levantar el Scheduler, Webserver y Worker de Airflow, incluyendo la conexión a la base de datos de metadatos de Airflow y montando el directorio de DAGs.

## Directorio `/dags`

Aquí residen todos los flujos de trabajo (DAGs) del DWH.

* **`dag_ingesta_excel.py`**: DAG que orquesta la **Lectura e Ingesta** (Paso 1). Llama a los scripts de Python en `/etl-workers` para mover data de `/input_data` a la capa Staging.
* **`dag_transformacion.py`**: DAG que orquesta la **Transformación y Modelado** (Paso 2). Ejecuta los scripts SQL almacenados en `/dags/sql` para poblar el DWH de Producción.

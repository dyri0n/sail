# 🧠 ETL-NODE: Orquestación y Cómputo

Este directorio contiene los componentes activos del pipeline ETL: Apache Airflow (orquestación) y los ETL Workers (cómputo/ingesta).

## Directorios Clave

* **`/airflow`**: El orquestador, donde se definen los flujos de trabajo (DAGs).
* **`/etl-workers`**: Los contenedores de cómputo que ejecutan las tareas pesadas de ingesta de datos (Paso 1).
* **`/input_data`**: La carpeta de *landing* donde se depositan los archivos fuente (Excel, CSV) que serán procesados.

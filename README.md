# 🏛️ Data Warehouse Central - Arquitectura Docker-Airflow

Este repositorio contiene la arquitectura completa para el pipeline de Extracción, Transformación y Carga (ETL) del Data Warehouse (DWH) de RRHH.

El diseño se basa en dos nodos principales, cada uno contenido en un servicio Docker Compose:

1.  **`/dwh-node`**: Contiene la base de datos (PostgreSQL, MySQL, etc.) que aloja las capas Staging y Producción del DWH.
2.  **`/etl-node`**: Contiene los servicios de orquestación (Airflow) y los workers de cómputo (Python) necesarios para ejecutar el pipeline.

## Flujo del Proceso ETL (De 2 Pasos)

1.  **Paso de Ingesta (Extract & Load - ETL Worker)**: Scripts de Python leen los archivos fuente (`.xlsx`, `.csv`) desde `/etl-node/input_data` y los cargan directamente a las tablas de la capa **Staging** en la base de datos.
2.  **Paso de Transformación (Transform - Airflow DAG/SQL)**: Scripts SQL complejos (orquestados por Airflow) se ejecutan en la base de datos **Staging** para limpiar, cruzar y cargar los datos transformados y modelados (Dimensiones y Hechos) en la capa **Production_DWH**.

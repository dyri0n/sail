# 📜 Scripts SQL de Transformación (Paso 2)

Este directorio contiene la lógica de transformación del DWH, ejecutada por Airflow.

Los scripts reciben datos de la capa `staging` y realizan:

1.  **Limpieza y Estandarización**
2.  **Lógica SCD (Dimensiones de Cambio Lento)**
3.  **Cruce de Datos y Agregación (Tablas de Hechos)**

* **`staging_to_dim_clientes.sql`**: Ejemplo de script que implementa la lógica SCD para la dimensión de Clientes.
* **`staging_to_fact_ventas.sql`**: Ejemplo de script que calcula las métricas y carga la tabla de hechos.

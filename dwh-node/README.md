# 💾 DWH-NODE: Base de Datos

Este directorio aloja el servicio de base de datos que actuará como nuestro Data Warehouse.

## Archivos Clave

* **`docker-compose.yml`**: Define el servicio de la base de datos (e.g., Postgres) y configura volúmenes y puertos.
* **`/init-scripts`**: Directorio para los scripts SQL que se ejecutan automáticamente al levantar el contenedor por primera vez.

## Directorio `/init-scripts`

Contiene el SQL necesario para configurar el ambiente del DWH:

* **`01_init_dbs.sql`**: Script que crea las dos bases de datos principales:
    * `staging`: Para datos crudos o mínimamente limpiados.
    * `production_dwh`: Para el modelo final (Dimensiones y Tablas de Hechos).

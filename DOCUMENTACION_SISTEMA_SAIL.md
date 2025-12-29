# 📄 Documentación Técnica Extendida: Proyecto SAIL

## 🚀 1. Arquitectura de Datos y Flujos de Información
**SAIL** emplea un enfoque de **Data-as-Infrastructure**, donde cada componente es agnóstico pero está fuertemente integrado mediante Docker.

### 📁 Pipeline de Ingesta (ELT vs ETL)
A diferencia de un ETL tradicional, SAIL aplica un enfoque híbrido:
1.  **Extract & Load (EL) / Staging**: Los Workers Python extraen archivos Excel/CSV y los cargan en `stg` "as-is" usando `Pandas` (con tipos de datos flexibles).
2.  **Transform (T) / Loading**: La lógica de negocio pesada reside en PostgreSQL mediante scripts SQL, aprovechando el motor de base de datos para join y agregaciones masivas.

---

## 🏗️ 2. Deep Dive: Motor de Base de Datos (PostgreSQL 17)
### A. Segregación de Roles y Seguridad (RBAC)
El sistema implementa una política de privilegios mínimos:
-   **`dwh_admin`**: Propietario del schema `dwh`. Tiene permisos de `SELECT` sobre `stg`. Es el usuario utilizado por Airflow para las transformaciones finales.
-   **`stg_admin`**: Propietario del schema `stg`. Único usuario con permisos de `TRUNCATE` y `INSERT` sobre tablas temporales.
-   **Superusuario (`postgres`)**: Reservado para tareas de mantenimiento e inicialización.

### B. Gestión de Integridad en Cargas Masivas
Para optimizar el rendimiento de los DAGs de "Poblado Completo", se implementa un patrón de **Desactivación de Triggers**:
```sql
ALTER TABLE dwh.fact_rotacion DISABLE TRIGGER ALL;
-- Proceso de carga masiva
ALTER TABLE dwh.fact_rotacion ENABLE TRIGGER ALL;
```
Esto permite realizar inserciones de millones de registros sin la sobrecarga de validación inmediata de Foreign Keys, la cual se valida al reactivar o mediante procesos de auditoría post-carga.

---

## 🔄 3. Lógica de Transformación Advanced: SCD Tipo 2
La dimensión `dim_empleado` es el corazón analítico y utiliza **Slowly Changing Dimensions (SCD) Tipo 2** para mantener la trazabilidad histórica.

### Mecanismo de Detección de Cambios (Hashing)
En lugar de comparar columna por columna, el sistema genera un hash MD5 de los atributos personales:
```sql
MD5(ROW(s.nombre, s.sexo, s.fecha_nacimiento, s.nacionalidad, s.estado_civil)::text)
```
Si el hash de Staging difiere del hash de la fila activa en DWH, el sistema:
1.  **Cierra** la versión actual (`scd_es_actual = FALSE`, `fecha_fin = Ayer`).
2.  **Inserta** una nueva fila con los datos actualizados y `scd_es_actual = TRUE`.

### Clasificación de Acciones (Logic Engine)
El script de transformación utiliza un CTE o tabla temporal para clasificar cada registro de origen en etiquetas: `NUEVO`, `REACTIVAR_SCD1`, `REINGRESO_SCD2`, `BAJA_SCD2`, `CAMBIO_SCD2`, facilitando el mantenimiento y debugging de la lógica.

---

## 🌬️ 4. Orquestación Avanzada con Airflow 3.x
### A. Patrón TaskFlow API
El sistema utiliza el decorador `@task` (TaskFlow API) en lugar de los operadores tradicionales para las tareas de Python, lo que permite el paso de objetos y metadatos (XComs) de forma nativa y tipada.

### B. Aislamiento de Ejecución (DockerOperator)
Las tareas que requieren dependencias específicas de Python o gran cómputo se ejecutan mediante contenedores efímeros. Esto garantiza que el core de Airflow no se vea afectado por conflictos de librerías o fugas de memoria durante el procesamiento de Excels pesados.

---

## 🌐 5. Infraestructura y Red (Networking)
### Comunicación Inter-Contenedor
Debido a que los servicios residen en diferentes `docker-compose.yaml`, el sistema utiliza el host bridge o redes compartidas:
-   **Host Aliasing**: Se utiliza `host.docker.internal` para que el nodo ETL pueda alcanzar al DWH independientemente de si la IP local cambia.
-   **Persistence**: El volumen `pg_data` utiliza un driver local mapeado para asegurar que los datos del DWH sobrevivan a reinicios de contenedores o actualizaciones de imagen.

---

## 📈 6. Patrones de Diseño ETL
1.  **Idempotencia**: Todos los scripts SQL están diseñados para ser ejecutados múltiples veces sin duplicar datos (uso de `UPSERT` o clasificación previa).
2.  **Truncate-and-Load**: La zona de `stg` se limpia en cada inicio de ciclo para garantizar que no existan datos zombies de ejecuciones fallidas.
3.  **Audit Columns**: Cada tabla de hechos y dimensiones cuenta con `fecha_carga` para trazabilidad de linaje de datos.

---

## 📝 7. Especificaciones Técnicas de Software
- **Python**: 3.11 (Optimizado para Pandas 2.x)
- **PostgreSQL**: 17.x (Aprovechando `MERGE` statement nativo)
- **Airflow**: 3.x (Utilizando el nuevo scheduler de alta disponibilidad)
- **OS Base**: Debian Bullseye (en imágenes Docker por estabilidad)

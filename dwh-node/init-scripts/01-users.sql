-- =============================================================================
-- 01-USERS.SQL - Configuración de usuarios y permisos
-- =============================================================================
-- Ejecutado automáticamente por Postgres al iniciar el contenedor.
-- Se ejecuta ANTES de crear schemas porque necesitamos los usuarios primero.
-- =============================================================================

-- Usuario para el Data Warehouse (tablas dimensionales y de hechos)
-- SUPERUSER necesario para poder ejecutar SET session_replication_role durante ETL
CREATE USER dwh_admin WITH PASSWORD 'sail-rrhh-p4' SUPERUSER;

-- Usuario para el Staging (tablas temporales de carga)
CREATE USER stg_admin WITH PASSWORD 'sail-stg-p4';

-- Permisos de conexión a la base de datos
GRANT CONNECT ON DATABASE rrhh_prod TO dwh_admin;
GRANT CONNECT ON DATABASE rrhh_prod TO stg_admin;

-- Permitir que dwh_admin lea del staging (para los ETL queries)
-- Esto se configura después de crear el schema staging

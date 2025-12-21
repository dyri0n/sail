# 💾 DWH-NODE: Base de Datos Unificada (DWH + Staging)

Nodo de base de datos PostgreSQL que contiene tanto el **Data Warehouse** como las tablas de **Staging** en una sola instancia.

## Arquitectura

```
┌─────────────────────────────────────┐
│         rrhh_prod (Database)        │
│                                     │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Schema: stg │  │ Schema: dwh │   │
│  │ (temporal)  │  │  (final)    │   │
│  │             │  │             │   │
│  │ stg_*       │  │ dim_*       │   │
│  │ tables      │  │ fact_*      │   │
│  └─────────────┘  └─────────────┘   │
└─────────────────────────────────────┘
```

## Estructura de Archivos

```
dwh-node/
├── docker-compose.yaml      # Orquestación del contenedor
├── Dockerfile               # Imagen producción (sin datos de prueba)
├── Dockerfile.testing       # Imagen testing (con datos de prueba)
└── init-scripts/
    ├── 01-users.sql         # Usuarios: dwh_admin, stg_admin
    ├── 02-schema-stg.sql    # Schema staging + tablas stg_*
    ├── 03-schema-dwh.sql    # Schema dwh + dims + facts
    └── 04-seed-test-data.sql # Datos de prueba (solo testing)
```

## Modos de Ejecución

### 🏭 Producción (sin datos de prueba)

```bash
docker compose up -d
```

### 🧪 Testing (con datos de prueba)

```bash
DOCKERFILE=Dockerfile.testing docker compose up -d --build
```

## Conexión

| Usuario   | Password      | Schema | Permisos                |
| --------- | ------------- | ------ | ----------------------- |
| dwh_admin | sail-rrhh-p4  | dwh    | ALL (dwh), SELECT (stg) |
| stg_admin | sail-stg-p4   | stg    | ALL (stg)               |
| postgres  | password_root | -      | Superuser               |

### Ejemplo conexión psql

```bash
# Como dwh_admin (puede leer staging y escribir dwh)
psql -h localhost -p 6000 -U dwh_admin -d rrhh_prod

# Verificar schemas
\dn

# Ver tablas de staging
\dt stg.*

# Ver tablas de dwh
\dt dwh.*
```

## Red Docker

El contenedor se conecta a la red `sail-network` que comparte con Airflow:

```bash
# La red se crea automáticamente al levantar este compose
docker network ls | grep sail
```

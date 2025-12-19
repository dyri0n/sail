# 🗄️ STG-NODE: Base de Datos Staging

Nodo de base de datos PostgreSQL para la capa de **Staging** del pipeline ETL de RRHH.

## Estructura

```
stg-node/
├── docker-compose.yaml      # Orquestación con perfiles prod/testing
├── Dockerfile               # Imagen producción (solo schema)
├── Dockerfile.testing       # Imagen testing (schema + datos prueba)
├── init-scripts/
│   ├── 01-init_schema.sql   # DDL de todas las tablas staging
│   └── 02-seed_test_data.sql # Datos de prueba (solo testing)
└── README.md
```

## Modos de Ejecución

### 🏭 Producción (sin datos)

```bash
docker compose --profile prod up -d
```

- Puerto: `6001` (configurable via `STG_PORT`)
- Base de datos: `rrhh_staging`
- Solo crea el schema vacío

### 🧪 Testing (con datos de prueba)

```bash
docker compose --profile testing up -d
```

- Puerto: `6002` (configurable via `STG_TEST_PORT`)
- Base de datos: `rrhh_staging_test`
- Incluye datos de prueba precargados

## Conexión

| Modo    | Host      | Puerto | Usuario   | Password    | Base de datos     |
| ------- | --------- | ------ | --------- | ----------- | ----------------- |
| Prod    | localhost | 6001   | stg_admin | sail-stg-p4 | rrhh_staging      |
| Testing | localhost | 6002   | stg_admin | sail-stg-p4 | rrhh_staging_test |

### Ejemplo conexión psql

```bash
# Producción
psql -h localhost -p 6001 -U stg_admin -d rrhh_staging

# Testing
psql -h localhost -p 6002 -U stg_admin -d rrhh_staging_test
```

### Ejemplo conexión Python

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=6002,  # Testing
    database="rrhh_staging_test",
    user="stg_admin",
    password="sail-stg-p4"
)
```

## Tablas Disponibles

| Tabla                                      | Descripción                              |
| ------------------------------------------ | ---------------------------------------- |
| `staging.stg_rotacion_empleados`           | Maestro de empleados y datos de rotación |
| `staging.stg_capacitaciones_resumen`       | Resumen mensual de capacitaciones        |
| `staging.stg_capacitaciones_participantes` | Detalle de participantes                 |
| `staging.stg_perfiles_trabajo`             | Descripciones de puestos (DFT)           |
| `staging.stg_proceso_seleccion`            | Procesos de selección y reclutamiento    |

## Variables de Entorno

Crear archivo `.env` en esta carpeta para personalizar:

```env
STG_ROOT_PASSWORD=password_root
STG_PORT=6001
STG_TEST_PASSWORD=test_password
STG_TEST_PORT=6002
```

## Comandos Útiles

```bash
# Bajar servicios
docker compose --profile prod down
docker compose --profile testing down

# Ver logs
docker compose --profile testing logs -f

# Reconstruir imagen (después de cambiar SQL)
docker compose --profile testing build --no-cache
docker compose --profile testing up -d

# Limpiar volúmenes (reset completo)
docker compose --profile testing down -v
```

# 💾 DWH-NODE: Base de Datos Unificada (DWH + Staging)

Nodo de base de datos **PostgreSQL 17** que contiene tanto el **Data Warehouse** como las tablas de **Staging** en una sola instancia, configurado con zona horaria `America/Santiago`.

## 🏗️ Arquitectura

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
         Puerto externo: 6000
```

## 📁 Estructura de Archivos

```
dwh-node/
├── docker-compose.yaml       # Orquestación del contenedor
├── Dockerfile                # Imagen producción (sin datos de prueba)
├── Dockerfile.testing        # Imagen testing (con datos de prueba)
├── database_staggin.sql      # Backup/referencia schema staging
├── scripts/
│   ├── compose-up.ps1        # Levantar contenedor (Windows)
│   ├── compose-up.sh         # Levantar contenedor (Linux/Mac)
│   ├── compose-down.ps1      # Detener contenedor (Windows)
│   └── compose-down.sh       # Detener contenedor (Linux/Mac)
└── init-scripts/
    ├── 01-users.sql          # Usuarios: dwh_admin, stg_admin
    ├── 02-schema-stg.sql     # Schema staging + tablas stg_*
    ├── 03-schema-dwh.sql     # Schema dwh + dims + facts
    └── 04-seed-test-data.sql # Datos de prueba (solo testing)
```

## ⚙️ Variables de Entorno

El contenedor usa estas variables (definidas en `docker-compose.yaml`):

| Variable            | Valor Default      | Descripción                             |
| ------------------- | ------------------ | --------------------------------------- |
| `POSTGRES_USER`     | `postgres`         | Superusuario PostgreSQL                 |
| `POSTGRES_PASSWORD` | `password_root`    | Password del superusuario               |
| `POSTGRES_DB`       | `rrhh_prod`        | Base de datos principal                 |
| `DWH_PORT`          | `6000`             | Puerto expuesto (mapea al 5432 interno) |
| `TZ`                | `America/Santiago` | Zona horaria del contenedor             |

Para cambiar el puerto externo:

```powershell
# Windows
$env:DWH_PORT = "6001"
docker compose up -d
```

```bash
# Linux/Mac
DWH_PORT=6001 docker compose up -d
```

## 🚀 Modos de Ejecución

### 🏭 Producción (sin datos de prueba)

```powershell
# Windows
.\scripts\compose-up.ps1

# Linux/Mac
./scripts/compose-up.sh

# O directamente
docker compose up -d
```

### 🧪 Testing (con datos de prueba)

```powershell
# Windows
$env:DOCKERFILE = "Dockerfile.testing"
docker compose up -d --build

# Linux/Mac
DOCKERFILE=Dockerfile.testing docker compose up -d --build
```

## 🔌 Conexión

| Usuario     | Password        | Schema | Permisos                |
| ----------- | --------------- | ------ | ----------------------- |
| `dwh_admin` | `sail-rrhh-p4`  | `dwh`  | ALL (dwh), SELECT (stg) |
| `stg_admin` | `sail-stg-p4`   | `stg`  | ALL (stg)               |
| `postgres`  | `password_root` | -      | Superuser               |

### Desde línea de comandos

```bash
# Usando psql desde el host
psql -h localhost -p 6000 -U dwh_admin -d rrhh_prod

# Dentro del contenedor
docker exec -it dwh_rrhh_container psql -U dwh_admin -d rrhh_prod

# Comandos útiles una vez conectado
\dn              # Listar schemas
\dt stg.*        # Ver tablas de staging
\dt dwh.*        # Ver tablas de dwh
\d dwh.dim_tiempo  # Describir tabla
```

### Connection String (para aplicaciones)

```
# SQLAlchemy / Python
postgresql+psycopg2://dwh_admin:sail-rrhh-p4@localhost:6000/rrhh_prod

# JDBC
jdbc:postgresql://localhost:6000/rrhh_prod?user=dwh_admin&password=sail-rrhh-p4
```

## 📊 Schemas y Tablas

### Schema `stg` (Staging)

Tablas temporales donde se cargan datos crudos:

- `stg_rotacion_empleados` - Datos maestro de empleados desde SAP
- `stg_capacitaciones_resumen` - Resumen mensual de capacitaciones
- `stg_capacitaciones_participantes` - Detalle de asistentes
- `stg_feriados` - Feriados extraídos de API externa

### Schema `dwh` (Data Warehouse)

**Dimensiones:**

- `dim_tiempo` - Calendario 2010-2028 con feriados Chile
- `dim_empleado` - SCD Tipo 2 con historial
- `dim_cargo` - Cargos y familias de puesto
- `dim_empresa` - Sociedades
- `dim_gerencia` - Estructura organizacional
- `dim_centro_costo` - Centros de costo
- `dim_modalidad_contrato` - Junk dimension (tipo empleo + jornada)
- `dim_turno` - Turnos de trabajo

**Facts:**

- `fact_rotacion` - Transaccional: movimientos de personal
- `fact_dotacion` - Snapshot: foto mensual de headcount

## 🔧 Healthcheck

El contenedor incluye un healthcheck que verifica:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres -d rrhh_prod"]
  interval: 10s
  timeout: 5s
  retries: 5
```

Para verificar el estado:

```bash
docker inspect dwh_rrhh_container --format='{{.State.Health.Status}}'
```

## 📦 Volumen de Datos

Los datos persisten en el volumen Docker `pg_data`:

```bash
# Ver volumen
docker volume inspect dwh-node_pg_data

# ⚠️ PELIGRO: Eliminar volumen (borra todos los datos)
docker compose down -v
```

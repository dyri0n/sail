# 🧠 ETL-NODE: Orquestación y Cómputo

Este directorio contiene los componentes activos del pipeline ETL: **Apache Airflow** (orquestación) y los **ETL Workers** (cómputo/ingesta).

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│                         ETL-NODE                             │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              📂 /airflow                             │    │
│  │         Apache Airflow 3.x (Orquestador)            │    │
│  │                                                     │    │
│  │  • Scheduler    - Programa y dispara tareas         │    │
│  │  • Webserver    - UI en puerto 8080                 │    │
│  │  • DAG Processor- Parsea y descubre DAGs            │    │
│  │  • Postgres     - Metadatos de Airflow              │    │
│  └────────────────────────┬────────────────────────────┘    │
│                           │                                  │
│                           │ DockerOperator                   │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              📂 /etl-workers                         │    │
│  │         Contenedores Python (Cómputo Pesado)        │    │
│  │                                                     │    │
│  │  • Pandas       - Transformación de datos           │    │
│  │  • SQLAlchemy   - Conexión a bases de datos         │    │
│  │  • Requests     - Consumo de APIs externas          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              📂 /input_data                          │    │
│  │            Landing Zone (Archivos Fuente)           │    │
│  │                                                     │    │
│  │  • Excel (.xlsx)  - Reportes SAP, nóminas           │    │
│  │  • CSV            - Exportaciones manuales          │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## 📁 Estructura de Directorios

```
etl-node/
├── 📂 airflow/              # Orquestador principal
│   ├── docker-compose.yaml  # Stack Airflow 3.x completo
│   ├── Dockerfile           # Imagen con providers
│   ├── .env.example         # Variables de entorno (COPIAR A .env)
│   ├── dags/                # Flujos de trabajo (DAGs)
│   ├── logs/                # Logs de ejecución
│   └── scripts/             # Scripts de gestión
│
├── 📂 etl-workers/          # Workers Python para tareas pesadas
│   ├── docker-compose.yaml  # Contenedor de pruebas
│   ├── Dockerfile           # Imagen Python 3.11
│   ├── requirements.txt     # Dependencias Python
│   └── scripts/             # Scripts de extracción
│
└── 📂 input_data/           # Landing zone para archivos fuente
    └── (archivos Excel/CSV depositados aquí)
```

## 🚀 Quick Start

### 1. Configurar Variables de Entorno

```powershell
cd airflow
cp .env.example .env
# Editar .env según tu entorno (ver documentación en airflow/README.md)
```

### 2. Levantar Airflow

```powershell
# Windows
.\airflow\scripts\compose-up.ps1

# Linux/Mac
./airflow/scripts/compose-up.sh
```

### 3. Acceder a la UI

- **URL**: http://localhost:8080
- **Usuario**: `admin`
- **Password**: `admin` (o el configurado en `.env`)

## 🔗 Conexiones

El nodo ETL se conecta al **DWH-NODE** usando estas credenciales (configuradas automáticamente por `airflow-init`):

| Connection ID | Host | Puerto | Usuario | Base de Datos |
|---------------|------|--------|---------|---------------|
| `dwh_postgres_conn` | `host.docker.internal` | `6000` | `dwh_admin` | `rrhh_prod` |

## 📖 Documentación Detallada

- [📂 airflow/README.md](./airflow/README.md) - Configuración completa de Airflow
- [📂 etl-workers/README.md](./etl-workers/README.md) - Workers de Python

# 🚀 SAIL - Sistema de Analytics e Inteligencia Laboral

<p align="center">
  <img src="https://img.shields.io/badge/PostgreSQL-17-336791?style=for-the-badge&logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Apache%20Airflow-3.1.5-017CEE?style=for-the-badge&logo=apache-airflow" alt="Airflow">
  <img src="https://img.shields.io/badge/Docker-24+-2496ED?style=for-the-badge&logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python" alt="Python">
</p>

---

## 📋 Descripción

**SAIL** es un Data Warehouse moderno para el área de **Recursos Humanos**, diseñado con arquitectura **Kimball** (modelo estrella). Permite centralizar, transformar y analizar datos de:

- 👥 **Dotación y Rotación** de personal
- 📚 **Capacitaciones** y desarrollo
- 📊 **Métricas de RRHH** (turnover, headcount, etc.)

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              SAIL - ARQUITECTURA                            │
└─────────────────────────────────────────────────────────────────────────────┘

     ┌──────────────────┐
     │   📁 INPUT_DATA  │  Archivos Excel/CSV
     │  (Landing Zone)  │  depositados manualmente
     └────────┬─────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ETL-NODE (Orquestación)                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    🌬️ APACHE AIRFLOW 3.x                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐   │   │
│  │  │  Scheduler  │  │  Webserver  │  │DAG Processor│  │  Postgres │   │   │
│  │  │             │  │   :8080     │  │  (parser)   │  │ (metadata)│   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│  ┌──────────────────┐              │                                        │
│  │ 🔨 ETL-WORKERS   │◄─────────────┘  DockerOperator                       │
│  │  (Python/Pandas) │     (orquesta contenedores efímeros)                 │
│  └──────────────────┘                                                      │
└───────────────────────────────────────────┬─────────────────────────────────┘
                                            │
                      SQL + Conexión        │
                      (dwh_postgres_conn)   │
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DWH-NODE (PostgreSQL 17)                           │
│                                                                             │
│     ┌───────────────────────────────────────────────────────────────┐       │
│     │                    📦 rrhh_prod (Database)                    │       │
│     │                                                               │       │
│     │   ┌─────────────────────┐    ┌─────────────────────┐         │       │
│     │   │    Schema: stg      │    │    Schema: dwh      │         │       │
│     │   │   (Staging Area)    │    │   (Data Warehouse)  │         │       │
│     │   │                     │    │                     │         │       │
│     │   │ • stg_rotacion_*    │───▶│ • dim_tiempo        │         │       │
│     │   │ • stg_capacitaciones│    │ • dim_empleado      │         │       │
│     │   │ • stg_feriados      │    │ • dim_cargo         │         │       │
│     │   │                     │    │ • dim_empresa       │         │       │
│     │   │   (Datos crudos,    │    │ • dim_gerencia      │         │       │
│     │   │    temporales)      │    │ • dim_centro_costo  │         │       │
│     │   │                     │    │ • fact_rotacion     │         │       │
│     │   │                     │    │ • fact_dotacion     │         │       │
│     │   └─────────────────────┘    └─────────────────────┘         │       │
│     └───────────────────────────────────────────────────────────────┘       │
│                                Puerto: 6000                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
SAIL/
├── 📂 dwh-node/                    # Nodo de Base de Datos
│   ├── docker-compose.yaml         # Orquestación PostgreSQL
│   ├── Dockerfile                  # Imagen producción
│   ├── Dockerfile.testing          # Imagen con datos de prueba
│   └── init-scripts/               # Scripts SQL de inicialización
│       ├── 01-users.sql            # Usuarios y roles
│       ├── 02-schema-stg.sql       # Schema staging
│       ├── 03-schema-dwh.sql       # Schema DWH (dims + facts)
│       └── 04-seed-test-data.sql   # Datos de prueba (testing)
│
├── 📂 etl-node/                    # Nodo de Procesamiento ETL
│   ├── 📂 airflow/                 # Apache Airflow (orquestador)
│   │   ├── docker-compose.yaml     # Stack completo Airflow 3.x
│   │   ├── Dockerfile              # Imagen con providers
│   │   ├── .env.example            # Variables de entorno ejemplo
│   │   ├── dags/                   # Flujos de trabajo
│   │   │   ├── dag_conformed.py    # DAG: Dimensiones conformadas
│   │   │   ├── dag_rotacion.py     # DAG: Facts de rotación
│   │   │   ├── config/settings.py  # Configuración centralizada
│   │   │   └── sql/                # Scripts SQL de transformación
│   │   │       ├── dimensiones/    # MERGE de dims
│   │   │       └── fact-tables/    # Carga de facts
│   │   └── logs/                   # Logs de ejecución
│   │
│   ├── 📂 etl-workers/             # Workers Python (cómputo pesado)
│   │   ├── docker-compose.yaml
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── scripts/                # Scripts de extracción
│   │       └── extract_feriados.py # API feriados Chile
│   │
│   └── 📂 input_data/              # Landing zone (archivos fuente)
│
└── 📂 scripts/                     # Scripts de gestión global
    ├── start-all.ps1 / .sh         # Levantar toda la infra
    └── stop-all.ps1 / .sh          # Detener toda la infra
```

---

## 🚀 Quick Start

### Prerrequisitos

- **Docker Desktop** 24+ con Docker Compose v2
- **PowerShell** 7+ (Windows) o **Bash** (Linux/Mac)
- **Git** para clonar el repositorio

### 1️⃣ Clonar y Configurar

```powershell
# Clonar repositorio
git clone https://github.com/dyri0n/sail.git
cd sail

# Configurar variables de entorno para Airflow
cd etl-node/airflow
cp .env.example .env
# Editar .env si es necesario (ver sección Configuración)
cd ../..
```

### 2️⃣ Levantar Infraestructura Completa

```powershell
# Windows (PowerShell)
.\scripts\start-all.ps1

# Linux/Mac
./scripts/start-all.sh
```

### 3️⃣ Verificar Servicios

| Servicio           | URL                   | Credenciales                 |
| ------------------ | --------------------- | ---------------------------- |
| **Airflow UI**     | http://localhost:8080 | `admin` / `admin`            |
| **PostgreSQL DWH** | `localhost:6000`      | `dwh_admin` / `sail-rrhh-p4` |

### 4️⃣ Ejecutar tu Primer DAG

1. Accede a http://localhost:8080
2. Activa el DAG `01_carga_dimensiones_conformadas`
3. Haz clic en ▶️ **Trigger DAG**
4. Observa la ejecución en el Graph View

---

## ⚙️ Configuración

### Variables de Entorno (Airflow)

Copia `etl-node/airflow/.env.example` a `.env` y ajusta:

```dotenv
# ============ CREDENCIALES AIRFLOW ============
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=tu_password_seguro
AIRFLOW_FERNET_KEY=genera_con_script

# ============ CONEXIÓN AL DWH ============
# Testing local (DWH en mismo host)
DWH_HOST=host.docker.internal
DWH_PORT=6000

# Producción (DWH en servidor remoto)
# DWH_HOST=192.168.1.50
# DWH_PORT=6000

DWH_USER=dwh_admin
DWH_PASSWORD=sail-rrhh-p4
DWH_DATABASE=rrhh_prod
```

### Generar Fernet Key (Seguridad)

```powershell
# Windows
.\etl-node\airflow\scripts\generate-fernet-key.ps1

# Linux/Mac
./etl-node/airflow/scripts/generate-fernet-key.sh
```

---

## 🔄 Pipeline ETL

### DAGs Disponibles

| DAG                                    | Descripción                               | Schedule |
| -------------------------------------- | ----------------------------------------- | -------- |
| `01_carga_dimensiones_conformadas`     | Carga dims: tiempo, empleado, cargo, etc. | `@daily` |
| `02_carga_hechos_movimientos_dotacion` | Carga facts: rotación, dotación snapshot  | `@daily` |

### Flujo de Datos

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Fuentes   │───▶│   Staging   │───▶│     DWH     │
│  (Excel/API)│    │  (stg.*)    │    │ (dim/fact)  │
└─────────────┘    └─────────────┘    └─────────────┘
     Paso 1            Paso 2             Paso 3
   (Workers)      (SQL Transform)     (Consumo BI)
```

---

## 🗄️ Modelo de Datos

### Dimensiones (Schema: `dwh`)

| Tabla                    | Descripción                   | Tipo       |
| ------------------------ | ----------------------------- | ---------- |
| `dim_tiempo`             | Calendario con feriados Chile | Estática   |
| `dim_empleado`           | Maestro de empleados          | SCD Tipo 2 |
| `dim_cargo`              | Cargos y familias de puesto   | Estática   |
| `dim_empresa`            | Sociedades/empresas           | Estática   |
| `dim_gerencia`           | Estructura organizacional     | Estática   |
| `dim_centro_costo`       | Centros de costo              | Estática   |
| `dim_modalidad_contrato` | Junk: Tipo empleo + Jornada   | Junk       |

### Tablas de Hechos (Schema: `dwh`)

| Tabla           | Descripción               | Granularidad       |
| --------------- | ------------------------- | ------------------ |
| `fact_rotacion` | Movimientos (altas/bajas) | Transaccional      |
| `fact_dotacion` | Foto mensual headcount    | Snapshot periódico |

---

## 🛠️ Comandos Útiles

### Docker

```powershell
# Ver contenedores activos
docker ps

# Logs de Airflow Scheduler
docker logs airflow-scheduler -f

# Logs del DWH
docker logs dwh_rrhh_container -f

# Conectar a PostgreSQL DWH
docker exec -it dwh_rrhh_container psql -U dwh_admin -d rrhh_prod
```

### Airflow CLI (dentro del contenedor)

```bash
# Listar DAGs
docker exec airflow-scheduler airflow dags list

# Trigger manual
docker exec airflow-scheduler airflow dags trigger 01_carga_dimensiones_conformadas

# Ver estado de tareas
docker exec airflow-scheduler airflow tasks list 01_carga_dimensiones_conformadas
```

### Detener Todo

```powershell
# Windows
.\scripts\stop-all.ps1

# Linux/Mac
./scripts/stop-all.sh
```

---

## 🧪 Testing

### Modo Testing (con datos de prueba)

```powershell
# Levantar DWH con seed data
cd dwh-node
$env:DOCKERFILE = "Dockerfile.testing"
docker compose up -d --build
```

### Worker Interactivo

```powershell
cd etl-node/etl-workers
docker compose --profile development up -d
docker exec -it etl-worker-shell bash
```

---

## 📊 Conexión desde Herramientas BI

### Power BI / Tableau / Metabase

```
Host: localhost (o IP del servidor)
Puerto: 6000
Base de datos: rrhh_prod
Usuario: dwh_admin
Password: sail-rrhh-p4
Schema: dwh
```

### Python (Pandas/SQLAlchemy)

```python
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine(
    "postgresql+psycopg2://dwh_admin:sail-rrhh-p4@localhost:6000/rrhh_prod"
)

# Ejemplo: Leer dimensión empleados
df = pd.read_sql("SELECT * FROM dwh.dim_empleado WHERE scd_es_actual = true", engine)
```

---

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama feature: `git checkout -b feature/nueva-dimension`
3. Commit cambios: `git commit -m 'Add dim_ubicacion'`
4. Push a la rama: `git push origin feature/nueva-dimension`
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 📞 Soporte

- 📧 Email: [soporte@ejemplo.cl](mailto:soporte@ejemplo.cl)
- 🐛 Issues: [GitHub Issues](https://github.com/dyri0n/sail/issues)

---

<p align="center">
  <sub>Built with ❤️ by Data Team</sub>
</p>

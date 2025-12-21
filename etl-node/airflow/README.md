# 🌬️ Airflow: El Cerebro del ETL

Apache Airflow **3.x** orquesta todos los flujos de trabajo del Data Warehouse. Esta versión utiliza el nuevo `LocalExecutor` y el componente `DAG Processor` separado.

## 📁 Estructura

```
airflow/
├── docker-compose.yaml       # Stack completo Airflow 3.x
├── Dockerfile                # Imagen con providers instalados
├── pyproject.toml            # Configuración proyecto Python
├── requirements-dev.txt      # Dependencias desarrollo
├── .env.example              # ⚠️ COPIAR A .env
│
├── dags/                     # Flujos de trabajo
│   ├── dag_conformed.py      # DAG 01: Carga dimensiones
│   ├── dag_rotacion.py       # DAG 02: Carga facts rotación
│   ├── example_dag.py        # Ejemplo de referencia
│   ├── trigger_etl.py        # Trigger manual
│   ├── config/
│   │   └── settings.py       # Configuración centralizada
│   └── sql/
│       ├── dimensiones/      # Scripts SQL para dims
│       └── fact-tables/      # Scripts SQL para facts
│
├── logs/                     # Logs de ejecución (auto-generado)
│
└── scripts/
    ├── compose-up.ps1        # Levantar (Windows)
    ├── compose-up.sh         # Levantar (Linux/Mac)
    ├── compose-down.ps1      # Detener (Windows)
    ├── compose-down.sh       # Detener (Linux/Mac)
    ├── generate-fernet-key.ps1  # Generar Fernet Key (Windows)
    └── generate-fernet-key.sh   # Generar Fernet Key (Linux/Mac)
```

## ⚙️ Configuración de Variables de Entorno

### Paso 1: Copiar archivo de ejemplo

```powershell
cp .env.example .env
```

### Paso 2: Configurar `.env`

El archivo `.env.example` contiene todas las variables documentadas. Las más importantes son:

#### 🔐 Credenciales Airflow

```dotenv
# Usuario admin para UI (http://localhost:8080)
AIRFLOW_ADMIN_USERNAME=admin
AIRFLOW_ADMIN_PASSWORD=admin            # ⚠️ Cambiar en producción

# Clave Fernet para encriptar conexiones (OBLIGATORIO cambiar)
AIRFLOW_FERNET_KEY=81HqDtbqAywKSOumSha3BhWNOdQ26slT6K0YaZeZyPs=

# UID del usuario dentro del contenedor
AIRFLOW_UID=50000
```

#### 🗄️ Conexión al DWH

```dotenv
# Para desarrollo local (DWH en mismo host)
DWH_HOST=host.docker.internal
DWH_PORT=6000

# Para producción (DWH en servidor remoto)
# DWH_HOST=192.168.1.50
# DWH_PORT=6000

DWH_USER=dwh_admin
DWH_PASSWORD=sail-rrhh-p4
DWH_DATABASE=rrhh_prod
```

### Paso 3: Generar Fernet Key (Seguridad)

```powershell
# Windows
.\scripts\generate-fernet-key.ps1

# Linux/Mac
./scripts/generate-fernet-key.sh

# O manualmente con Python
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Copia la clave generada a `AIRFLOW_FERNET_KEY` en tu `.env`.

## 🚀 Levantar Servicios

```powershell
# Windows
.\scripts\compose-up.ps1

# Linux/Mac
./scripts/compose-up.sh

# O directamente
docker compose up -d
```

### Servicios que se levantan:

| Servicio                | Puerto | Descripción                   |
| ----------------------- | ------ | ----------------------------- |
| `airflow-webserver`     | 8080   | UI web (API Server)           |
| `airflow-scheduler`     | -      | Programa tareas               |
| `airflow-dag-processor` | -      | Parsea DAGs (nuevo en 3.x)    |
| `airflow-init`          | -      | Inicializa BD y usuario admin |
| `postgres`              | -      | Metadatos de Airflow          |

### Verificar estado

```powershell
# Ver contenedores
docker compose ps

# Logs del scheduler
docker compose logs airflow-scheduler -f

# Logs de inicialización
docker compose logs airflow-init
```

## 🔄 DAGs Disponibles

### DAG 01: `01_carga_dimensiones_conformadas`

Carga todas las dimensiones maestras del DWH.

**Flujo:**

```
inicio_carga
    ├──> dim_tiempo (paralelo)
    ├──> dim_cargo (paralelo)
    ├──> dim_empresa (paralelo)
    ├──> dim_gerencia (paralelo)
    ├──> dim_centro_costo (paralelo)
    └──> dim_modalidad (paralelo)
              │
              ▼
         dim_empleado (SCD Tipo 2)
              │
              ▼
         fin_carga
```

**Schedule:** `@daily`

### DAG 02: `02_carga_hechos_movimientos_dotacion`

Carga las tablas de hechos de rotación y dotación.

**Flujo:**

```
inicio_facts
    │
    ▼
dim_medida
    │
    ▼
fact_rotacion_transaccional
    │
    ▼
fact_dotacion_snapshot
    │
    ▼
fin_facts
```

**Schedule:** `@daily`

## 🔌 Conexiones Configuradas

El servicio `airflow-init` crea automáticamente estas conexiones:

| Connection ID       | Tipo     | Host        | Puerto      | Schema          |
| ------------------- | -------- | ----------- | ----------- | --------------- |
| `dwh_postgres_conn` | Postgres | `$DWH_HOST` | `$DWH_PORT` | `$DWH_DATABASE` |

Para verificar o editar:

```bash
# Listar conexiones
docker exec airflow-scheduler airflow connections list

# Ver detalles
docker exec airflow-scheduler airflow connections get dwh_postgres_conn
```

## 📝 Archivos SQL

Los scripts SQL de transformación están en `dags/sql/`:

### Dimensiones (`sql/dimensiones/`)

| Archivo                      | Tabla Destino                | Descripción                      |
| ---------------------------- | ---------------------------- | -------------------------------- |
| `poblar_dim_tiempo.sql`      | `dwh.dim_tiempo`             | Genera calendario 2010-2028      |
| `update_feriados.sql`        | `dwh.dim_tiempo`             | Actualiza feriados desde staging |
| `dim_cargo.sql`              | `dwh.dim_cargo`              | MERGE cargos                     |
| `dim_empresa.sql`            | `dwh.dim_empresa`            | MERGE empresas                   |
| `dim_gerencia.sql`           | `dwh.dim_gerencia`           | MERGE gerencias                  |
| `dim_centro_costo.sql`       | `dwh.dim_centro_costo`       | MERGE centros de costo           |
| `dim_modalidad_contrato.sql` | `dwh.dim_modalidad_contrato` | MERGE modalidades                |
| `merge_dim_empleado.sql`     | `dwh.dim_empleado`           | SCD Tipo 2 empleados             |

### Tablas de Hechos (`sql/fact-tables/`)

| Archivo             | Tabla Destino       | Descripción                |
| ------------------- | ------------------- | -------------------------- |
| `fact_rotacion.sql` | `dwh.fact_rotacion` | Movimientos de personal    |
| `fact_dotacion.sql` | `dwh.fact_dotacion` | Snapshot mensual headcount |

## 🧪 Testing

### Ejecutar DAG manualmente

```bash
# Desde el host
docker exec airflow-scheduler airflow dags trigger 01_carga_dimensiones_conformadas

# Con parámetros
docker exec airflow-scheduler airflow dags trigger 01_carga_dimensiones_conformadas --conf '{"param1": "valor"}'
```

### Probar una tarea específica

```bash
docker exec airflow-scheduler airflow tasks test 01_carga_dimensiones_conformadas merge_dim_tiempo 2024-01-01
```

## 🐛 Troubleshooting

### Error: "Connection refused" al DWH

Verifica que `DWH_HOST` esté correcto en `.env`:

- Windows/Mac: `host.docker.internal`
- Linux: IP del host o nombre del contenedor

### Error: "Invalid Fernet Key"

Regenera la clave:

```powershell
.\scripts\generate-fernet-key.ps1
# Copia la clave a .env y reinicia
docker compose down
docker compose up -d
```

### DAGs no aparecen

Verifica los logs del DAG Processor:

```bash
docker compose logs airflow-dag-processor
```

### Limpiar y reiniciar todo

```powershell
docker compose down -v  # ⚠️ Elimina volúmenes
docker compose up -d --build
```

# 🔨 ETL-WORKERS: El Músculo de Cómputo

Contenedores **Python 3.11** dedicados a tareas de cómputo intensivas: extracción de APIs, transformación de archivos Excel/CSV, y carga masiva a staging.

## 📁 Estructura

```
etl-workers/
├── docker-compose.yaml    # Contenedores para testing/desarrollo
├── Dockerfile             # Imagen Python con dependencias
├── requirements.txt       # Dependencias: pandas, sqlalchemy, requests
└── scripts/
    └── extract_feriados.py   # Extrae feriados de API Boostr
```

## 🐍 Dependencias

El archivo `requirements.txt` incluye:

```
pandas>=2.0.0          # Manipulación de datos
requests>=2.31.0       # Consumo de APIs HTTP
sqlalchemy>=2.0.0      # ORM y conexión a BD
psycopg2-binary>=2.9.9 # Driver PostgreSQL
```

## 🚀 Uso

### Modo Testing (ejecutar tarea única)

```powershell
# Construir imagen
docker compose build

# Ejecutar script específico
docker compose run --rm etl-job python scripts/extract_feriados.py "postgresql+psycopg2://stg_admin:sail-stg-p4@host.docker.internal:6000/rrhh_prod"
```

### Modo Desarrollo (shell interactivo)

```powershell
# Levantar shell interactivo
docker compose --profile development up -d

# Conectar al contenedor
docker exec -it etl-worker-shell bash

# Dentro del contenedor
cd /app/scripts
python extract_feriados.py "postgresql://..."
```

## ⚙️ Variables de Entorno

El contenedor espera estas variables (configurar en docker-compose o al ejecutar):

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DB_URI` | Connection string completa | `postgresql+psycopg2://user:pass@host:port/db` |
| `LOG_LEVEL` | Nivel de logging | `DEBUG`, `INFO`, `WARNING` |

### Connection String para Staging

```
# Desde contenedor hacia DWH en host local
postgresql+psycopg2://stg_admin:sail-stg-p4@host.docker.internal:6000/rrhh_prod

# Si DWH está en servidor remoto
postgresql+psycopg2://stg_admin:sail-stg-p4@192.168.1.50:6000/rrhh_prod
```

## 📜 Scripts Disponibles

### `extract_feriados.py`

Extrae feriados de Chile desde la API pública de [Boostr](https://api.boostr.cl) y los carga a la tabla `stg.stg_feriados`.

**Uso:**

```bash
python scripts/extract_feriados.py "<CONNECTION_STRING>"
```

**Funcionamiento:**

1. Consulta API `https://api.boostr.cl/feriados/{año}.json` para cada año (2010-2028)
2. Extrae: fecha, nombre, tipo, irrenunciable
3. Carga a `stg.stg_feriados` (REPLACE completo)

**Output esperado:**

```
--- Iniciando extracción de feriados Chile (2010-2028) ---
Descargando 2010...
Descargando 2011...
...
Total extraído: 285 feriados.
Datos guardados en stg.stg_feriados
```

## 🔗 Integración con Airflow

Los workers se invocan desde Airflow usando `DockerOperator`:

```python
from airflow.providers.docker.operators.docker import DockerOperator

t_api_feriados = DockerOperator(
    task_id='worker_api_feriados',
    image='mi-sistema/etl-worker:latest',
    api_version='auto',
    auto_remove=True,
    docker_url='unix://var/run/docker.sock',
    network_mode='bridge',
    environment={
        'DB_URI': 'postgresql+psycopg2://stg_admin:sail-stg-p4@host.docker.internal:6000/rrhh_prod'
    },
    command='python /app/scripts/extract_feriados.py "$DB_URI"',
)
```

## 🏗️ Construir Imagen

```powershell
# Construir con tag
docker build -t mi-sistema/etl-worker:latest .

# Verificar
docker images | Select-String "etl-worker"
```

## 🐛 Troubleshooting

### Error: "Connection refused"

Verifica que el host esté accesible desde el contenedor:

```bash
# Dentro del contenedor
docker exec -it etl-worker-shell bash
apt-get update && apt-get install -y postgresql-client
psql -h host.docker.internal -p 6000 -U stg_admin -d rrhh_prod
```

### Error: "Module not found"

Reconstruir imagen:

```powershell
docker compose build --no-cache
```

### Logs de ejecución

```powershell
docker compose logs etl-job
```

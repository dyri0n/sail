# 📜 Scripts SQL de Transformación

Este directorio contiene la lógica de transformación del DWH, ejecutada por los DAGs de Airflow mediante `SQLExecuteQueryOperator`.

## 🏗️ Arquitectura de Datos

```
┌─────────────────┐         ┌─────────────────┐
│  Schema: stg    │         │  Schema: dwh    │
│  (Staging)      │────────▶│  (Warehouse)    │
│                 │  MERGE  │                 │
│  stg_rotacion   │  / SCD  │  dim_*, fact_*  │
│  stg_capacit... │         │                 │
└─────────────────┘         └─────────────────┘
```

## 📁 Estructura

```
sql/
├── dimensiones/              # Scripts para tablas dimensionales
│   ├── poblar_dim_tiempo.sql     # Genera calendario 2010-2028
│   ├── update_feriados.sql       # Actualiza feriados desde stg
│   ├── dim_cargo.sql             # MERGE cargos
│   ├── dim_empresa.sql           # MERGE empresas
│   ├── dim_gerencia.sql          # MERGE gerencias
│   ├── dim_centro_costo.sql      # MERGE centros de costo
│   ├── dim_modalidad_contrato.sql# MERGE modalidades
│   ├── dim_medida.sql            # Medidas para facts
│   └── merge_dim_empleado.sql    # SCD Tipo 2 empleados
│
└── fact-tables/              # Scripts para tablas de hechos
    ├── fact_rotacion.sql         # Movimientos de personal
    └── fact_dotacion.sql         # Snapshot mensual headcount
```

## 📋 Operaciones Soportadas

### MERGE (Upsert)

La mayoría de dimensiones usan lógica MERGE para insertar/actualizar:

```sql
-- Ejemplo patrón MERGE
INSERT INTO dwh.dim_cargo (nombre_cargo, familia_puesto)
SELECT DISTINCT nombre_cargo, familia_puesto
FROM stg.stg_rotacion_empleados
ON CONFLICT (nombre_cargo) DO UPDATE
SET familia_puesto = EXCLUDED.familia_puesto;
```

### SCD Tipo 2 (Slowly Changing Dimension)

La dimensión empleado mantiene historial de cambios:

```sql
-- Cierra registros que cambiaron
UPDATE dwh.dim_empleado
SET scd_fecha_fin_vigencia = CURRENT_DATE - 1,
    scd_es_actual = FALSE
WHERE empleado_id_nk IN (SELECT empleado_id FROM cambios_detectados)
  AND scd_es_actual = TRUE;

-- Inserta nuevas versiones
INSERT INTO dwh.dim_empleado (empleado_id_nk, ..., scd_es_actual)
SELECT ..., TRUE FROM cambios_detectados;
```

### Generación Matemática

`dim_tiempo` se genera sin necesidad de datos fuente:

```sql
-- Genera fechas desde 2010 hasta 2028
INSERT INTO dwh.dim_tiempo (tiempo_sk, fecha, anio, mes_numero, ...)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INTEGER AS tiempo_sk,
    d AS fecha,
    EXTRACT(YEAR FROM d) AS anio,
    ...
FROM generate_series('2010-01-01'::DATE, '2028-12-31'::DATE, '1 day') AS d;
```

## 🔗 Uso desde Airflow

Los DAGs referencian estos scripts con rutas relativas:

```python
# En dag_conformed.py
with DAG(..., template_searchpath=["/opt/airflow/dags/sql"]) as dag:

    t_dim_tiempo = SQLExecuteQueryOperator(
        task_id="merge_dim_tiempo",
        conn_id="dwh_postgres_conn",
        sql="dimensiones/poblar_dim_tiempo.sql",  # Ruta relativa
    )
```

## ⚠️ Consideraciones

1. **Orden de ejecución**: Las dimensiones deben cargarse ANTES que los hechos
2. **Idempotencia**: Los scripts deben poder ejecutarse múltiples veces sin duplicar datos
3. **Transacciones**: Cada script se ejecuta en una transacción (rollback automático si falla)
4. **Search Path**: Los scripts asumen `search_path` en el schema correcto (configurado en conexión)

## 🧪 Testing Manual

```sql
-- Conectar al DWH
psql -h localhost -p 6000 -U dwh_admin -d rrhh_prod

-- Ejecutar script manualmente
\i /path/to/sql/dimensiones/dim_cargo.sql

-- Verificar resultado
SELECT COUNT(*) FROM dwh.dim_cargo;
```

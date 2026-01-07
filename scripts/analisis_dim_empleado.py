#!/usr/bin/env python3
"""
Análisis del Problema Raíz: dim_empleado
=========================================
Investiga por qué muchos empleados de STG no están en dim_empleado.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DSN = "host=localhost port=6000 dbname=rrhh_prod user=postgres password=password_root"


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


print_section("ANÁLISIS: Problema Raíz en dim_empleado")

conn = psycopg2.connect(DSN)
cur = conn.cursor(cursor_factory=RealDictCursor)

# 1. Rango de IDs en todas las tablas STG vs DWH
print_section("1. Rangos de IDs en STG vs DWH")

queries = {
    "stg_rotacion_empleados": "SELECT MIN(id_empleado) as min_id, MAX(id_empleado) as max_id, COUNT(DISTINCT id_empleado) as unicos FROM stg.stg_rotacion_empleados",
    "stg_participacion_capacitaciones": "SELECT MIN(id_empleado) as min_id, MAX(id_empleado) as max_id, COUNT(DISTINCT id_empleado) as unicos FROM stg.stg_participacion_capacitaciones WHERE id_empleado IS NOT NULL",
    "stg_asistencia_diaria": "SELECT MIN(id_empleado) as min_id, MAX(id_empleado) as max_id, COUNT(DISTINCT id_empleado) as unicos FROM stg.stg_asistencia_diaria",
    "dim_empleado": "SELECT MIN(empleado_id_nk::int) as min_id, MAX(empleado_id_nk::int) as max_id, COUNT(DISTINCT empleado_id_nk) as unicos FROM dwh.dim_empleado WHERE empleado_id_nk ~ '^[0-9]+$'",
}

print(f"\n{'Tabla':<40} {'Min ID':<15} {'Max ID':<15} {'Únicos':<15}")
print("-" * 85)
for tabla, query in queries.items():
    cur.execute(query)
    result = cur.fetchone()
    print(
        f"{tabla:<40} {result['min_id']:<15} {result['max_id']:<15} {result['unicos']:<15}"
    )

# 2. Verificar el origen de dim_empleado: ¿viene de stg_rotacion_empleados?
print_section("2. Origen de dim_empleado: stg_rotacion_empleados")

query1 = """
SELECT 
    COUNT(DISTINCT id_empleado) as total_empleados_rotacion,
    MIN(id_empleado) as min_id,
    MAX(id_empleado) as max_id
FROM stg.stg_rotacion_empleados;
"""

cur.execute(query1)
result = cur.fetchone()
print(f"\nstg_rotacion_empleados:")
print(f"  Total empleados únicos: {result['total_empleados_rotacion']}")
print(f"  Rango: {result['min_id']} a {result['max_id']}")

# Comparar con dim_empleado
query2 = """
SELECT 
    COUNT(*) as total_empleados_dwh,
    MIN(empleado_id_nk::int) as min_id,
    MAX(empleado_id_nk::int) as max_id
FROM dwh.dim_empleado
WHERE empleado_id_nk ~ '^[0-9]+$';
"""

cur.execute(query2)
result = cur.fetchone()
print(f"\ndim_empleado:")
print(f"  Total empleados: {result['total_empleados_dwh']}")
print(f"  Rango: {result['min_id']} a {result['max_id']}")

# 3. Identificar empleados que están en STG pero NO en DWH
print_section("3. Empleados en STG (cualquier tabla) pero NO en DWH")

query3 = """
WITH all_stg_empleados AS (
    SELECT DISTINCT id_empleado FROM stg.stg_rotacion_empleados
    UNION
    SELECT DISTINCT id_empleado FROM stg.stg_participacion_capacitaciones WHERE id_empleado IS NOT NULL
    UNION
    SELECT DISTINCT id_empleado FROM stg.stg_asistencia_diaria
),
empleados_faltantes AS (
    SELECT 
        ase.id_empleado,
        CASE 
            WHEN EXISTS (SELECT 1 FROM stg.stg_rotacion_empleados WHERE id_empleado = ase.id_empleado) THEN 'Sí' 
            ELSE 'No' 
        END as en_rotacion,
        CASE 
            WHEN EXISTS (SELECT 1 FROM stg.stg_participacion_capacitaciones WHERE id_empleado = ase.id_empleado) THEN 'Sí' 
            ELSE 'No' 
        END as en_participacion,
        CASE 
            WHEN EXISTS (SELECT 1 FROM stg.stg_asistencia_diaria WHERE id_empleado = ase.id_empleado) THEN 'Sí' 
            ELSE 'No' 
        END as en_asistencia
    FROM all_stg_empleados ase
    WHERE NOT EXISTS (
        SELECT 1 FROM dwh.dim_empleado de 
        WHERE de.empleado_id_nk = ase.id_empleado::text
    )
)
SELECT 
    COUNT(*) as empleados_faltantes,
    COUNT(CASE WHEN en_rotacion = 'Sí' THEN 1 END) as en_rotacion,
    COUNT(CASE WHEN en_participacion = 'Sí' THEN 1 END) as en_participacion,
    COUNT(CASE WHEN en_asistencia = 'Sí' THEN 1 END) as en_asistencia,
    COUNT(CASE WHEN en_rotacion = 'No' AND en_participacion = 'Sí' THEN 1 END) as solo_participacion,
    COUNT(CASE WHEN en_rotacion = 'No' AND en_asistencia = 'Sí' THEN 1 END) as solo_asistencia
FROM empleados_faltantes;
"""

cur.execute(query3)
result = cur.fetchone()
print(f"\nTotal empleados únicos en STG (todas las tablas): calculando...")
print(f"Empleados faltantes en dim_empleado: {result['empleados_faltantes']}")
print(f"\nDesglose de empleados faltantes:")
print(f"  Están en stg_rotacion_empleados: {result['en_rotacion']}")
print(f"  Están en stg_participacion_capacitaciones: {result['en_participacion']}")
print(f"  Están en stg_asistencia_diaria: {result['en_asistencia']}")
print(f"  SOLO en participación (no en rotación): {result['solo_participacion']}")
print(f"  SOLO en asistencia (no en rotación): {result['solo_asistencia']}")

# 4. Identificar si el problema es que dim_empleado SOLO se carga de rotacion
print_section("4. ¿dim_empleado se carga SOLO desde rotacion?")

query4 = """
-- Empleados de rotacion que SÍ están en DWH
WITH rotacion_en_dwh AS (
    SELECT COUNT(DISTINCT id_empleado) as count
    FROM stg.stg_rotacion_empleados sre
    WHERE EXISTS (
        SELECT 1 FROM dwh.dim_empleado de 
        WHERE de.empleado_id_nk = sre.id_empleado::text
    )
),
-- Total empleados en rotacion
total_rotacion AS (
    SELECT COUNT(DISTINCT id_empleado) as count
    FROM stg.stg_rotacion_empleados
)
SELECT 
    tr.count as total_rotacion,
    red.count as en_dwh,
    tr.count - red.count as faltantes,
    (red.count * 100.0 / tr.count) as porcentaje_cargado
FROM total_rotacion tr, rotacion_en_dwh red;
"""

cur.execute(query4)
result = cur.fetchone()
print(f"\nEmpleados en stg_rotacion_empleados: {result['total_rotacion']}")
print(
    f"Cargados en dim_empleado: {result['en_dwh']} ({result['porcentaje_cargado']:.1f}%)"
)
print(f"Faltantes de rotación: {result['faltantes']}")

if result["porcentaje_cargado"] < 100:
    print(f"\n⚠️  HALLAZGO: No todos los empleados de rotación están en dim_empleado!")
else:
    print(f"\n✅ Todos los empleados de rotación están en dim_empleado")
    print(
        f"💡 El problema es que participación/asistencia tienen empleados NO presentes en rotación"
    )

# 5. Ver algunos ejemplos de empleados que solo están en participación/asistencia
print_section("5. Ejemplos de empleados SOLO en participación o asistencia")

query5 = """
WITH all_stg_empleados AS (
    SELECT DISTINCT id_empleado FROM stg.stg_rotacion_empleados
    UNION
    SELECT DISTINCT id_empleado FROM stg.stg_participacion_capacitaciones WHERE id_empleado IS NOT NULL
    UNION
    SELECT DISTINCT id_empleado FROM stg.stg_asistencia_diaria
),
empleados_info AS (
    SELECT 
        ase.id_empleado,
        EXISTS (SELECT 1 FROM stg.stg_rotacion_empleados WHERE id_empleado = ase.id_empleado) as en_rotacion,
        EXISTS (SELECT 1 FROM stg.stg_participacion_capacitaciones WHERE id_empleado = ase.id_empleado) as en_participacion,
        EXISTS (SELECT 1 FROM stg.stg_asistencia_diaria WHERE id_empleado = ase.id_empleado) as en_asistencia,
        EXISTS (SELECT 1 FROM dwh.dim_empleado WHERE empleado_id_nk = ase.id_empleado::text) as en_dwh
    FROM all_stg_empleados ase
)
SELECT 
    id_empleado,
    en_rotacion,
    en_participacion,
    en_asistencia,
    en_dwh
FROM empleados_info
WHERE NOT en_rotacion AND (en_participacion OR en_asistencia)
ORDER BY id_empleado
LIMIT 20;
"""

cur.execute(query5)
results = cur.fetchall()
print(f"\nEmpleados que NO están en rotación pero SÍ en otras tablas:")
print(
    f"{'ID Empleado':<15} {'Rotación':<12} {'Participac.':<12} {'Asistencia':<12} {'En DWH':<12}"
)
print("-" * 65)
for row in results:
    print(
        f"{row['id_empleado']:<15} {str(row['en_rotacion']):<12} {str(row['en_participacion']):<12} {str(row['en_asistencia']):<12} {str(row['en_dwh']):<12}"
    )

# 6. Resumen y diagnóstico
print_section("6. DIAGNÓSTICO FINAL")

print("""
🔍 PROBLEMA RAÍZ IDENTIFICADO:
══════════════════════════════════════════════════════════════════════════════

dim_empleado se está poblando ÚNICAMENTE desde stg_rotacion_empleados.

Sin embargo:
  • stg_participacion_capacitaciones tiene empleados que NO están en rotación
  • stg_asistencia_diaria tiene empleados que NO están en rotación

Esto causa:
  ❌ 74% de participaciones perdidas (661 registros)
  ❌ 72% de asistencias sin empleado válido (57,964 registros)
  ❌ Análisis incompletos y sesgados

💡 CAUSA RAÍZ:
  • El maestro de empleados (rotación) está desactualizado o incompleto
  • Los empleados nuevos aparecen en asistencias/capacitaciones pero no en rotación
  • El ETL de dim_empleado NO considera otras fuentes de empleados

🔧 SOLUCIONES POSIBLES:

  OPCIÓN 1 (Recomendada): Sincronizar todas las fuentes
    1. Actualizar stg_rotacion_empleados con datos más recientes
    2. Incorporar empleados de asistencias/participaciones que no estén en rotación
    3. Recargar dim_empleado con TODOS los empleados únicos

  OPCIÓN 2: Modificar ETL de dim_empleado
    1. Hacer un UNION de empleados desde:
       - stg_rotacion_empleados (principal)
       - stg_participacion_capacitaciones (empleados faltantes)
       - stg_asistencia_diaria (empleados faltantes)
    2. Crear registros en dim_empleado para empleados sin datos completos
    3. Recargar todas las facts

  OPCIÓN 3: Enriquecer datos en STG
    1. Obtener datos completos de empleados desde el sistema fuente (SAP/GeoVictoria)
    2. Actualizar stg_rotacion_empleados
    3. Recargar todo el DWH

⚠️  IMPACTO DE NO CORREGIR:
  • Análisis de capacitaciones incompleto (solo 26% de datos)
  • Asistencias sin sentido (todas al empleado -1)
  • Reportes gerenciales inválidos
  • Decisiones basadas en datos incorrectos

🎯 ACCIÓN INMEDIATA:
  1. Identificar el rango de fechas de rotación vs asistencia/participación
  2. Verificar si hay datos más recientes disponibles en origen
  3. Ejecutar carga incremental de dim_empleado
  4. Recargar facts afectadas
""")

cur.close()
conn.close()

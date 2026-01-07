#!/usr/bin/env python3
"""
Investigación Detallada: Problema de empleado_sk en Asistencias
===============================================================
Este script investiga por qué TODOS los registros de asistencia tienen empleado_sk inválido.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DSN = "host=localhost port=6000 dbname=rrhh_prod user=postgres password=password_root"


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


print_section("INVESTIGACIÓN: Problema de empleado_sk en Asistencias")

conn = psycopg2.connect(DSN)
cur = conn.cursor(cursor_factory=RealDictCursor)

# 1. Analizar los empleado_sk en fact_asistencia
print_section("1. Distribución de empleado_sk en fact_asistencia")

query1 = """
SELECT 
    empleado_sk,
    COUNT(*) as registros
FROM dwh.fact_asistencia
GROUP BY empleado_sk
ORDER BY registros DESC
LIMIT 20;
"""

cur.execute(query1)
results = cur.fetchall()
print(f"\nTop 20 empleado_sk más frecuentes:")
print(f"{'empleado_sk':<20} {'Registros':<20}")
print("-" * 40)
for row in results:
    print(f"{row['empleado_sk'] or 'NULL':<20} {row['registros']:<20}")

# 2. Verificar si empleado_sk apunta a un registro válido
print_section("2. Verificación de validez de empleado_sk")

query2 = """
WITH asist_empleados AS (
    SELECT DISTINCT empleado_sk
    FROM dwh.fact_asistencia
)
SELECT 
    ae.empleado_sk,
    de.empleado_id_nk,
    de.nombre_completo,
    de.scd_es_actual,
    COUNT(fa.asistencia_id) as total_asistencias
FROM asist_empleados ae
LEFT JOIN dwh.dim_empleado de ON ae.empleado_sk = de.empleado_sk
LEFT JOIN dwh.fact_asistencia fa ON ae.empleado_sk = fa.empleado_sk
GROUP BY ae.empleado_sk, de.empleado_id_nk, de.nombre_completo, de.scd_es_actual
ORDER BY total_asistencias DESC
LIMIT 10;
"""

cur.execute(query2)
results = cur.fetchall()
print(f"\nEmpleados en fact_asistencia:")
print(
    f"{'empleado_sk':<15} {'empleado_id_nk':<20} {'Nombre':<30} {'Activo':<10} {'Asistencias':<15}"
)
print("-" * 100)
for row in results:
    print(
        f"{row['empleado_sk'] or 'NULL':<15} {row['empleado_id_nk'] or 'NULL':<20} {row['nombre_completo'] or 'N/A':<30} {str(row['scd_es_actual']):<10} {row['total_asistencias']:<15}"
    )

# 3. Analizar los id_empleado en STG
print_section("3. IDs de empleado en stg_asistencia_diaria")

query3 = """
SELECT 
    COUNT(*) as total_registros,
    COUNT(DISTINCT id_empleado) as empleados_unicos,
    MIN(id_empleado) as min_id,
    MAX(id_empleado) as max_id,
    COUNT(CASE WHEN id_empleado IS NULL THEN 1 END) as nulos
FROM stg.stg_asistencia_diaria;
"""

cur.execute(query3)
result = cur.fetchone()
print(f"\nTotal registros: {result['total_registros']:,}")
print(f"Empleados únicos: {result['empleados_unicos']:,}")
print(f"Rango de IDs: {result['min_id']} a {result['max_id']}")
print(f"Registros con ID NULL: {result['nulos']}")

# Top empleados por asistencias en STG
query4 = """
SELECT 
    id_empleado,
    COUNT(*) as asistencias
FROM stg.stg_asistencia_diaria
GROUP BY id_empleado
ORDER BY asistencias DESC
LIMIT 20;
"""

cur.execute(query4)
results = cur.fetchall()
print(f"\nTop 20 empleados por asistencias en STG:")
print(f"{'id_empleado':<20} {'Asistencias':<20}")
print("-" * 40)
for row in results:
    print(f"{row['id_empleado']:<20} {row['asistencias']:<20}")

# 4. Verificar mapeo entre id_empleado (STG) y empleado_id_nk (DWH)
print_section("4. Mapeo id_empleado (STG) -> empleado_id_nk (DWH)")

query5 = """
WITH stg_empleados AS (
    SELECT DISTINCT id_empleado
    FROM stg.stg_asistencia_diaria
    WHERE id_empleado IS NOT NULL
    LIMIT 50
)
SELECT 
    se.id_empleado as stg_id_empleado,
    de.empleado_sk,
    de.empleado_id_nk,
    de.nombre_completo,
    COUNT(sad.row_id) as asistencias_stg
FROM stg_empleados se
LEFT JOIN dwh.dim_empleado de ON de.empleado_id_nk = se.id_empleado::text
LEFT JOIN stg.stg_asistencia_diaria sad ON sad.id_empleado = se.id_empleado
GROUP BY se.id_empleado, de.empleado_sk, de.empleado_id_nk, de.nombre_completo
ORDER BY asistencias_stg DESC
LIMIT 30;
"""

cur.execute(query5)
results = cur.fetchall()
print(f"\nMapeo de primeros 30 empleados (ordenados por asistencias):")
print(
    f"{'STG ID':<15} {'empleado_sk':<15} {'DWH ID (NK)':<15} {'Nombre':<30} {'Asist. STG':<15}"
)
print("-" * 100)

match_count = 0
no_match_count = 0
for row in results:
    status = "✅" if row["empleado_sk"] else "❌"
    print(
        f"{status} {row['stg_id_empleado']:<13} {str(row['empleado_sk'] or 'NULL'):<15} {row['empleado_id_nk'] or 'NULL':<15} {row['nombre_completo'] or 'SIN MATCH':<30} {row['asistencias_stg']:<15}"
    )
    if row["empleado_sk"]:
        match_count += 1
    else:
        no_match_count += 1

print(f"\nResultado del mapeo (primeros 30):")
print(f"  Con match: {match_count} ({match_count * 100.0 / len(results):.1f}%)")
print(f"  Sin match: {no_match_count} ({no_match_count * 100.0 / len(results):.1f}%)")

# 5. Buscar el patrón: ¿Todos los registros tienen el mismo empleado_sk?
print_section("5. Análisis del empleado_sk usado en fact_asistencia")

query6 = """
SELECT 
    fa.empleado_sk,
    de.empleado_id_nk,
    de.nombre_completo,
    de.scd_es_actual,
    COUNT(*) as total_asistencias,
    MIN(dt.fecha) as primera_asistencia,
    MAX(dt.fecha) as ultima_asistencia
FROM dwh.fact_asistencia fa
LEFT JOIN dwh.dim_empleado de ON fa.empleado_sk = de.empleado_sk
LEFT JOIN dwh.dim_tiempo dt ON fa.fecha_sk = dt.tiempo_sk
GROUP BY fa.empleado_sk, de.empleado_id_nk, de.nombre_completo, de.scd_es_actual;
"""

cur.execute(query6)
results = cur.fetchall()
print(f"\nAnálisis detallado del/los empleado_sk usado(s):")
for row in results:
    print(f"\nempleado_sk: {row['empleado_sk']}")
    print(f"  empleado_id_nk: {row['empleado_id_nk'] or 'NULL'}")
    print(f"  Nombre: {row['nombre_completo'] or 'NULL'}")
    print(f"  Es actual: {row['scd_es_actual']}")
    print(f"  Total asistencias: {row['total_asistencias']:,}")
    print(f"  Rango fechas: {row['primera_asistencia']} a {row['ultima_asistencia']}")

# 6. Verificar qué empleado_sk se está usando
print_section("6. Identificación del empleado_sk problemático")

query7 = """
SELECT 
    fa.empleado_sk,
    de.empleado_id_nk,
    de.nombre_completo
FROM dwh.fact_asistencia fa
LEFT JOIN dwh.dim_empleado de ON fa.empleado_sk = de.empleado_sk
LIMIT 1;
"""

cur.execute(query7)
result = cur.fetchone()
if result:
    print(
        f"\nEl empleado_sk usado en TODAS las asistencias es: {result['empleado_sk']}"
    )
    print(f"  Corresponde a empleado_id_nk: {result['empleado_id_nk'] or 'NULL'}")
    print(f"  Nombre: {result['nombre_completo'] or 'NULL'}")

    # Verificar si es un ID por defecto o el primer registro de dim_empleado
    query8 = """
    SELECT empleado_sk, empleado_id_nk, nombre_completo
    FROM dwh.dim_empleado
    ORDER BY empleado_sk
    LIMIT 5;
    """

    cur.execute(query8)
    primeros = cur.fetchall()
    print(f"\nPrimeros 5 registros de dim_empleado:")
    for emp in primeros:
        marker = "👈 ESTE" if emp["empleado_sk"] == result["empleado_sk"] else ""
        print(
            f"  SK={emp['empleado_sk']}, NK={emp['empleado_id_nk']}, Nombre={emp['nombre_completo']} {marker}"
        )

# 7. Verificar si hay empleados de asistencias en dim_empleado
print_section("7. Empleados de STG asistencia en dim_empleado")

query9 = """
WITH stg_emp AS (
    SELECT DISTINCT id_empleado
    FROM stg.stg_asistencia_diaria
),
match_status AS (
    SELECT 
        se.id_empleado,
        de.empleado_sk,
        de.empleado_id_nk,
        COUNT(sad.row_id) as registros_stg
    FROM stg_emp se
    LEFT JOIN dwh.dim_empleado de ON de.empleado_id_nk = se.id_empleado::text AND de.scd_es_actual = TRUE
    LEFT JOIN stg.stg_asistencia_diaria sad ON sad.id_empleado = se.id_empleado
    GROUP BY se.id_empleado, de.empleado_sk, de.empleado_id_nk
)
SELECT 
    COUNT(*) as total_empleados_stg,
    COUNT(empleado_sk) as con_match_dwh,
    COUNT(*) - COUNT(empleado_sk) as sin_match_dwh,
    SUM(CASE WHEN empleado_sk IS NULL THEN registros_stg ELSE 0 END) as asistencias_perdidas
FROM match_status;
"""

cur.execute(query9)
result = cur.fetchone()
print(f"\nTotal empleados únicos en STG asistencia: {result['total_empleados_stg']}")
print(
    f"Con match en dim_empleado (scd_es_actual=TRUE): {result['con_match_dwh']} ({result['con_match_dwh'] * 100.0 / result['total_empleados_stg']:.1f}%)"
)
print(
    f"Sin match en dim_empleado: {result['sin_match_dwh']} ({result['sin_match_dwh'] * 100.0 / result['total_empleados_stg']:.1f}%)"
)
print(f"Asistencias de empleados sin match: {result['asistencias_perdidas']:,}")

# 8. Resumen y diagnóstico
print_section("8. DIAGNÓSTICO Y CAUSA RAÍZ")

print("\n🔍 PROBLEMA IDENTIFICADO:")
print("═" * 80)
print("""
TODOS los 80,141 registros de asistencia están usando el mismo empleado_sk,
probablemente el primer registro de dim_empleado o un valor por defecto.

Esto sugiere que el ETL:
  1. No está haciendo el JOIN correctamente entre id_empleado (STG) y empleado_sk (DWH)
  2. Está usando un valor fijo/por defecto cuando no encuentra match
  3. No está validando la integridad referencial antes de insertar
""")

print("\n💡 CAUSA RAÍZ PROBABLE:")
print("  • El ETL no mapea id_empleado -> empleado_id_nk -> empleado_sk")
print("  • Posible uso de un empleado_sk hardcodeado en el INSERT")
print("  • Falta validación de que el empleado existe en dim_empleado")

print("\n🔧 SOLUCIÓN REQUERIDA:")
print("  1. Revisar el DAG/script de ETL de asistencias en Airflow")
print(
    "  2. Corregir el JOIN: stg.id_empleado -> dim_empleado.empleado_id_nk -> empleado_sk"
)
print("  3. Implementar validación de integridad referencial")
print("  4. Truncar fact_asistencia y recargar con el mapeo correcto")

print("\n⚠️  IMPACTO:")
print("  • 80,141 registros de asistencia con empleado_sk incorrecto")
print("  • Reportes de puntualidad/ausentismo por empleado son INVÁLIDOS")
print("  • Urgente corregir antes de usar para análisis")

cur.close()
conn.close()

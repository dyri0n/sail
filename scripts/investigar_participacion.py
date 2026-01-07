#!/usr/bin/env python3
"""
Investigación Detallada: Problema de Participación en Capacitaciones
=====================================================================
Este script investiga por qué se pierden 661 registros (74%) de participaciones.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DSN = "host=localhost port=6000 dbname=rrhh_prod user=postgres password=password_root"


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


print_section("INVESTIGACIÓN: Pérdida de Participaciones en Capacitaciones")

conn = psycopg2.connect(DSN)
cur = conn.cursor(cursor_factory=RealDictCursor)

# 1. Verificar empleados en STG que NO están en dim_empleado
print_section("1. Empleados en STG sin match en dim_empleado")

query1 = """
WITH empleados_stg AS (
    SELECT DISTINCT 
        id_empleado,
        rut,
        nombre,
        apellidos
    FROM stg.stg_participacion_capacitaciones
    WHERE id_empleado IS NOT NULL
),
empleados_sin_match AS (
    SELECT 
        es.id_empleado,
        es.rut,
        es.nombre,
        es.apellidos,
        COUNT(*) OVER (PARTITION BY es.id_empleado) as participaciones
    FROM empleados_stg es
    WHERE NOT EXISTS (
        SELECT 1 FROM dwh.dim_empleado de 
        WHERE de.empleado_id_nk = es.id_empleado::text
    )
)
SELECT 
    COUNT(DISTINCT id_empleado) as total_empleados_sin_match,
    SUM(participaciones) as participaciones_perdidas
FROM empleados_sin_match;
"""

cur.execute(query1)
result = cur.fetchone()
print(f"\nEmpleados sin match: {result['total_empleados_sin_match']}")
print(f"Participaciones perdidas por este motivo: {result['participaciones_perdidas']}")

# Mostrar algunos ejemplos
query2 = """
WITH empleados_stg AS (
    SELECT DISTINCT 
        id_empleado,
        rut,
        nombre,
        apellidos
    FROM stg.stg_participacion_capacitaciones
    WHERE id_empleado IS NOT NULL
)
SELECT 
    es.id_empleado,
    es.rut,
    es.nombre || ' ' || es.apellidos as nombre_completo,
    COUNT(spc.id_registro) as participaciones
FROM empleados_stg es
LEFT JOIN stg.stg_participacion_capacitaciones spc ON es.id_empleado = spc.id_empleado
WHERE NOT EXISTS (
    SELECT 1 FROM dwh.dim_empleado de 
    WHERE de.empleado_id_nk = es.id_empleado::text
)
GROUP BY es.id_empleado, es.rut, es.nombre, es.apellidos
ORDER BY participaciones DESC
LIMIT 20;
"""

cur.execute(query2)
results = cur.fetchall()
print(f"\nEjemplos de empleados sin match (top 20 por participaciones):")
print(f"{'ID Empleado':<15} {'RUT':<15} {'Nombre':<40} {'Participaciones':<15}")
print("-" * 85)
for row in results:
    print(
        f"{row['id_empleado']:<15} {row['rut'] or 'N/A':<15} {row['nombre_completo']:<40} {row['participaciones']:<15}"
    )

# 2. Verificar si hay empleados en dim_empleado
print_section("2. Estado de dim_empleado")

query3 = """
SELECT 
    COUNT(*) as total_empleados,
    COUNT(DISTINCT empleado_id_nk) as empleados_unicos_nk,
    COUNT(CASE WHEN scd_es_actual = TRUE THEN 1 END) as empleados_activos,
    MIN(empleado_id_nk::int) as min_id,
    MAX(empleado_id_nk::int) as max_id
FROM dwh.dim_empleado
WHERE empleado_id_nk ~ '^[0-9]+$';
"""

cur.execute(query3)
result = cur.fetchone()
print(f"\nTotal empleados en dim_empleado: {result['total_empleados']}")
print(f"Empleados únicos (empleado_id_nk): {result['empleados_unicos_nk']}")
print(f"Empleados con scd_es_actual=TRUE: {result['empleados_activos']}")
print(f"Rango de IDs: {result['min_id']} a {result['max_id']}")

# 3. Verificar el tipo de dato y formato
print_section("3. Verificación de formato de IDs")

query4 = """
SELECT 
    'STG' as origen,
    MIN(id_empleado) as min_id,
    MAX(id_empleado) as max_id,
    COUNT(DISTINCT id_empleado) as unicos
FROM stg.stg_participacion_capacitaciones
WHERE id_empleado IS NOT NULL

UNION ALL

SELECT 
    'DWH' as origen,
    MIN(empleado_id_nk::int) as min_id,
    MAX(empleado_id_nk::int) as max_id,
    COUNT(DISTINCT empleado_id_nk) as unicos
FROM dwh.dim_empleado
WHERE empleado_id_nk ~ '^[0-9]+$';
"""

cur.execute(query4)
results = cur.fetchall()
print(f"\n{'Origen':<10} {'Min ID':<15} {'Max ID':<15} {'Únicos':<15}")
print("-" * 55)
for row in results:
    print(
        f"{row['origen']:<10} {row['min_id']:<15} {row['max_id']:<15} {row['unicos']:<15}"
    )

# 4. Verificar si el problema es por RUT vs ID
print_section("4. Mapeo por RUT vs ID")

query5 = """
WITH stg_empleados AS (
    SELECT DISTINCT 
        id_empleado,
        rut
    FROM stg.stg_participacion_capacitaciones
    WHERE id_empleado IS NOT NULL AND rut IS NOT NULL
)
SELECT 
    COUNT(*) as total_en_stg,
    COUNT(CASE WHEN de1.empleado_sk IS NOT NULL THEN 1 END) as match_por_id,
    COUNT(CASE WHEN de2.empleado_sk IS NOT NULL THEN 1 END) as match_por_rut,
    COUNT(CASE WHEN de1.empleado_sk IS NULL AND de2.empleado_sk IS NULL THEN 1 END) as sin_match
FROM stg_empleados se
LEFT JOIN dwh.dim_empleado de1 ON de1.empleado_id_nk = se.id_empleado::text
LEFT JOIN dwh.dim_empleado de2 ON de2.rut = se.rut;
"""

cur.execute(query5)
result = cur.fetchone()
print(f"\nTotal empleados únicos en STG con RUT: {result['total_en_stg']}")
print(
    f"Match por ID (empleado_id_nk): {result['match_por_id']} ({result['match_por_id'] * 100.0 / result['total_en_stg']:.1f}%)"
)
print(
    f"Match por RUT: {result['match_por_rut']} ({result['match_por_rut'] * 100.0 / result['total_en_stg']:.1f}%)"
)
print(f"Sin match por ningún método: {result['sin_match']}")

# 5. Verificar cursos sin match
print_section("5. Cursos en STG sin match en dim_curso")

query6 = """
WITH cursos_sin_match AS (
    SELECT DISTINCT 
        spc.nombre_curso,
        COUNT(*) as participaciones
    FROM stg.stg_participacion_capacitaciones spc
    WHERE NOT EXISTS (
        SELECT 1 FROM dwh.dim_curso dc 
        WHERE LOWER(TRIM(dc.nombre_curso)) = LOWER(TRIM(spc.nombre_curso))
    )
    GROUP BY spc.nombre_curso
)
SELECT 
    COUNT(*) as cursos_sin_match,
    SUM(participaciones) as participaciones_afectadas
FROM cursos_sin_match;
"""

cur.execute(query6)
result = cur.fetchone()
print(f"\nCursos sin match: {result['cursos_sin_match']}")
print(f"Participaciones afectadas: {result['participaciones_afectadas']}")

# 6. Analizar registros que SÍ se cargaron
print_section("6. Análisis de registros cargados exitosamente")

query7 = """
WITH loaded_participations AS (
    SELECT 
        fpc.empleado_sk,
        de.empleado_id_nk,
        de.nombre_completo,
        COUNT(*) as participaciones_cargadas
    FROM dwh.fact_participacion_capacitacion fpc
    JOIN dwh.dim_empleado de ON fpc.empleado_sk = de.empleado_sk
    GROUP BY fpc.empleado_sk, de.empleado_id_nk, de.nombre_completo
)
SELECT 
    COUNT(*) as empleados_con_participaciones,
    SUM(participaciones_cargadas) as total_participaciones,
    AVG(participaciones_cargadas) as promedio_por_empleado,
    MIN(participaciones_cargadas) as min_participaciones,
    MAX(participaciones_cargadas) as max_participaciones
FROM loaded_participations;
"""

cur.execute(query7)
result = cur.fetchone()
print(
    f"\nEmpleados con participaciones en DWH: {result['empleados_con_participaciones']}"
)
print(f"Total participaciones cargadas: {result['total_participaciones']}")
print(f"Promedio por empleado: {result['promedio_por_empleado']:.2f}")
print(
    f"Rango: {result['min_participaciones']} a {result['max_participaciones']} participaciones"
)

# 7. Verificar si hay empleados con RUT pero sin ID o viceversa
print_section("7. Completitud de datos en STG")

query8 = """
SELECT 
    COUNT(*) as total_registros,
    COUNT(id_empleado) as con_id_empleado,
    COUNT(rut) as con_rut,
    COUNT(CASE WHEN id_empleado IS NULL AND rut IS NULL THEN 1 END) as sin_id_ni_rut,
    COUNT(CASE WHEN id_empleado IS NULL AND rut IS NOT NULL THEN 1 END) as solo_rut,
    COUNT(CASE WHEN id_empleado IS NOT NULL AND rut IS NULL THEN 1 END) as solo_id
FROM stg.stg_participacion_capacitaciones;
"""

cur.execute(query8)
result = cur.fetchone()
print(f"\nTotal registros en STG: {result['total_registros']}")
print(
    f"Con ID empleado: {result['con_id_empleado']} ({result['con_id_empleado'] * 100.0 / result['total_registros']:.1f}%)"
)
print(
    f"Con RUT: {result['con_rut']} ({result['con_rut'] * 100.0 / result['total_registros']:.1f}%)"
)
print(f"Sin ID ni RUT: {result['sin_id_ni_rut']}")
print(f"Solo RUT (sin ID): {result['solo_rut']}")
print(f"Solo ID (sin RUT): {result['solo_id']}")

# 8. Resumen final
print_section("8. RESUMEN Y DIAGNÓSTICO")

print("\n🔍 CAUSAS IDENTIFICADAS:")
print("═" * 80)

# Calcular porcentajes
total_stg = 892
total_dwh = 231
perdidas = total_stg - total_dwh

print(
    f"\nPérdida total: {perdidas} registros ({perdidas * 100.0 / total_stg:.1f}% de los datos)"
)
print("\nPosibles causas:")
print("  1. Empleados sin match en dim_empleado")
print("  2. Cursos sin match en dim_curso")
print("  3. Problemas en el ETL (filtros, errores de carga)")
print("  4. Datos incompletos en STG (sin ID o RUT)")

print("\n💡 RECOMENDACIONES:")
print("  • Revisar el proceso de carga de dim_empleado desde stg_rotacion_empleados")
print("  • Implementar matching por RUT como fallback si no hay match por ID")
print("  • Verificar los logs del DAG de capacitaciones en Airflow")
print("  • Implementar validación de integridad referencial ANTES de cargar a DWH")

cur.close()
conn.close()

#!/usr/bin/env python3
"""
Investigación del problema de empleado_sk en fact_asistencia
============================================================
Analiza por qué el JOIN SCD2 no funciona y propone soluciones.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DSN = "host=localhost port=6000 dbname=rrhh_prod user=postgres password=password_root"


def print_section(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


print_section("INVESTIGACIÓN: JOIN SCD2 en fact_asistencia")

conn = psycopg2.connect(DSN)
cur = conn.cursor(cursor_factory=RealDictCursor)

# 1. Ver estado de fechas SCD en dim_empleado
print_section("1. Estado de fechas SCD en dim_empleado")
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(scd_fecha_inicio_vigencia) as con_fecha_inicio,
        COUNT(scd_fecha_fin_vigencia) as con_fecha_fin,
        MIN(scd_fecha_inicio_vigencia) as min_inicio,
        MAX(scd_fecha_fin_vigencia) as max_fin
    FROM dwh.dim_empleado
""")
r = cur.fetchone()
for k, v in r.items():
    print(f"  {k}: {v}")

# 2. Ejemplo de empleados
print_section("2. Ejemplos de dim_empleado (primeros 10)")
cur.execute("""
    SELECT empleado_sk, empleado_id_nk, scd_fecha_inicio_vigencia, scd_fecha_fin_vigencia, scd_es_actual
    FROM dwh.dim_empleado 
    ORDER BY empleado_sk
    LIMIT 10
""")
print(f"{'SK':<8} {'NK':<12} {'Fecha Inicio':<15} {'Fecha Fin':<15} {'Actual':<8}")
print("-" * 60)
for r in cur.fetchall():
    print(
        f"{r['empleado_sk']:<8} {r['empleado_id_nk']:<12} {str(r['scd_fecha_inicio_vigencia']):<15} {str(r['scd_fecha_fin_vigencia']):<15} {str(r['scd_es_actual']):<8}"
    )

# 3. Rango de fechas en asistencias
print_section("3. Rango de fechas en stg_asistencia_diaria")
cur.execute("""
    SELECT 
        MIN(asistio_en) as fecha_min,
        MAX(asistio_en) as fecha_max,
        COUNT(DISTINCT asistio_en) as dias_unicos
    FROM stg.stg_asistencia_diaria
""")
r = cur.fetchone()
print(f"  Rango: {r['fecha_min']} a {r['fecha_max']}")
print(f"  Días únicos: {r['dias_unicos']}")

# 4. Test del JOIN original (con BETWEEN)
print_section("4. Test del JOIN original del ETL (con BETWEEN)")
cur.execute("""
    SELECT 
        COUNT(*) as total_stg,
        COUNT(de.empleado_sk) as con_match,
        COUNT(*) - COUNT(de.empleado_sk) as sin_match
    FROM stg.stg_asistencia_diaria s
    LEFT JOIN dwh.dim_empleado de 
        ON CAST(s.id_empleado AS VARCHAR) = de.empleado_id_nk 
        AND s.asistio_en BETWEEN de.scd_fecha_inicio_vigencia AND de.scd_fecha_fin_vigencia
""")
r = cur.fetchone()
print(f"  Total STG: {r['total_stg']:,}")
print(
    f"  Con match: {r['con_match']:,} ({r['con_match'] * 100.0 / r['total_stg']:.1f}%)"
)
print(
    f"  Sin match: {r['sin_match']:,} ({r['sin_match'] * 100.0 / r['total_stg']:.1f}%)"
)

# 5. Test sin condición de fecha (solo scd_es_actual)
print_section("5. Test con scd_es_actual = TRUE (sin BETWEEN)")
cur.execute("""
    SELECT 
        COUNT(*) as total_stg,
        COUNT(de.empleado_sk) as con_match,
        COUNT(*) - COUNT(de.empleado_sk) as sin_match
    FROM stg.stg_asistencia_diaria s
    LEFT JOIN dwh.dim_empleado de 
        ON CAST(s.id_empleado AS VARCHAR) = de.empleado_id_nk 
        AND de.scd_es_actual = TRUE
""")
r = cur.fetchone()
print(f"  Total STG: {r['total_stg']:,}")
print(
    f"  Con match: {r['con_match']:,} ({r['con_match'] * 100.0 / r['total_stg']:.1f}%)"
)
print(
    f"  Sin match: {r['sin_match']:,} ({r['sin_match'] * 100.0 / r['total_stg']:.1f}%)"
)

# 6. Ver qué empleados de asistencia NO están en dim_empleado
print_section("6. Empleados en asistencia que NO están en dim_empleado")
cur.execute("""
    SELECT COUNT(DISTINCT s.id_empleado) as empleados_sin_match
    FROM stg.stg_asistencia_diaria s
    WHERE NOT EXISTS (
        SELECT 1 FROM dwh.dim_empleado de 
        WHERE de.empleado_id_nk = CAST(s.id_empleado AS VARCHAR)
    )
""")
r = cur.fetchone()
print(f"  Empleados sin match en dim_empleado: {r['empleados_sin_match']}")

# Total de empleados únicos
cur.execute(
    "SELECT COUNT(DISTINCT id_empleado) as total FROM stg.stg_asistencia_diaria"
)
total = cur.fetchone()["total"]
print(f"  Total empleados únicos en STG: {total}")
print(f"  Empleados CON match: {total - r['empleados_sin_match']}")

# 7. Ver qué valores de empleado_sk tiene fact_asistencia actualmente
print_section("7. Valores de empleado_sk en fact_asistencia actual")
cur.execute("""
    SELECT 
        empleado_sk,
        COUNT(*) as registros
    FROM dwh.fact_asistencia
    GROUP BY empleado_sk
    ORDER BY registros DESC
    LIMIT 10
""")
results = cur.fetchall()
print(f"{'empleado_sk':<15} {'Registros':<15}")
print("-" * 30)
for r in results:
    print(f"{r['empleado_sk']:<15} {r['registros']:,}")

# 8. Diagnóstico final
print_section("8. DIAGNÓSTICO")

# Contar problemas
cur.execute("""
    SELECT COUNT(*) FROM dwh.dim_empleado 
    WHERE scd_fecha_inicio_vigencia IS NULL OR scd_fecha_fin_vigencia IS NULL
""")
sin_fechas = cur.fetchone()["count"]

print(f"""
🔍 PROBLEMAS IDENTIFICADOS:

1. Empleados con fechas SCD NULL: {sin_fechas}
   → El BETWEEN falla si las fechas son NULL

2. Empleados en asistencia sin match en dim_empleado: {r["empleados_sin_match"]} de {total}
   → Estos NUNCA tendrán empleado_sk válido

3. El ETL usa COALESCE(de.empleado_sk, -1) cuando no hay match
   → Por eso TODOS los registros tienen empleado_sk = -1

💡 SOLUCIÓN PROPUESTA:

   OPCIÓN A (Conservar datos): 
   - Cambiar JOIN de BETWEEN a scd_es_actual = TRUE
   - Crear empleados faltantes en dim_empleado
   - Recargar fact_asistencia

   OPCIÓN B (Eliminar huérfanos):
   - Mantener JOIN con scd_es_actual = TRUE
   - Eliminar asistencias de empleados que no existen
   - Recargar solo las que tienen match

⚠️  RECOMENDACIÓN: Opción A (no perder datos)
""")

cur.close()
conn.close()

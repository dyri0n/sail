#!/usr/bin/env python3
"""
Script para verificar que no hay duplicados en dim_empleado (SCD Type 2).
Cada empleado debe tener solo 1 registro con scd_es_actual = TRUE.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Conexión al DWH usando DSN string
DSN = "host=localhost port=5432 dbname=rrhh_dwh user=dwh_admin password=dwh_secure_pass"


def check_duplicates():
    """Verifica duplicados de scd_es_actual = TRUE por empleado"""
    conn = psycopg2.connect(DSN)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Query para encontrar empleados con múltiples registros activos
    query = """
    SELECT 
        empleado_id_nk,
        COUNT(*) as registros_activos
    FROM dwh.dim_empleado
    WHERE scd_es_actual = TRUE
    GROUP BY empleado_id_nk
    HAVING COUNT(*) > 1
    ORDER BY COUNT(*) DESC;
    """

    cur.execute(query)
    duplicates = cur.fetchall()

    if duplicates:
        print("❌ ERROR: Se encontraron empleados con múltiples registros activos:")
        print("-" * 60)
        for row in duplicates[:20]:  # Mostrar hasta 20
            print(
                f"  Empleado {row['empleado_id_nk']}: {row['registros_activos']} registros activos"
            )
        if len(duplicates) > 20:
            print(f"  ... y {len(duplicates) - 20} más")
        print(f"\nTotal empleados con duplicados: {len(duplicates)}")
    else:
        print("✅ CORRECTO: No hay empleados con múltiples registros activos")

    cur.close()
    conn.close()
    return len(duplicates)


def check_stats():
    """Muestra estadísticas generales de dim_empleado"""
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Estadísticas generales
    stats_query = """
    SELECT 
        COUNT(*) as total_registros,
        COUNT(*) FILTER (WHERE scd_es_actual = TRUE) as registros_activos,
        COUNT(*) FILTER (WHERE scd_es_actual = FALSE) as registros_historicos,
        COUNT(DISTINCT empleado_id_nk) as empleados_unicos
    FROM dwh.dim_empleado;
    """

    cur.execute(stats_query)
    stats = cur.fetchone()

    print("\n📊 ESTADÍSTICAS dim_empleado:")
    print("-" * 60)
    print(f"  Total registros: {stats['total_registros']}")
    print(f"  Registros activos (scd_es_actual=TRUE): {stats['registros_activos']}")
    print(
        f"  Registros históricos (scd_es_actual=FALSE): {stats['registros_historicos']}"
    )
    print(f"  Empleados únicos: {stats['empleados_unicos']}")

    # Verificación: registros activos debe ser igual a empleados únicos
    if stats["registros_activos"] == stats["empleados_unicos"]:
        print(
            f"\n✅ VALIDACIÓN SCD2 CORRECTA: Cada empleado tiene exactamente 1 registro activo"
        )
    else:
        print(
            f"\n❌ VALIDACIÓN SCD2 FALLIDA: {stats['registros_activos']} activos vs {stats['empleados_unicos']} empleados"
        )

    cur.close()
    conn.close()


def show_sample():
    """Muestra una muestra de los datos"""
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    sample_query = """
    SELECT 
        empleado_sk,
        empleado_id_nk,
        nombre_completo,
        estado_laboral_activo,
        scd_es_actual,
        scd_fecha_inicio_vigencia,
        scd_fecha_fin_vigencia
    FROM dwh.dim_empleado
    ORDER BY empleado_id_nk, scd_fecha_inicio_vigencia
    LIMIT 10;
    """

    cur.execute(sample_query)
    rows = cur.fetchall()

    print("\n📋 MUESTRA DE DATOS (primeros 10 registros):")
    print("-" * 100)
    print(
        f"{'SK':>6} | {'ID_NK':>8} | {'Nombre':<25} | {'Activo':<6} | {'SCD_Actual':<10} | {'Inicio':<12} | {'Fin':<12}"
    )
    print("-" * 100)

    for row in rows:
        print(
            f"{row['empleado_sk']:>6} | {row['empleado_id_nk']:>8} | {str(row['nombre_completo'])[:25]:<25} | "
            f"{str(row['estado_laboral_activo']):<6} | {str(row['scd_es_actual']):<10} | "
            f"{str(row['scd_fecha_inicio_vigencia']):<12} | {str(row['scd_fecha_fin_vigencia']):<12}"
        )

    cur.close()
    conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICACIÓN DE dim_empleado - SCD Type 2")
    print("=" * 60)

    duplicates = check_duplicates()
    check_stats()
    show_sample()

    print("\n" + "=" * 60)
    if duplicates == 0:
        print("🎉 RESULTADO: La corrección fue exitosa, no hay duplicados")
    else:
        print("⚠️  RESULTADO: Aún existen duplicados que deben corregirse")
    print("=" * 60)

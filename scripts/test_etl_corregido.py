"""
Test del ETL corregido para fact_asistencia y fact_participacion.

Este script:
1. Limpia las tablas de hechos
2. Ejecuta los SQLs corregidos
3. Verifica que NO haya empleado_sk = -1
"""

import psycopg

# Conexión
DSN = "host=localhost port=6000 dbname=rrhh_prod user=postgres password=password_root"


def print_section(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}")


def execute_sql_file(cursor, filepath: str) -> bool:
    """Ejecuta un archivo SQL."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            sql = f.read()
        cursor.execute(sql)
        return True
    except Exception as e:
        print(f"  ❌ Error ejecutando {filepath}: {e}")
        return False


def main():
    print("\n" + "=" * 70)
    print("  TEST DEL ETL CORREGIDO")
    print("=" * 70)

    with psycopg.connect(DSN) as conn:
        conn.autocommit = True
        cursor = conn.cursor()

        # =====================================================================
        # PASO 1: Ver estado actual
        # =====================================================================
        print_section("1. Estado actual de las tablas")

        queries = {
            "fact_asistencia (total)": "SELECT COUNT(*) FROM dwh.fact_asistencia",
            "fact_asistencia (emp_sk=-1)": "SELECT COUNT(*) FROM dwh.fact_asistencia WHERE empleado_sk = -1",
            "fact_participacion (total)": "SELECT COUNT(*) FROM dwh.fact_participacion_capacitacion",
            "fact_participacion (emp_sk=-1)": "SELECT COUNT(*) FROM dwh.fact_participacion_capacitacion WHERE empleado_sk = -1",
            "dim_empleado (total)": "SELECT COUNT(*) FROM dwh.dim_empleado",
        }

        for name, query in queries.items():
            cursor.execute(query)
            result = cursor.fetchone()[0]
            print(f"  {name}: {result:,}")

        # =====================================================================
        # PASO 2: Limpiar tablas de hechos (reset para test)
        # =====================================================================
        print_section("2. Limpiando tablas para test")

        cursor.execute("TRUNCATE TABLE dwh.fact_asistencia CASCADE")
        print("  ✓ fact_asistencia truncada")

        cursor.execute("TRUNCATE TABLE dwh.fact_participacion_capacitacion CASCADE")
        print("  ✓ fact_participacion_capacitacion truncada")

        # =====================================================================
        # PASO 3: Ejecutar ETL corregido de asistencias
        # =====================================================================
        print_section("3. Ejecutando ETL corregido: fact_asistencia.sql")

        sql_path_asistencia = (
            r"d:\Code\SAIL\etl-node\airflow\dags\sql\fact-tables\fact_asistencia.sql"
        )

        if execute_sql_file(cursor, sql_path_asistencia):
            cursor.execute("SELECT COUNT(*) FROM dwh.fact_asistencia")
            total = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM dwh.fact_asistencia WHERE empleado_sk = -1"
            )
            con_menos_uno = cursor.fetchone()[0]

            print(f"  ✓ Registros insertados: {total:,}")
            print(
                f"  {'❌' if con_menos_uno > 0 else '✓'} Registros con empleado_sk=-1: {con_menos_uno:,}"
            )

            if con_menos_uno == 0 and total > 0:
                print(f"\n  🎉 ¡ÉXITO! Todas las asistencias tienen empleado válido")
            elif con_menos_uno > 0:
                pct = (con_menos_uno / total * 100) if total > 0 else 0
                print(f"\n  ⚠️  ADVERTENCIA: {pct:.1f}% aún tienen empleado_sk=-1")

        # =====================================================================
        # PASO 4: Ejecutar ETL corregido de participaciones
        # =====================================================================
        print_section("4. Ejecutando ETL corregido: fact_participacion.sql")

        sql_path_participacion = (
            r"d:\Code\SAIL\etl-node\airflow\dags\sql\fact-tables\fact_participacion.sql"
        )

        if execute_sql_file(cursor, sql_path_participacion):
            cursor.execute("SELECT COUNT(*) FROM dwh.fact_participacion_capacitacion")
            total = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM dwh.fact_participacion_capacitacion WHERE empleado_sk = -1"
            )
            con_menos_uno = cursor.fetchone()[0]

            print(f"  ✓ Registros insertados: {total:,}")
            print(
                f"  {'❌' if con_menos_uno > 0 else '✓'} Registros con empleado_sk=-1: {con_menos_uno:,}"
            )

            if con_menos_uno == 0 and total > 0:
                print(
                    f"\n  🎉 ¡ÉXITO! Todas las participaciones tienen empleado válido"
                )
            elif con_menos_uno > 0:
                pct = (con_menos_uno / total * 100) if total > 0 else 0
                print(f"\n  ⚠️  ADVERTENCIA: {pct:.1f}% aún tienen empleado_sk=-1")

        # =====================================================================
        # PASO 5: Verificar empleados nuevos en dim_empleado
        # =====================================================================
        print_section("5. Verificación de dim_empleado")

        cursor.execute("SELECT COUNT(*) FROM dwh.dim_empleado")
        total_emp = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(DISTINCT empleado_id_nk) 
            FROM dwh.dim_empleado 
            WHERE scd_fecha_inicio_vigencia = '2020-01-01'
        """)
        emp_auto_insertados = cursor.fetchone()[0]

        print(f"  Total empleados en dim_empleado: {total_emp:,}")
        print(
            f"  Empleados auto-insertados (fecha 2020-01-01): {emp_auto_insertados:,}"
        )

        # =====================================================================
        # PASO 6: Resumen final
        # =====================================================================
        print_section("6. RESUMEN FINAL")

        cursor.execute("SELECT COUNT(*) FROM stg.stg_asistencia_diaria")
        stg_asist = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dwh.fact_asistencia")
        dwh_asist = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM stg.stg_participacion_capacitaciones")
        stg_part = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM dwh.fact_participacion_capacitacion")
        dwh_part = cursor.fetchone()[0]

        print(f"\n  ASISTENCIAS:")
        print(f"    STG: {stg_asist:,} registros")
        print(f"    DWH: {dwh_asist:,} registros")
        print(
            f"    Ratio: {(dwh_asist / stg_asist * 100):.1f}%"
            if stg_asist > 0
            else "N/A"
        )

        print(f"\n  PARTICIPACIONES:")
        print(f"    STG: {stg_part:,} registros")
        print(f"    DWH: {dwh_part:,} registros")
        print(
            f"    Ratio: {(dwh_part / stg_part * 100):.1f}%" if stg_part > 0 else "N/A"
        )

        # Verificar que no hay -1
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM dwh.fact_asistencia WHERE empleado_sk = -1) as asist_invalidos,
                (SELECT COUNT(*) FROM dwh.fact_participacion_capacitacion WHERE empleado_sk = -1) as part_invalidos
        """)
        result = cursor.fetchone()

        print(f"\n  VALIDACIÓN empleado_sk != -1:")
        print(
            f"    fact_asistencia: {'✅ OK' if result[0] == 0 else '❌ ' + str(result[0]) + ' inválidos'}"
        )
        print(
            f"    fact_participacion: {'✅ OK' if result[1] == 0 else '❌ ' + str(result[1]) + ' inválidos'}"
        )

        if result[0] == 0 and result[1] == 0:
            print(
                f"\n  🎉 ¡CORRECCIÓN EXITOSA! Los ETLs ahora funcionan correctamente."
            )
        else:
            print(f"\n  ⚠️  Aún hay registros con empleado_sk=-1. Revisar los ETLs.")


if __name__ == "__main__":
    main()

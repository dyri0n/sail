"""Script para limpiar el DWH antes de ejecutar el DAG maestro."""

import psycopg

DSN = "host=localhost port=6000 dbname=rrhh_prod user=postgres password=password_root"

with psycopg.connect(DSN) as conn:
    conn.autocommit = True
    cur = conn.cursor()

    print("Limpiando tablas del DWH...")

    # Truncar tablas de hechos
    tables = [
        "dwh.fact_asistencia",
        "dwh.fact_participacion_capacitacion",
        "dwh.fact_realizacion_capacitacion",
        "dwh.fact_seleccion",
        "dwh.fact_rotacion",
        "dwh.fact_dotacion_snapshot",
    ]

    for t in tables:
        try:
            cur.execute(f"TRUNCATE TABLE {t} CASCADE")
            print(f"  ✓ {t}")
        except Exception as e:
            print(f"  ⚠ {t}: {e}")

    # Truncar dimensiones (excepto dim_tiempo)
    dims = [
        "dwh.dim_empleado",
        "dwh.dim_cargo",
        "dwh.dim_gerencia",
        "dwh.dim_centro_costo",
        "dwh.dim_empresa",
        "dwh.dim_modalidad_contrato",
        "dwh.dim_tipo_jornada",
        "dwh.dim_tipo_asistencia",
        "dwh.dim_medida_aplicada",
        "dwh.dim_curso",
        "dwh.dim_tipo_formacion",
    ]

    for d in dims:
        try:
            cur.execute(f"TRUNCATE TABLE {d} CASCADE")
            print(f"  ✓ {d}")
        except Exception as e:
            print(f"  ⚠ {d}: {e}")

    print("\n✅ Limpieza completada")

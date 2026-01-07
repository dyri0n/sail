"""Verificación post-ETL."""

import psycopg

DSN = "host=localhost port=6000 dbname=rrhh_prod user=postgres password=password_root"

with psycopg.connect(DSN) as conn:
    cur = conn.cursor()

    print("=" * 70)
    print("  VERIFICACIÓN POST-ETL")
    print("=" * 70)

    queries = [
        ("dim_empleado", "SELECT COUNT(*) FROM dwh.dim_empleado"),
        ("fact_asistencia (total)", "SELECT COUNT(*) FROM dwh.fact_asistencia"),
        (
            "fact_asistencia (emp=-1)",
            "SELECT COUNT(*) FROM dwh.fact_asistencia WHERE empleado_sk = -1",
        ),
        (
            "fact_participacion (total)",
            "SELECT COUNT(*) FROM dwh.fact_participacion_capacitacion",
        ),
        (
            "fact_participacion (emp=-1)",
            "SELECT COUNT(*) FROM dwh.fact_participacion_capacitacion WHERE empleado_sk = -1",
        ),
        ("fact_rotacion", "SELECT COUNT(*) FROM dwh.fact_rotacion"),
        ("fact_seleccion", "SELECT COUNT(*) FROM dwh.fact_seleccion"),
    ]

    for name, q in queries:
        cur.execute(q)
        val = cur.fetchone()[0]
        print(f"  {name}: {val:,}")

    print()

    cur.execute("SELECT COUNT(*) FROM stg.stg_asistencia_diaria")
    stg_asist = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dwh.fact_asistencia")
    dwh_asist = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM stg.stg_participacion_capacitaciones")
    stg_part = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM dwh.fact_participacion_capacitacion")
    dwh_part = cur.fetchone()[0]

    print("  RATIOS STG -> DWH:")
    print(
        f"    Asistencias: {stg_asist:,} -> {dwh_asist:,} ({dwh_asist * 100 / stg_asist:.1f}%)"
    )
    print(
        f"    Participaciones: {stg_part:,} -> {dwh_part:,} ({dwh_part * 100 / stg_part:.1f}%)"
    )

    cur.execute("SELECT COUNT(*) FROM dwh.fact_asistencia WHERE empleado_sk = -1")
    a_inv = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(*) FROM dwh.fact_participacion_capacitacion WHERE empleado_sk = -1"
    )
    p_inv = cur.fetchone()[0]

    print()
    if a_inv == 0 and p_inv == 0:
        print("  ✅ ÉXITO: No hay registros con empleado_sk = -1")
    else:
        print(
            f"  ❌ ERROR: Hay {a_inv} asistencias y {p_inv} participaciones con empleado_sk = -1"
        )

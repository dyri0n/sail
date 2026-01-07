"""Diagnóstico de fact_rotacion."""

import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=6000,
    database="rrhh_prod",
    user="postgres",
    password="password_root",
)
cur = conn.cursor()

# 1. Conteo total
cur.execute("SELECT COUNT(*) FROM dwh.fact_rotacion")
print(f"Total fact_rotacion: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM stg.stg_rotacion_empleados")
print(f"Total staging: {cur.fetchone()[0]}")

# 2. Verificar empleados duplicados en la fact table
cur.execute("""
    SELECT e.empleado_id_nk, f.fecha_inicio_vigencia_sk, COUNT(*) as cnt
    FROM dwh.fact_rotacion f
    JOIN dwh.dim_empleado e ON f.empleado_sk = e.empleado_sk
    GROUP BY e.empleado_id_nk, f.fecha_inicio_vigencia_sk
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC
    LIMIT 10
""")
print("\n=== Empleados duplicados en fact_rotacion ===")
dups = cur.fetchall()
if dups:
    for r in dups:
        print(f"  emp={r[0]}, fecha={r[1]}, repeticiones={r[2]}")
else:
    print("  No hay duplicados!")

# 3. Verificar dim_empleado duplicados
cur.execute("""
    SELECT empleado_id_nk, COUNT(*) as cnt
    FROM dwh.dim_empleado
    WHERE scd_es_actual = TRUE
    GROUP BY empleado_id_nk
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC
    LIMIT 10
""")
print("\n=== Empleados con múltiples scd_es_actual=TRUE ===")
dups = cur.fetchall()
if dups:
    for r in dups:
        print(f"  emp={r[0]}, versiones_activas={r[1]}")
else:
    print("  No hay duplicados!")

conn.close()

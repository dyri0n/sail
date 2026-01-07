import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=6000,
    database="rrhh_prod",
    user="postgres",
    password="password_root",
)
cur = conn.cursor()

# Verificar dim_medida_aplicada para BAJA
cur.execute(
    "SELECT medida_sk, tipo_movimiento, razon_detallada FROM dwh.dim_medida_aplicada WHERE UPPER(tipo_movimiento) = 'BAJA'"
)
print("=== Medidas BAJA en dim ===")
for r in cur.fetchall():
    print(f"  sk={r[0]}, tipo={r[1]}, razon={r[2]}")

# Verificar empleado 103872 en dim_empleado
cur.execute(
    "SELECT empleado_sk, empleado_id_nk, scd_es_actual FROM dwh.dim_empleado WHERE empleado_id_nk = '103872'"
)
print("\n=== Empleado 103872 en dim ===")
for r in cur.fetchall():
    print(f"  sk={r[0]}, id={r[1]}, actual={r[2]}")

# Verificar empleado 103849 en dim_empleado
cur.execute(
    "SELECT empleado_sk, empleado_id_nk, scd_es_actual FROM dwh.dim_empleado WHERE empleado_id_nk = '103849'"
)
print("\n=== Empleado 103849 en dim ===")
for r in cur.fetchall():
    print(f"  sk={r[0]}, id={r[1]}, actual={r[2]}")

# Verificar fact_rotacion para empleado 103872
cur.execute("""
    SELECT f.rotacion_sk, f.fecha_inicio_vigencia_sk, f.empleado_sk, f.medida_sk, m.tipo_movimiento, m.razon_detallada
    FROM dwh.fact_rotacion f
    JOIN dwh.dim_medida_aplicada m ON f.medida_sk = m.medida_sk
    JOIN dwh.dim_empleado e ON f.empleado_sk = e.empleado_sk
    WHERE e.empleado_id_nk = '103872'
    ORDER BY f.fecha_inicio_vigencia_sk
""")
print("\n=== Registros fact_rotacion para emp 103872 ===")
for r in cur.fetchall():
    print(
        f"  rotacion_sk={r[0]}, fecha={r[1]}, emp_sk={r[2]}, medida_sk={r[3]}, tipo={r[4]}, razon={r[5]}"
    )

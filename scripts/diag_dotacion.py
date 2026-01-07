"""
Diagnóstico para fact_dotacion_snapshot vacía
"""

import psycopg2

# Conexión al DWH
conn = psycopg2.connect(
    host="localhost",
    port=6000,
    database="rrhh_prod",
    user="dwh_admin",
    password="sail-rrhh-p4",
)

queries = [
    ("1. Conteo fact_rotacion", "SELECT COUNT(*) FROM dwh.fact_rotacion"),
    (
        "2. Conteo fact_dotacion_snapshot",
        "SELECT COUNT(*) FROM dwh.fact_dotacion_snapshot",
    ),
    (
        "3. Conteo dim_tiempo (fin de mes)",
        """
        SELECT COUNT(*) FROM dwh.dim_tiempo 
        WHERE EXTRACT(MONTH FROM fecha) != EXTRACT(MONTH FROM (fecha + INTERVAL '1 day'))
    """,
    ),
    ("4. Conteo dim_empleado", "SELECT COUNT(*) FROM dwh.dim_empleado"),
    (
        "5. Muestra fact_rotacion (5 filas)",
        """
        SELECT fecha_inicio_vigencia_sk, fecha_fin_vigencia_sk, empleado_sk, medida_sk
        FROM dwh.fact_rotacion 
        LIMIT 5
    """,
    ),
    (
        "6. Tipos de medida en dim_medida_aplicada",
        """
        SELECT medida_sk, tipo_movimiento, razon_detallada 
        FROM dwh.dim_medida_aplicada
    """,
    ),
    (
        "7. Fechas fin de mes en dim_tiempo en rango de fact_rotacion",
        """
        SELECT tiempo_sk, fecha 
        FROM dwh.dim_tiempo 
        WHERE EXTRACT(MONTH FROM fecha) != EXTRACT(MONTH FROM (fecha + INTERVAL '1 day'))
        AND tiempo_sk >= 20231121 AND tiempo_sk <= 99991231
        ORDER BY tiempo_sk
        LIMIT 20
    """,
    ),
    (
        "8. Rango de fechas en fact_rotacion",
        """
        SELECT 
            MIN(fecha_inicio_vigencia_sk) as min_inicio,
            MAX(fecha_inicio_vigencia_sk) as max_inicio,
            MIN(fecha_fin_vigencia_sk) as min_fin,
            MAX(fecha_fin_vigencia_sk) as max_fin
        FROM dwh.fact_rotacion
    """,
    ),
    (
        "9. Rango de fechas en dim_tiempo",
        """
        SELECT MIN(tiempo_sk), MAX(tiempo_sk), MIN(fecha), MAX(fecha) 
        FROM dwh.dim_tiempo
    """,
    ),
    (
        "10. Test JOIN fact_rotacion con dim_tiempo (fin de mes)",
        """
        SELECT COUNT(*) FROM dwh.fact_rotacion f
        JOIN dwh.dim_tiempo t 
            ON t.fecha >= TO_DATE(f.fecha_inicio_vigencia_sk::text, 'YYYYMMDD')
            AND t.fecha <= TO_DATE(f.fecha_fin_vigencia_sk::text, 'YYYYMMDD')
            AND EXTRACT(MONTH FROM t.fecha) != EXTRACT(MONTH FROM (t.fecha + INTERVAL '1 day'))
    """,
    ),
    (
        "11. Test JOIN completo para snapshot (sin filtro BAJA)",
        """
        SELECT COUNT(*) FROM dwh.fact_rotacion f
        JOIN dwh.dim_tiempo t 
            ON t.fecha >= TO_DATE(f.fecha_inicio_vigencia_sk::text, 'YYYYMMDD')
            AND t.fecha <= TO_DATE(f.fecha_fin_vigencia_sk::text, 'YYYYMMDD')
            AND EXTRACT(MONTH FROM t.fecha) != EXTRACT(MONTH FROM (t.fecha + INTERVAL '1 day'))
        JOIN dwh.dim_modalidad_contrato dmod ON f.modalidad_sk = dmod.modalidad_sk
        JOIN dwh.dim_medida_aplicada dma ON f.medida_sk = dma.medida_sk
    """,
    ),
    (
        "12. Empleados en fact_rotacion con sk válido",
        """
        SELECT COUNT(*) FROM dwh.fact_rotacion WHERE empleado_sk > 0
    """,
    ),
    (
        "13. Medidas sin tipo BAJA",
        """
        SELECT COUNT(*) FROM dwh.fact_rotacion f
        JOIN dwh.dim_medida_aplicada dma ON f.medida_sk = dma.medida_sk
        WHERE UPPER(dma.tipo_movimiento) NOT IN ('BAJA')
    """,
    ),
    (
        "14. Verificar staging rotacion",
        """
        SELECT COUNT(*) FROM stg.stg_rotacion_empleados
    """,
    ),
    (
        "15. Detalle fact_dotacion_snapshot (meses distintos)",
        """
        SELECT mes_cierre_sk, COUNT(*) as empleados
        FROM dwh.fact_dotacion_snapshot
        GROUP BY mes_cierre_sk
        ORDER BY mes_cierre_sk
    """,
    ),
    (
        "16. Meses afectados en staging",
        """
        SELECT DISTINCT DATE_TRUNC('month', desde3)::DATE as mes
        FROM stg.stg_rotacion_empleados
        WHERE desde3 IS NOT NULL
        ORDER BY mes
    """,
    ),
    (
        "17. TEST: Query del snapshot completo hasta mes actual (deberia dar)",
        """
        SELECT COUNT(DISTINCT (t.tiempo_sk, f.empleado_sk)) 
        FROM dwh.fact_rotacion f
        JOIN dwh.dim_tiempo t 
            ON t.fecha >= TO_DATE(f.fecha_inicio_vigencia_sk::text, 'YYYYMMDD')
            AND t.fecha <= LEAST(
                TO_DATE(f.fecha_fin_vigencia_sk::text, 'YYYYMMDD'),
                (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month - 1 day')::DATE
            )
            AND EXTRACT(MONTH FROM t.fecha) != EXTRACT(MONTH FROM (t.fecha + INTERVAL '1 day'))
        JOIN dwh.dim_modalidad_contrato dmod ON f.modalidad_sk = dmod.modalidad_sk
        JOIN dwh.dim_medida_aplicada dma ON f.medida_sk = dma.medida_sk
        WHERE f.empleado_sk > 0
            AND UPPER(dma.tipo_movimiento) NOT IN ('BAJA')
    """,
    ),
]

print("=" * 60)
print("DIAGNÓSTICO fact_dotacion_snapshot")
print("=" * 60)

cursor = conn.cursor()

for title, query in queries:
    print(f"\n{title}")
    print("-" * 50)
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        if cursor.description:
            cols = [desc[0] for desc in cursor.description]
            print(f"Columnas: {cols}")
        for row in results:
            print(row)
    except Exception as e:
        print(f"ERROR: {e}")

cursor.close()
conn.close()

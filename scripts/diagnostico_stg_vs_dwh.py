#!/usr/bin/env python3
"""
Diagnóstico Comprensivo: STG vs DWH
====================================
Compara datos entre staging (STG) y data warehouse (DWH) para validar:
1. CAPACITACIONES (Participación y Realización)
2. ASISTENCIAS

Objetivo: Verificar que los datos de STG se cargan y relacionan correctamente en DWH.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import sys

# Credenciales de conexión (desde dwh-node)
DSN = "host=localhost port=6000 dbname=rrhh_prod user=postgres password=password_root"


def print_section(title):
    """Imprime un separador de sección"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title):
    """Imprime un separador de subsección"""
    print(f"\n{'─' * 80}")
    print(f"  {title}")
    print(f"{'─' * 80}")


def execute_query(conn, query, description=""):
    """Ejecuta una query y retorna resultados"""
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        return results
    except Exception as e:
        print(f"❌ Error en '{description}': {e}")
        return None


def compare_counts(conn, stg_table, dwh_table, entity_name):
    """Compara conteo total entre STG y DWH"""
    print_subsection(f"📊 Conteo Total: {entity_name}")

    # STG count
    stg_query = f"SELECT COUNT(*) as count FROM stg.{stg_table}"
    stg_result = execute_query(conn, stg_query, f"Count {stg_table}")
    stg_count = stg_result[0]["count"] if stg_result else 0

    # DWH count
    dwh_query = f"SELECT COUNT(*) as count FROM dwh.{dwh_table}"
    dwh_result = execute_query(conn, dwh_query, f"Count {dwh_table}")
    dwh_count = dwh_result[0]["count"] if dwh_result else 0

    print(f"  STG ({stg_table}): {stg_count:,} registros")
    print(f"  DWH ({dwh_table}): {dwh_count:,} registros")

    if stg_count > 0:
        ratio = (dwh_count / stg_count) * 100
        print(f"  Ratio DWH/STG: {ratio:.2f}%")

        if ratio < 95:
            print(f"  ⚠️  ADVERTENCIA: Se están perdiendo datos en el ETL!")
        elif ratio > 105:
            print(f"  ⚠️  ADVERTENCIA: Se están duplicando datos en el ETL!")
        else:
            print(f"  ✅ OK: Ratio dentro del rango aceptable")

    return stg_count, dwh_count


def diagnose_capacitacion_realizacion(conn):
    """Diagnóstico de Realización de Capacitaciones"""
    print_section("1️⃣  REALIZACIÓN DE CAPACITACIONES")

    # Comparar conteos
    stg_count, dwh_count = compare_counts(
        conn,
        "stg_realizacion_capacitaciones",
        "fact_realizacion_capacitacion",
        "Realización de Capacitaciones",
    )

    # Verificar campos clave
    print_subsection("🔍 Validación de Campos Clave")

    # Campos en STG
    stg_query = """
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT titulo) as cursos_unicos,
        COUNT(DISTINCT fecha_inicio) as fechas_inicio_unicas,
        COUNT(DISTINCT mes) as meses_unicos,
        SUM(nro_asistentes) as total_asistentes,
        SUM(total_horas) as total_horas,
        SUM(coste) as total_coste,
        AVG(valoracion_formador) as avg_valoracion,
        AVG(indice_satisfaccion) as avg_satisfaccion,
        AVG(nps) as avg_nps
    FROM stg.stg_realizacion_capacitaciones
    """

    stg_stats = execute_query(conn, stg_query, "STG Realizacion Stats")

    if stg_stats:
        s = stg_stats[0]
        print(f"  STG:")
        print(f"    • Total registros: {s['total']:,}")
        print(f"    • Cursos únicos: {s['cursos_unicos']:,}")
        print(f"    • Fechas de inicio únicas: {s['fechas_inicio_unicas']:,}")
        print(f"    • Total asistentes: {s['total_asistentes']:,}")
        print(f"    • Total horas: {s['total_horas']:,}")
        print(
            f"    • Total coste: ${s['total_coste']:,.2f}"
            if s["total_coste"]
            else "    • Total coste: N/A"
        )
        print(
            f"    • Valoración formador promedio: {s['avg_valoracion']:.2f}"
            if s["avg_valoracion"]
            else "    • Valoración: N/A"
        )
        print(
            f"    • Satisfacción promedio: {s['avg_satisfaccion']:.2f}%"
            if s["avg_satisfaccion"]
            else "    • Satisfacción: N/A"
        )
        print(
            f"    • NPS promedio: {s['avg_nps']:.1f}"
            if s["avg_nps"]
            else "    • NPS: N/A"
        )

    # Campos en DWH
    dwh_query = """
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT curso_sk) as cursos_unicos,
        COUNT(DISTINCT fecha_inicio_sk) as fechas_inicio_unicas,
        SUM(total_asistentes) as total_asistentes,
        SUM(duracion_horas_total) as total_horas,
        SUM(costo_total_curso) as total_coste,
        AVG(valoracion_formador) as avg_valoracion,
        AVG(satisfaccion_promedio) as avg_satisfaccion,
        AVG(nps_score) as avg_nps
    FROM dwh.fact_realizacion_capacitacion
    """

    dwh_stats = execute_query(conn, dwh_query, "DWH Realizacion Stats")

    if dwh_stats:
        d = dwh_stats[0]
        print(f"\n  DWH:")
        print(f"    • Total registros: {d['total']:,}")
        print(f"    • Cursos únicos (curso_sk): {d['cursos_unicos']:,}")
        print(f"    • Fechas de inicio únicas: {d['fechas_inicio_unicas']:,}")
        print(f"    • Total asistentes: {d['total_asistentes']:,}")
        print(f"    • Total horas: {d['total_horas']:,}")
        print(
            f"    • Total coste: ${d['total_coste']:,.2f}"
            if d["total_coste"]
            else "    • Total coste: N/A"
        )
        print(
            f"    • Valoración formador promedio: {d['avg_valoracion']:.2f}"
            if d["avg_valoracion"]
            else "    • Valoración: N/A"
        )
        print(
            f"    • Satisfacción promedio: {d['avg_satisfaccion']:.2f}%"
            if d["avg_satisfaccion"]
            else "    • Satisfacción: N/A"
        )
        print(
            f"    • NPS promedio: {d['avg_nps']:.1f}"
            if d["avg_nps"]
            else "    • NPS: N/A"
        )

    # Comparar métricas
    if stg_stats and dwh_stats:
        print_subsection("📈 Comparación de Métricas")
        s = stg_stats[0]
        d = dwh_stats[0]

        metrics = [
            ("Total Asistentes", s["total_asistentes"], d["total_asistentes"]),
            ("Total Horas", s["total_horas"], d["total_horas"]),
            ("Total Coste", s["total_coste"], d["total_coste"]),
        ]

        for metric_name, stg_val, dwh_val in metrics:
            if stg_val is not None and dwh_val is not None:
                diff = dwh_val - stg_val
                pct = (diff / stg_val * 100) if stg_val != 0 else 0
                status = "✅" if abs(pct) < 5 else "⚠️"
                print(
                    f"  {status} {metric_name}: STG={stg_val:,.0f}, DWH={dwh_val:,.0f}, Diff={diff:+.0f} ({pct:+.1f}%)"
                )

    # Verificar integridad de claves foráneas
    print_subsection("🔗 Integridad de Claves Foráneas")

    # Verificar curso_sk
    check_fk_query = """
    SELECT 
        COUNT(*) as total_sin_curso,
        COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dwh.fact_realizacion_capacitacion) as porcentaje
    FROM dwh.fact_realizacion_capacitacion frc
    WHERE curso_sk IS NULL OR curso_sk NOT IN (SELECT curso_sk FROM dwh.dim_curso)
    """

    fk_result = execute_query(conn, check_fk_query, "FK Curso Check")
    if fk_result:
        total = fk_result[0]["total_sin_curso"]
        pct = fk_result[0]["porcentaje"]
        if total > 0:
            print(f"  ⚠️  Registros sin curso_sk válido: {total} ({pct:.2f}%)")
        else:
            print(f"  ✅ Todos los registros tienen curso_sk válido")

    # Verificar fecha_inicio_sk
    check_fecha_query = """
    SELECT 
        COUNT(*) as total_sin_fecha
    FROM dwh.fact_realizacion_capacitacion frc
    WHERE fecha_inicio_sk IS NULL OR fecha_inicio_sk NOT IN (SELECT tiempo_sk FROM dwh.dim_tiempo)
    """

    fecha_result = execute_query(conn, check_fecha_query, "FK Fecha Check")
    if fecha_result:
        total = fecha_result[0]["total_sin_fecha"]
        if total > 0:
            print(f"  ⚠️  Registros sin fecha_inicio_sk válida: {total}")
        else:
            print(f"  ✅ Todos los registros tienen fecha_inicio_sk válida")


def diagnose_capacitacion_participacion(conn):
    """Diagnóstico de Participación en Capacitaciones"""
    print_section("2️⃣  PARTICIPACIÓN EN CAPACITACIONES")

    # Comparar conteos
    stg_count, dwh_count = compare_counts(
        conn,
        "stg_participacion_capacitaciones",
        "fact_participacion_capacitacion",
        "Participación en Capacitaciones",
    )

    # Verificar campos clave
    print_subsection("🔍 Validación de Campos Clave")

    # Campos en STG
    stg_query = """
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT rut) as empleados_unicos_rut,
        COUNT(DISTINCT id_empleado) as empleados_unicos_id,
        COUNT(DISTINCT nombre_curso) as cursos_unicos,
        COUNT(DISTINCT mes) as meses_unicos,
        SUM(total_horas_formacion) as total_horas,
        AVG(total_horas_formacion) as avg_horas_por_participacion
    FROM stg.stg_participacion_capacitaciones
    """

    stg_stats = execute_query(conn, stg_query, "STG Participacion Stats")

    if stg_stats:
        s = stg_stats[0]
        print(f"  STG:")
        print(f"    • Total registros: {s['total']:,}")
        print(f"    • Empleados únicos (RUT): {s['empleados_unicos_rut']:,}")
        print(f"    • Empleados únicos (ID): {s['empleados_unicos_id']:,}")
        print(f"    • Cursos únicos: {s['cursos_unicos']:,}")
        print(f"    • Meses únicos: {s['meses_unicos']:,}")
        print(f"    • Total horas formación: {s['total_horas']:,}")
        print(
            f"    • Promedio horas/participación: {s['avg_horas_por_participacion']:.2f}"
            if s["avg_horas_por_participacion"]
            else "    • Promedio: N/A"
        )

    # Campos en DWH
    dwh_query = """
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT empleado_sk) as empleados_unicos,
        COUNT(DISTINCT curso_sk) as cursos_unicos,
        COUNT(DISTINCT mes_realizacion_sk) as meses_unicos,
        SUM(horas_capacitacion_recibidas) as total_horas,
        AVG(horas_capacitacion_recibidas) as avg_horas_por_participacion,
        SUM(asistencia_count) as total_asistencias
    FROM dwh.fact_participacion_capacitacion
    """

    dwh_stats = execute_query(conn, dwh_query, "DWH Participacion Stats")

    if dwh_stats:
        d = dwh_stats[0]
        print(f"\n  DWH:")
        print(f"    • Total registros: {d['total']:,}")
        print(f"    • Empleados únicos (empleado_sk): {d['empleados_unicos']:,}")
        print(f"    • Cursos únicos (curso_sk): {d['cursos_unicos']:,}")
        print(f"    • Meses únicos: {d['meses_unicos']:,}")
        print(f"    • Total horas formación: {d['total_horas']:,}")
        print(
            f"    • Promedio horas/participación: {d['avg_horas_por_participacion']:.2f}"
            if d["avg_horas_por_participacion"]
            else "    • Promedio: N/A"
        )
        print(f"    • Total asistencias: {d['total_asistencias']:,}")

    # Comparar métricas
    if stg_stats and dwh_stats:
        print_subsection("📈 Comparación de Métricas")
        s = stg_stats[0]
        d = dwh_stats[0]

        if s["total_horas"] is not None and d["total_horas"] is not None:
            diff = d["total_horas"] - s["total_horas"]
            pct = (diff / s["total_horas"] * 100) if s["total_horas"] != 0 else 0
            status = "✅" if abs(pct) < 5 else "⚠️"
            print(
                f"  {status} Total Horas: STG={s['total_horas']:,.0f}, DWH={d['total_horas']:,.0f}, Diff={diff:+.0f} ({pct:+.1f}%)"
            )

    # Verificar integridad de claves foráneas
    print_subsection("🔗 Integridad de Claves Foráneas")

    # Verificar empleado_sk
    check_emp_query = """
    SELECT 
        COUNT(*) as total_sin_empleado
    FROM dwh.fact_participacion_capacitacion fpc
    WHERE empleado_sk IS NULL OR empleado_sk NOT IN (SELECT empleado_sk FROM dwh.dim_empleado)
    """

    emp_result = execute_query(conn, check_emp_query, "FK Empleado Check")
    if emp_result:
        total = emp_result[0]["total_sin_empleado"]
        if total > 0:
            print(f"  ⚠️  Registros sin empleado_sk válido: {total}")
        else:
            print(f"  ✅ Todos los registros tienen empleado_sk válido")

    # Verificar curso_sk
    check_curso_query = """
    SELECT 
        COUNT(*) as total_sin_curso
    FROM dwh.fact_participacion_capacitacion fpc
    WHERE curso_sk IS NULL OR curso_sk NOT IN (SELECT curso_sk FROM dwh.dim_curso)
    """

    curso_result = execute_query(conn, check_curso_query, "FK Curso Check")
    if curso_result:
        total = curso_result[0]["total_sin_curso"]
        if total > 0:
            print(f"  ⚠️  Registros sin curso_sk válido: {total}")
        else:
            print(f"  ✅ Todos los registros tienen curso_sk válido")

    # Verificar relación con fact_realizacion
    print_subsection("🔗 Relación con Realización de Capacitaciones")

    link_query = """
    SELECT 
        COUNT(*) as total_participaciones,
        COUNT(realizacion_link_id) as con_link,
        COUNT(*) - COUNT(realizacion_link_id) as sin_link,
        (COUNT(realizacion_link_id) * 100.0 / COUNT(*)) as pct_con_link
    FROM dwh.fact_participacion_capacitacion
    """

    link_result = execute_query(conn, link_query, "Realizacion Link Check")
    if link_result:
        r = link_result[0]
        print(f"  Total participaciones: {r['total_participaciones']:,}")
        print(f"  Con link a realización: {r['con_link']:,} ({r['pct_con_link']:.1f}%)")
        print(f"  Sin link a realización: {r['sin_link']:,}")

        if r["pct_con_link"] < 80:
            print(
                f"  ⚠️  ADVERTENCIA: Más del 20% de participaciones no están vinculadas a realizaciones"
            )
        else:
            print(f"  ✅ OK: Mayoría de participaciones vinculadas")


def diagnose_asistencia(conn):
    """Diagnóstico de Asistencias"""
    print_section("3️⃣  ASISTENCIAS DIARIAS")

    # Comparar conteos
    stg_count, dwh_count = compare_counts(
        conn, "stg_asistencia_diaria", "fact_asistencia", "Asistencias Diarias"
    )

    # Verificar campos clave
    print_subsection("🔍 Validación de Campos Clave")

    # Campos en STG
    stg_query = """
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT id_empleado) as empleados_unicos,
        COUNT(DISTINCT asistio_en) as fechas_unicas,
        COUNT(DISTINCT tipo_permiso) as tipos_permiso,
        COUNT(DISTINCT tipo_turno) as tipos_turno,
        MIN(asistio_en) as fecha_min,
        MAX(asistio_en) as fecha_max,
        COUNT(CASE WHEN hora_ingreso IS NOT NULL THEN 1 END) as con_hora_ingreso,
        COUNT(CASE WHEN hora_salida IS NOT NULL THEN 1 END) as con_hora_salida,
        COUNT(CASE WHEN atraso IS NOT NULL AND atraso > '00:00:00'::interval THEN 1 END) as con_atraso
    FROM stg.stg_asistencia_diaria
    """

    stg_stats = execute_query(conn, stg_query, "STG Asistencia Stats")

    if stg_stats:
        s = stg_stats[0]
        print(f"  STG:")
        print(f"    • Total registros: {s['total']:,}")
        print(f"    • Empleados únicos: {s['empleados_unicos']:,}")
        print(f"    • Fechas únicas: {s['fechas_unicas']:,}")
        print(f"    • Tipos de permiso: {s['tipos_permiso']:,}")
        print(f"    • Tipos de turno: {s['tipos_turno']:,}")
        print(f"    • Rango de fechas: {s['fecha_min']} a {s['fecha_max']}")
        print(
            f"    • Con hora ingreso: {s['con_hora_ingreso']:,} ({s['con_hora_ingreso'] * 100.0 / s['total']:.1f}%)"
        )
        print(
            f"    • Con hora salida: {s['con_hora_salida']:,} ({s['con_hora_salida'] * 100.0 / s['total']:.1f}%)"
        )
        print(
            f"    • Con atraso: {s['con_atraso']:,} ({s['con_atraso'] * 100.0 / s['total']:.1f}%)"
        )

    # Campos en DWH
    dwh_query = """
    SELECT 
        COUNT(*) as total,
        COUNT(DISTINCT empleado_sk) as empleados_unicos,
        COUNT(DISTINCT fecha_sk) as fechas_unicas,
        COUNT(DISTINCT permiso_sk) as tipos_permiso,
        COUNT(DISTINCT turno_planificado_sk) as tipos_turno,
        COUNT(CASE WHEN hora_entrada_real IS NOT NULL THEN 1 END) as con_hora_entrada,
        COUNT(CASE WHEN hora_salida_real IS NOT NULL THEN 1 END) as con_hora_salida,
        COUNT(CASE WHEN minutos_atraso > 0 THEN 1 END) as con_atraso,
        SUM(CASE WHEN es_atraso = 1 THEN 1 ELSE 0 END) as es_atraso_count,
        SUM(CASE WHEN es_ausencia = 1 THEN 1 ELSE 0 END) as es_ausencia_count,
        AVG(horas_trabajadas) as avg_horas_trabajadas,
        SUM(horas_trabajadas) as total_horas_trabajadas
    FROM dwh.fact_asistencia
    """

    dwh_stats = execute_query(conn, dwh_query, "DWH Asistencia Stats")

    if dwh_stats:
        d = dwh_stats[0]
        print(f"\n  DWH:")
        print(f"    • Total registros: {d['total']:,}")
        print(f"    • Empleados únicos (empleado_sk): {d['empleados_unicos']:,}")
        print(f"    • Fechas únicas (fecha_sk): {d['fechas_unicas']:,}")
        print(f"    • Tipos de permiso (permiso_sk): {d['tipos_permiso']:,}")
        print(f"    • Tipos de turno (turno_sk): {d['tipos_turno']:,}")
        print(
            f"    • Con hora entrada: {d['con_hora_entrada']:,} ({d['con_hora_entrada'] * 100.0 / d['total']:.1f}%)"
        )
        print(
            f"    • Con hora salida: {d['con_hora_salida']:,} ({d['con_hora_salida'] * 100.0 / d['total']:.1f}%)"
        )
        print(
            f"    • Con minutos atraso > 0: {d['con_atraso']:,} ({d['con_atraso'] * 100.0 / d['total']:.1f}%)"
        )
        print(f"    • Marcados como atraso (es_atraso=1): {d['es_atraso_count']:,}")
        print(
            f"    • Marcados como ausencia (es_ausencia=1): {d['es_ausencia_count']:,}"
        )
        print(
            f"    • Promedio horas trabajadas: {d['avg_horas_trabajadas']:.2f}"
            if d["avg_horas_trabajadas"]
            else "    • Promedio: N/A"
        )
        print(
            f"    • Total horas trabajadas: {d['total_horas_trabajadas']:,.2f}"
            if d["total_horas_trabajadas"]
            else "    • Total: N/A"
        )

    # Verificar integridad de claves foráneas
    print_subsection("🔗 Integridad de Claves Foráneas")

    # Verificar empleado_sk
    check_emp_query = """
    SELECT 
        COUNT(*) as total_sin_empleado
    FROM dwh.fact_asistencia fa
    WHERE empleado_sk IS NULL OR empleado_sk NOT IN (SELECT empleado_sk FROM dwh.dim_empleado)
    """

    emp_result = execute_query(conn, check_emp_query, "FK Empleado Check")
    if emp_result:
        total = emp_result[0]["total_sin_empleado"]
        if total > 0:
            print(f"  ⚠️  Registros sin empleado_sk válido: {total}")
        else:
            print(f"  ✅ Todos los registros tienen empleado_sk válido")

    # Verificar fecha_sk
    check_fecha_query = """
    SELECT 
        COUNT(*) as total_sin_fecha
    FROM dwh.fact_asistencia fa
    WHERE fecha_sk IS NULL OR fecha_sk NOT IN (SELECT tiempo_sk FROM dwh.dim_tiempo)
    """

    fecha_result = execute_query(conn, check_fecha_query, "FK Fecha Check")
    if fecha_result:
        total = fecha_result[0]["total_sin_fecha"]
        if total > 0:
            print(f"  ⚠️  Registros sin fecha_sk válida: {total}")
        else:
            print(f"  ✅ Todos los registros tienen fecha_sk válida")

    # Analizar distribución de atrasos
    print_subsection("📊 Análisis de Atrasos")

    atraso_query = """
    SELECT 
        CASE 
            WHEN minutos_atraso = 0 THEN 'Sin atraso'
            WHEN minutos_atraso <= 5 THEN '1-5 min'
            WHEN minutos_atraso <= 15 THEN '6-15 min'
            WHEN minutos_atraso <= 30 THEN '16-30 min'
            WHEN minutos_atraso <= 60 THEN '31-60 min'
            ELSE 'Más de 60 min'
        END as rango_atraso,
        COUNT(*) as cantidad,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM dwh.fact_asistencia), 2) as porcentaje
    FROM dwh.fact_asistencia
    GROUP BY 
        CASE 
            WHEN minutos_atraso = 0 THEN 'Sin atraso'
            WHEN minutos_atraso <= 5 THEN '1-5 min'
            WHEN minutos_atraso <= 15 THEN '6-15 min'
            WHEN minutos_atraso <= 30 THEN '16-30 min'
            WHEN minutos_atraso <= 60 THEN '31-60 min'
            ELSE 'Más de 60 min'
        END
    ORDER BY 
        CASE 
            WHEN minutos_atraso = 0 THEN 1
            WHEN minutos_atraso <= 5 THEN 2
            WHEN minutos_atraso <= 15 THEN 3
            WHEN minutos_atraso <= 30 THEN 4
            WHEN minutos_atraso <= 60 THEN 5
            ELSE 6
        END
    """

    atraso_result = execute_query(conn, atraso_query, "Atraso Distribution")
    if atraso_result:
        print(f"  Distribución de atrasos:")
        for row in atraso_result:
            print(
                f"    {row['rango_atraso']:15s}: {row['cantidad']:6,} ({row['porcentaje']:5.2f}%)"
            )


def diagnose_data_quality(conn):
    """Diagnóstico de calidad de datos general"""
    print_section("4️⃣  CALIDAD DE DATOS GENERAL")

    # Verificar duplicados en dim_empleado
    print_subsection("👥 Integridad de dim_empleado")

    dup_query = """
    SELECT 
        empleado_id_nk,
        COUNT(*) as registros_activos
    FROM dwh.dim_empleado
    WHERE scd_es_actual = TRUE
    GROUP BY empleado_id_nk
    HAVING COUNT(*) > 1
    ORDER BY COUNT(*) DESC
    LIMIT 10
    """

    dup_result = execute_query(conn, dup_query, "Empleado Duplicates")
    if dup_result and len(dup_result) > 0:
        print(
            f"  ⚠️  Se encontraron {len(dup_result)} empleados con múltiples registros activos:"
        )
        for row in dup_result[:10]:
            print(
                f"    Empleado {row['empleado_id_nk']}: {row['registros_activos']} registros activos"
            )
    else:
        print(
            f"  ✅ No hay empleados con múltiples registros activos (SCD Type 2 correcto)"
        )

    # Verificar mapeo de empleados STG -> DWH
    print_subsection("🗺️  Mapeo de Empleados STG -> DWH")

    # Empleados en STG de participación que no están en DWH
    missing_emp_query = """
    SELECT COUNT(DISTINCT spc.id_empleado) as empleados_sin_match
    FROM stg.stg_participacion_capacitaciones spc
    WHERE spc.id_empleado IS NOT NULL
    AND NOT EXISTS (
        SELECT 1 FROM dwh.dim_empleado de 
        WHERE de.empleado_id_nk = spc.id_empleado::text
    )
    """

    missing_result = execute_query(conn, missing_emp_query, "Missing Employees")
    if missing_result:
        total = missing_result[0]["empleados_sin_match"]
        if total > 0:
            print(
                f"  ⚠️  Empleados en STG participación sin match en dim_empleado: {total}"
            )
        else:
            print(f"  ✅ Todos los empleados de STG están en dim_empleado")

    # Verificar dim_curso
    print_subsection("📚 Integridad de dim_curso")

    curso_query = """
    SELECT 
        COUNT(*) as total_cursos,
        COUNT(DISTINCT nombre_curso) as cursos_unicos
    FROM dwh.dim_curso
    """

    curso_result = execute_query(conn, curso_query, "Cursos Stats")
    if curso_result:
        print(f"  Total cursos en dim_curso: {curso_result[0]['total_cursos']:,}")
        print(f"  Cursos únicos por nombre: {curso_result[0]['cursos_unicos']:,}")

    # Cursos en STG que no están en DWH
    missing_curso_query = """
    SELECT COUNT(DISTINCT titulo) as cursos_sin_match
    FROM stg.stg_realizacion_capacitaciones
    WHERE NOT EXISTS (
        SELECT 1 FROM dwh.dim_curso dc 
        WHERE LOWER(TRIM(dc.nombre_curso)) = LOWER(TRIM(stg_realizacion_capacitaciones.titulo))
    )
    """

    missing_curso_result = execute_query(conn, missing_curso_query, "Missing Courses")
    if missing_curso_result:
        total = missing_curso_result[0]["cursos_sin_match"]
        if total > 0:
            print(f"  ⚠️  Cursos en STG realización sin match en dim_curso: {total}")
        else:
            print(f"  ✅ Todos los cursos de STG están en dim_curso")


def generate_summary(conn):
    """Genera un resumen ejecutivo"""
    print_section("📋 RESUMEN EJECUTIVO")

    # Obtener conteos generales
    queries = {
        "STG Realización": "SELECT COUNT(*) as cnt FROM stg.stg_realizacion_capacitaciones",
        "STG Participación": "SELECT COUNT(*) as cnt FROM stg.stg_participacion_capacitaciones",
        "STG Asistencia": "SELECT COUNT(*) as cnt FROM stg.stg_asistencia_diaria",
        "DWH Realización": "SELECT COUNT(*) as cnt FROM dwh.fact_realizacion_capacitacion",
        "DWH Participación": "SELECT COUNT(*) as cnt FROM dwh.fact_participacion_capacitacion",
        "DWH Asistencia": "SELECT COUNT(*) as cnt FROM dwh.fact_asistencia",
        "DWH Empleados Activos": "SELECT COUNT(*) as cnt FROM dwh.dim_empleado WHERE scd_es_actual = TRUE",
        "DWH Cursos": "SELECT COUNT(*) as cnt FROM dwh.dim_curso",
    }

    print(f"\n  Conteos Totales:")
    for name, query in queries.items():
        result = execute_query(conn, query, name)
        if result:
            print(f"    {name:25s}: {result[0]['cnt']:>10,}")

    print(f"\n  Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Base de datos: rrhh_prod (puerto 6000)")


def main():
    """Función principal"""
    print("\n" + "=" * 80)
    print("  DIAGNÓSTICO COMPRENSIVO: STG vs DWH")
    print("  Sistema SAIL - Análisis de Integridad de Datos")
    print("=" * 80)

    try:
        # Conectar a la base de datos
        print("\n🔌 Conectando a la base de datos...")
        conn = psycopg2.connect(DSN)
        print("✅ Conexión establecida")

        # Ejecutar diagnósticos
        diagnose_capacitacion_realizacion(conn)
        diagnose_capacitacion_participacion(conn)
        diagnose_asistencia(conn)
        diagnose_data_quality(conn)
        generate_summary(conn)

        # Cerrar conexión
        conn.close()
        print("\n✅ Diagnóstico completado exitosamente")

    except psycopg2.Error as e:
        print(f"\n❌ Error de base de datos: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

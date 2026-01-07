#!/usr/bin/env python3
"""
Resumen Visual del Diagnóstico
===============================
Muestra un resumen rápido y visual del estado del DWH.
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DSN = "host=localhost port=6000 dbname=rrhh_prod user=postgres password=password_root"


def print_header():
    print("\n" + "═" * 90)
    print("  🏥 DIAGNÓSTICO RÁPIDO - SISTEMA SAIL")
    print("  📊 Estado de Integridad de Datos: STG vs DWH")
    print("═" * 90)


def print_box(title, content, status="info"):
    """Imprime un cuadro con información"""
    colors = {"ok": "✅", "warning": "⚠️", "error": "❌", "info": "ℹ️"}
    icon = colors.get(status, "•")

    print(f"\n{icon} {title}")
    print("─" * 90)
    for line in content:
        print(f"  {line}")


def get_summary_stats(conn):
    """Obtiene estadísticas resumidas"""
    cur = conn.cursor(cursor_factory=RealDictCursor)

    stats = {}

    # Empleados
    queries = {
        "emp_stg_rotacion": "SELECT COUNT(DISTINCT id_empleado) as count FROM stg.stg_rotacion_empleados",
        "emp_stg_participacion": "SELECT COUNT(DISTINCT id_empleado) as count FROM stg.stg_participacion_capacitaciones WHERE id_empleado IS NOT NULL",
        "emp_stg_asistencia": "SELECT COUNT(DISTINCT id_empleado) as count FROM stg.stg_asistencia_diaria",
        "emp_dwh": "SELECT COUNT(DISTINCT empleado_id_nk) as count FROM dwh.dim_empleado",
        # Participaciones
        "part_stg": "SELECT COUNT(*) as count FROM stg.stg_participacion_capacitaciones",
        "part_dwh": "SELECT COUNT(*) as count FROM dwh.fact_participacion_capacitacion",
        # Asistencias
        "asist_stg": "SELECT COUNT(*) as count FROM stg.stg_asistencia_diaria",
        "asist_dwh": "SELECT COUNT(*) as count FROM dwh.fact_asistencia",
        "asist_dwh_empleados": "SELECT COUNT(DISTINCT empleado_sk) as count FROM dwh.fact_asistencia",
        # Realizaciones
        "real_stg": "SELECT COUNT(*) as count FROM stg.stg_realizacion_capacitaciones",
        "real_dwh": "SELECT COUNT(*) as count FROM dwh.fact_realizacion_capacitacion",
    }

    for key, query in queries.items():
        cur.execute(query)
        stats[key] = cur.fetchone()["count"]

    cur.close()
    return stats


def main():
    print_header()

    try:
        conn = psycopg2.connect(DSN)
        stats = get_summary_stats(conn)

        # Calcular métricas
        total_emp_stg = max(
            stats["emp_stg_rotacion"],
            stats["emp_stg_participacion"],
            stats["emp_stg_asistencia"],
        )
        emp_faltantes = total_emp_stg - stats["emp_dwh"]

        part_perdidas = stats["part_stg"] - stats["part_dwh"]
        part_pct = (
            (part_perdidas / stats["part_stg"] * 100) if stats["part_stg"] > 0 else 0
        )

        asist_ratio = (
            (stats["asist_dwh"] / stats["asist_stg"] * 100)
            if stats["asist_stg"] > 0
            else 0
        )

        # 1. Problema Principal
        if emp_faltantes > 0:
            status = "error"
            content = [
                f"dim_empleado tiene solo {stats['emp_dwh']} empleados",
                f"STG tiene al menos {total_emp_stg} empleados únicos (entre todas las tablas)",
                f"",
                f"🔴 FALTANTES: {emp_faltantes} empleados ({emp_faltantes * 100 / total_emp_stg:.1f}%)",
                f"",
                f"Desglose por tabla STG:",
                f"  • Rotación:      {stats['emp_stg_rotacion']} empleados",
                f"  • Participación: {stats['emp_stg_participacion']} empleados",
                f"  • Asistencia:    {stats['emp_stg_asistencia']} empleados",
            ]
        else:
            status = "ok"
            content = [f"dim_empleado completo con {stats['emp_dwh']} empleados"]

        print_box("DIMENSIÓN EMPLEADOS", content, status)

        # 2. Participaciones
        if part_pct > 10:
            status = "error"
        elif part_pct > 5:
            status = "warning"
        else:
            status = "ok"

        content = [
            f"STG: {stats['part_stg']:,} participaciones",
            f"DWH: {stats['part_dwh']:,} participaciones",
            f"",
            f"Pérdida: {part_perdidas:,} registros ({part_pct:.1f}%)",
        ]

        if part_pct > 10:
            content.append(f"")
            content.append(f"🔴 CRÍTICO: Más del 10% de datos perdidos")

        print_box("PARTICIPACIÓN EN CAPACITACIONES", content, status)

        # 3. Asistencias
        if stats["asist_dwh_empleados"] <= 1:
            status = "error"
            content = [
                f"STG: {stats['asist_stg']:,} asistencias de {stats['emp_stg_asistencia']} empleados",
                f"DWH: {stats['asist_dwh']:,} asistencias",
                f"",
                f"🔴 ERROR CRÍTICO:",
                f"  Todos los registros tienen empleado_sk = -1",
                f"  Empleados únicos en DWH: {stats['asist_dwh_empleados']} (debería ser ~{stats['emp_stg_asistencia']})",
                f"",
                f"🚨 ASISTENCIAS COMPLETAMENTE INVÁLIDAS",
            ]
        elif asist_ratio < 95:
            status = "warning"
            content = [
                f"STG: {stats['asist_stg']:,} asistencias",
                f"DWH: {stats['asist_dwh']:,} asistencias",
                f"Ratio: {asist_ratio:.1f}%",
            ]
        else:
            status = "ok"
            content = [
                f"STG: {stats['asist_stg']:,} asistencias",
                f"DWH: {stats['asist_dwh']:,} asistencias",
                f"Ratio: {asist_ratio:.1f}% ✓",
            ]

        print_box("ASISTENCIAS DIARIAS", content, status)

        # 4. Realizaciones
        real_diff = stats["real_dwh"] - stats["real_stg"]
        real_pct = (
            abs(real_diff) / stats["real_stg"] * 100 if stats["real_stg"] > 0 else 0
        )

        if real_pct > 10:
            status = "warning"
        else:
            status = "ok"

        content = [
            f"STG: {stats['real_stg']} realizaciones",
            f"DWH: {stats['real_dwh']} realizaciones",
            f"Diferencia: {real_diff:+d} ({real_pct:.1f}%)",
        ]

        if real_diff > 0:
            content.append(f"⚠️ Posible duplicación de {real_diff} registros")

        print_box("REALIZACIÓN DE CAPACITACIONES", content, status)

        # 5. Resumen y recomendaciones
        print("\n" + "═" * 90)
        print("  🎯 RESUMEN Y RECOMENDACIONES")
        print("═" * 90)

        issues = []
        if emp_faltantes > 0:
            issues.append(
                f"🔴 URGENTE: Cargar {emp_faltantes} empleados faltantes en dim_empleado"
            )

        if part_pct > 10:
            issues.append(
                f"🔴 URGENTE: Corregir pérdida de {part_perdidas} participaciones ({part_pct:.1f}%)"
            )

        if stats["asist_dwh_empleados"] <= 1:
            issues.append(
                f"🔴 URGENTE: Corregir empleado_sk en {stats['asist_dwh']:,} asistencias"
            )

        if real_diff > 5:
            issues.append(
                f"⚠️  Revisar duplicación en realizaciones (+{real_diff} registros)"
            )

        if issues:
            print("\n  PROBLEMAS DETECTADOS:")
            for i, issue in enumerate(issues, 1):
                print(f"\n  {i}. {issue}")

            print("\n\n  PLAN DE ACCIÓN:")
            print("\n  1️⃣  Ejecutar: uv run python analisis_dim_empleado.py")
            print("      → Identifica empleados faltantes y causa raíz")
            print("\n  2️⃣  Cargar empleados faltantes en dim_empleado")
            print("      → Resolver problema principal")
            print("\n  3️⃣  Recargar facts afectadas:")
            print("      → TRUNCATE fact_asistencia; re-ejecutar ETL")
            print("      → TRUNCATE fact_participacion_capacitacion; re-ejecutar ETL")
            print("\n  4️⃣  Validar: uv run python diagnostico_stg_vs_dwh.py")
            print("      → Verificar que ratio DWH/STG > 95%")
        else:
            print("\n  ✅ No se detectaron problemas críticos")
            print("  💡 El DWH está en buen estado")

        print("\n\n  📊 REPORTES DISPONIBLES:")
        print("     • scripts/RESUMEN_EJECUTIVO.md")
        print("     • scripts/DIAGNOSTICO_STG_DWH_2026-01-07.md")

        print("\n" + "═" * 90 + "\n")

        conn.close()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

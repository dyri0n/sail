#!/usr/bin/env python3
"""
DEV TOOLS - Herramientas de desarrollo para SAIL
================================================
Script interactivo para:
  1. Rebuild del DWH (docker-compose)
  2. Trigger del DAG maestro en Airflow
  3. Mini SQL Engine para consultas rápidas

Uso:
  python scripts/dev-tools.py

  O directamente:
  python scripts/dev-tools.py rebuild
  python scripts/dev-tools.py trigger
  python scripts/dev-tools.py sql
"""

import subprocess
import sys
import os
from pathlib import Path

# Agregar el path raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
os.chdir(PROJECT_ROOT)

# =============================================================================
# CONFIGURACIÓN DE CONEXIÓN (desde dwh-node/docker-compose.yaml)
# =============================================================================
DB_CONFIG = {
    "host": "localhost",
    "port": 6000,  # Puerto expuesto del contenedor
    "database": "rrhh_prod",
    "user": "postgres",
    "password": "password_root",
}

AIRFLOW_CONFIG = {
    "base_url": "http://localhost:8080",
    "username": "airflow",
    "password": "airflow",
}

DAG_MAESTRO_ID = "99_maestro_poblado_completo_dwh"


# =============================================================================
# UTILIDADES
# =============================================================================
def print_header(title: str):
    """Imprime un encabezado formateado."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)


def print_menu():
    """Muestra el menú principal."""
    print_header("SAIL DEV TOOLS")
    print("""
  [1] Rebuild DWH (docker-compose down + up)
  [2] Trigger DAG Maestro (Airflow)
  [3] SQL Console (consultas interactivas)
  [4] Quick Stats (resumen de tablas)
  [0] Salir
""")


# =============================================================================
# 1. REBUILD DWH
# =============================================================================
def rebuild_dwh():
    """Reconstruye el DWH usando el script existente."""
    print_header("REBUILD DWH")

    print("Opciones:")
    print("  [1] Rebuild completo (DWH + ETL)")
    print("  [2] Solo DWH Node")
    print("  [3] Solo ETL Node (Airflow)")
    print("  [0] Cancelar")

    option = input("\nOpción: ").strip()

    if option == "0":
        print("Cancelado.")
        return

    # Ejecutar el script PowerShell con la opción seleccionada
    script_path = PROJECT_ROOT / "scripts" / "rebuild-all.ps1"

    try:
        # Pasar la opción automáticamente
        process = subprocess.Popen(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script_path)],
            stdin=subprocess.PIPE,
            text=True,
        )
        # Enviar la opción y confirmación
        process.communicate(input=f"{option}\nSI\n")
        print("\n✓ Rebuild completado.")
    except Exception as e:
        print(f"\n✗ Error: {e}")


# =============================================================================
# 2. TRIGGER DAG
# =============================================================================
def trigger_dag():
    """Dispara el DAG maestro en Airflow."""
    print_header("TRIGGER DAG MAESTRO")

    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except ImportError:
        print("Instalando requests...")
        subprocess.run([sys.executable, "-m", "pip", "install", "requests", "-q"])
        import requests
        from requests.auth import HTTPBasicAuth

    url = f"{AIRFLOW_CONFIG['base_url']}/api/v1/dags/{DAG_MAESTRO_ID}/dagRuns"
    auth = HTTPBasicAuth(AIRFLOW_CONFIG["username"], AIRFLOW_CONFIG["password"])

    print(f"Disparando DAG: {DAG_MAESTRO_ID}")
    print(f"URL: {url}")

    try:
        response = requests.post(
            url,
            json={"conf": {}},
            auth=auth,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        if response.status_code in [200, 201]:
            data = response.json()
            print(f"\n✓ DAG disparado exitosamente!")
            print(f"  Run ID: {data.get('dag_run_id', 'N/A')}")
            print(f"  Estado: {data.get('state', 'N/A')}")
            print(
                f"\nMonitorear en: {AIRFLOW_CONFIG['base_url']}/dags/{DAG_MAESTRO_ID}/grid"
            )
        else:
            print(f"\n✗ Error {response.status_code}: {response.text}")

    except requests.exceptions.ConnectionError:
        print("\n✗ No se puede conectar a Airflow. ¿Está corriendo?")
        print(f"  Verificar: {AIRFLOW_CONFIG['base_url']}")
    except Exception as e:
        print(f"\n✗ Error: {e}")


# =============================================================================
# 3. SQL CONSOLE
# =============================================================================
def sql_console():
    """Consola SQL interactiva."""
    print_header("SQL CONSOLE")

    try:
        import psycopg2
        from psycopg2 import sql as psql
    except ImportError:
        print("Instalando psycopg2-binary...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"]
        )
        import psycopg2

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cursor = conn.cursor()
        print(
            f"✓ Conectado a {DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}"
        )
        print("\nComandos especiales:")
        print("  \\dt [schema]  - Listar tablas")
        print("  \\d tabla      - Describir tabla")
        print("  \\q            - Salir")
        print("  help          - Consultas útiles")
        print("\n" + "-" * 60)

    except Exception as e:
        print(f"\n✗ Error de conexión: {e}")
        print("  ¿Está corriendo el contenedor DWH?")
        return

    # Consultas útiles predefinidas
    useful_queries = {
        "1": (
            "Conteo fact_rotacion",
            "SELECT COUNT(*) AS total FROM dwh.fact_rotacion;",
        ),
        "2": (
            "Conteo staging",
            "SELECT COUNT(*) AS total FROM stg.stg_rotacion_empleados;",
        ),
        "3": ("Vista flujo rotación", "SELECT * FROM dwh.vw_flujo_rotacion LIMIT 20;"),
        "4": (
            "Empleados sin SK",
            "SELECT COUNT(*) FROM dwh.fact_rotacion WHERE empleado_sk = -1;",
        ),
        "5": (
            "Headcount por tipo",
            """
            SELECT 
                CASE variacion_headcount 
                    WHEN 1 THEN 'Alta (+1)'
                    WHEN -1 THEN 'Baja (-1)'
                    ELSE 'Sin cambio (0)'
                END AS tipo,
                COUNT(*) AS cantidad
            FROM dwh.fact_rotacion
            GROUP BY variacion_headcount
            ORDER BY variacion_headcount DESC;
        """,
        ),
    }

    while True:
        try:
            query = input("\nsql> ").strip()

            if not query:
                continue

            # Comandos especiales
            if query.lower() in ["\\q", "exit", "quit"]:
                print("Bye!")
                break

            if query.lower() == "help":
                print("\nConsultas útiles:")
                for key, (desc, _) in useful_queries.items():
                    print(f"  [{key}] {desc}")
                print("\nEscribe el número para ejecutar.")
                continue

            if query in useful_queries:
                desc, query = useful_queries[query]
                print(f">> {desc}")

            if query.lower().startswith("\\dt"):
                parts = query.split()
                schema = parts[1] if len(parts) > 1 else "dwh"
                query = f"""
                    SELECT table_name, pg_size_pretty(pg_total_relation_size(quote_ident(table_schema)||'.'||quote_ident(table_name))) as size
                    FROM information_schema.tables 
                    WHERE table_schema = '{schema}'
                    ORDER BY table_name;
                """

            if query.lower().startswith("\\d "):
                table = query.split()[1]
                schema = "dwh" if "." not in table else table.split(".")[0]
                table_name = table if "." not in table else table.split(".")[1]
                query = f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_schema = '{schema}' AND table_name = '{table_name}'
                    ORDER BY ordinal_position;
                """

            # Ejecutar query
            cursor.execute(query)

            if cursor.description:
                # SELECT - mostrar resultados
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                # Calcular anchos de columna
                widths = [len(str(col)) for col in columns]
                for row in rows:
                    for i, val in enumerate(row):
                        widths[i] = max(
                            widths[i], len(str(val) if val is not None else "NULL")
                        )

                # Imprimir header
                header = " | ".join(
                    str(col).ljust(widths[i]) for i, col in enumerate(columns)
                )
                print(header)
                print("-" * len(header))

                # Imprimir filas
                for row in rows:
                    print(
                        " | ".join(
                            str(val if val is not None else "NULL").ljust(widths[i])
                            for i, val in enumerate(row)
                        )
                    )

                print(f"\n({len(rows)} filas)")
            else:
                print(f"✓ Query ejecutado.")

        except KeyboardInterrupt:
            print("\n\nInterrumpido. Escribe \\q para salir.")
        except Exception as e:
            print(f"✗ Error: {e}")

    cursor.close()
    conn.close()


# =============================================================================
# 4. QUICK STATS
# =============================================================================
def quick_stats():
    """Muestra estadísticas rápidas de las tablas."""
    print_header("QUICK STATS")

    try:
        import psycopg2
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "psycopg2-binary", "-q"]
        )
        import psycopg2

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Stats de staging
        print("\n📦 STAGING (stg):")
        cursor.execute("""
            SELECT 'stg_rotacion_empleados' as tabla, COUNT(*) as filas FROM stg.stg_rotacion_empleados
            UNION ALL
            SELECT 'stg_asistencia_diaria', COUNT(*) FROM stg.stg_asistencia_diaria
            UNION ALL
            SELECT 'stg_realizacion_capacitaciones', COUNT(*) FROM stg.stg_realizacion_capacitaciones
            UNION ALL
            SELECT 'stg_participacion_capacitaciones', COUNT(*) FROM stg.stg_participacion_capacitaciones;
        """)
        for tabla, filas in cursor.fetchall():
            print(f"  {tabla}: {filas:,} filas")

        # Stats de DWH
        print("\n📊 DATA WAREHOUSE (dwh):")
        tables = [
            "fact_rotacion",
            "fact_dotacion_snapshot",
            "fact_asistencia",
            "fact_seleccion",
            "dim_empleado",
            "dim_cargo",
            "dim_empresa",
        ]
        for tabla in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM dwh.{tabla};")
                filas = cursor.fetchone()[0]
                emoji = "✓" if filas > 0 else "○"
                print(f"  {emoji} {tabla}: {filas:,} filas")
            except:
                conn.rollback()
                print(f"  ○ {tabla}: (no existe)")

        # Stats específicas de rotación
        print("\n🔄 ROTACIÓN (detalle):")
        cursor.execute("""
            SELECT 
                CASE variacion_headcount 
                    WHEN 1 THEN 'Altas (+1)'
                    WHEN -1 THEN 'Bajas (-1)'
                    ELSE 'Cambios (0)'
                END AS tipo,
                COUNT(*) AS cantidad
            FROM dwh.fact_rotacion
            GROUP BY variacion_headcount
            ORDER BY variacion_headcount DESC;
        """)
        for tipo, cantidad in cursor.fetchall():
            print(f"  {tipo}: {cantidad:,}")

        # Empleados sin SK
        cursor.execute("SELECT COUNT(*) FROM dwh.fact_rotacion WHERE empleado_sk = -1;")
        sin_sk = cursor.fetchone()[0]
        if sin_sk > 0:
            print(f"\n⚠️  Registros sin empleado_sk: {sin_sk}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")


# =============================================================================
# MAIN
# =============================================================================
def main():
    # Argumentos de línea de comandos
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "rebuild":
            rebuild_dwh()
        elif cmd == "trigger":
            trigger_dag()
        elif cmd == "sql":
            sql_console()
        elif cmd == "stats":
            quick_stats()
        else:
            print(f"Comando desconocido: {cmd}")
            print("Uso: python dev-tools.py [rebuild|trigger|sql|stats]")
        return

    # Menú interactivo
    while True:
        print_menu()
        option = input("Opción: ").strip()

        if option == "1":
            rebuild_dwh()
        elif option == "2":
            trigger_dag()
        elif option == "3":
            sql_console()
        elif option == "4":
            quick_stats()
        elif option == "0":
            print("\n¡Hasta luego!")
            break
        else:
            print("Opción no válida.")

        input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    main()

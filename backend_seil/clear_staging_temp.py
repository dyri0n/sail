import sys
from sqlalchemy import create_engine, text

# Connection details from docker-compose.yaml (mapped to localhost since we are on host)
# DWH_PORT is 6000
DB_URL = "postgresql://stg_admin:sail-stg-p4@localhost:6000/rrhh_prod"

cmds = [
    "TRUNCATE TABLE stg.stg_rotacion_empleados CASCADE;",
    "TRUNCATE TABLE stg.stg_capacitaciones_resumen CASCADE;",
    "TRUNCATE TABLE stg.stg_capacitaciones_participantes CASCADE;",
    "TRUNCATE TABLE stg.stg_asistencia_diaria_geovictoria CASCADE;"
]

def main():
    print(f"Connecting to {DB_URL}...")
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            for cmd in cmds:
                print(f"Executing: {cmd}")
                conn.execute(text(cmd))
                conn.commit()
        print("Success: Staging tables cleared.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

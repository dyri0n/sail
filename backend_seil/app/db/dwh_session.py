from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Conexión al Data Warehouse (puerto 6000)
# Usuario: dwh_admin, Database: rrhh_prod
DWH_DATABASE_URL = (
    "postgresql+psycopg2://"
    "dwh_admin:sail-rrhh-p4@localhost:6000/rrhh_prod"
)

dwh_engine = create_engine(DWH_DATABASE_URL)
DWHSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=dwh_engine)


def get_dwh_db() -> Session:
    """
    Dependency para FastAPI que proporciona una sesión de base de datos DWH.
    La sesión se cierra automáticamente después de cada request.
    """
    db = DWHSessionLocal()
    try:
        yield db
    finally:
        db.close()

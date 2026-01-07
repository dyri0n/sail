from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Conexión al Data Warehouse (puerto 6000)
DWH_DATABASE_URL = (
    "postgresql+psycopg2://"
    "dwh_admin:dwh_secret@localhost:6000/sail_dwh"
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

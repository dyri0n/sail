from app.db.session import SessionLocal
from app.models.file_load import FileLoad
from datetime import datetime


class FileRepository:

    def create(self, file_id, file_name, source_type, path):
        db = SessionLocal()
        try:
            record = FileLoad(
                id=file_id,
                file_name=file_name,
                source_type=source_type,
                path=path,
                status="uploaded",
                uploaded_at=datetime.utcnow()
            )
            db.add(record)
            db.commit()
        finally:
            db.close()

from app.db.session import SessionLocal
from app.models.audit import AuditLog
from app.utils.datetime_utils import now_chile

class AuditService:
    @staticmethod
    def log_event(
        action: str,
        user_id: str = None,
        username: str = None,
        resource: str = None,
        ip_address: str = None,
        level: str = "INFO",
        metadata: dict = None
    ):
        db = SessionLocal()
        try:
            log = AuditLog(
                user_id=user_id,
                username=username,
                action=action,
                resource=resource,
                ip_address=ip_address,
                level=level,
                metadata_json=metadata,
                timestamp=now_chile()
            )
            db.add(log)
            db.commit()
        finally:
            db.close()

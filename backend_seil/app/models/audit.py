import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base
from app.utils.datetime_utils import now_chile


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    username = Column(String, nullable=True)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    level = Column(String, default="INFO")  # INFO | WARNING | ERROR
    timestamp = Column(DateTime(timezone=True), default=now_chile)
    metadata_json = Column(JSON, nullable=True)

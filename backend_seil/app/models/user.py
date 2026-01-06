from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.db.base_class import Base
from app.utils.datetime_utils import now_chile


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)

    password_hash = Column(String, nullable=False)

    role = Column(String(20), nullable=False)  # ADMIN | GERENCIA
    department = Column(String(100), nullable=True)

    is_active = Column(Boolean, default=True)

    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_chile)
    
    # Relación con ETL executions
    etl_executions = relationship("ETLExecution", back_populates="triggered_by")

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base


class ExecutionState(str, enum.Enum):
    """Estados posibles de una ejecución ETL"""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskState(str, enum.Enum):
    """Estados posibles de una tarea ETL"""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    UP_FOR_RETRY = "up_for_retry"


class LogLevel(str, enum.Enum):
    """Niveles de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ETLExecution(Base):
    """Modelo para registrar ejecuciones de DAGs de Airflow"""
    __tablename__ = "etl_executions"

    id = Column(Integer, primary_key=True, index=True)
    dag_id = Column(String(250), nullable=False, index=True)
    dag_run_id = Column(String(250), nullable=False, unique=True, index=True)
    execution_date = Column(DateTime, nullable=True)
    triggered_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    state = Column(SQLEnum(ExecutionState), default=ExecutionState.QUEUED, nullable=False, index=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relaciones
    triggered_by = relationship("User", back_populates="etl_executions")
    tasks = relationship("ETLTaskInstance", back_populates="execution", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ETLExecution(id={self.id}, dag_id={self.dag_id}, state={self.state})>"


class ETLTaskInstance(Base):
    """Modelo para registrar instancias de tareas dentro de una ejecución"""
    __tablename__ = "etl_task_instances"

    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("etl_executions.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(String(250), nullable=False, index=True)
    state = Column(SQLEnum(TaskState), default=TaskState.QUEUED, nullable=False, index=True)
    try_number = Column(Integer, default=1, nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # Duración en segundos
    
    # Relaciones
    execution = relationship("ETLExecution", back_populates="tasks")
    logs = relationship("ETLLog", back_populates="task_instance", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ETLTaskInstance(id={self.id}, task_id={self.task_id}, state={self.state})>"


class ETLLog(Base):
    """Modelo para registrar logs individuales de tareas ETL"""
    __tablename__ = "etl_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_instance_id = Column(Integer, ForeignKey("etl_task_instances.id", ondelete="CASCADE"), nullable=False, index=True)
    log_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    level = Column(SQLEnum(LogLevel), default=LogLevel.INFO, nullable=False, index=True)
    message = Column(Text, nullable=False)

    # Relaciones
    task_instance = relationship("ETLTaskInstance", back_populates="logs")

    def __repr__(self):
        return f"<ETLLog(id={self.id}, level={self.level}, timestamp={self.log_timestamp})>"

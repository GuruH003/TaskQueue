from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum
from app.models.base import Base

class JobPriority(str, enum.Enum):
    critical = "critical"
    high = "high"
    normal = "normal"
    low = "low"

class JobStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"
    blocked = "blocked"

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.pending)
    priority = Column(Enum(JobPriority), default=JobPriority.normal)
    payload = Column(JSON)
    resource_cpu = Column(Integer, default=1)
    resource_memory = Column(Integer, default=128)
    depends_on = Column(JSON, default=list)
    timeout_seconds = Column(Integer, default=60)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

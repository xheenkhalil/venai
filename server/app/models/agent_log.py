import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_task_id = Column(UUID(as_uuid=True), ForeignKey("agent_tasks.id"), nullable=False, index=True)
    
    agent_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    
    input = Column(JSON, nullable=True)
    output = Column(JSON, nullable=True)
    
    execution_time = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

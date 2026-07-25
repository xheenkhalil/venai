import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    procurement_request_id = Column(UUID(as_uuid=True), ForeignKey("procurement_requests.id"), nullable=True, index=True)
    
    agent_type = Column(String, nullable=False) # supervisor, research, calling, analysis, report
    status = Column(String, default="pending", nullable=False) # pending, running, completed, failed, waiting_approval
    
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

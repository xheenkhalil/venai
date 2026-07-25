from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

class Call(Base):
    __tablename__ = "calls"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), index=True)
    agent_task_id = Column(UUID(as_uuid=True), ForeignKey("agent_tasks.id"), index=True, nullable=True)
    
    call_provider = Column(String, default="calle")
    external_call_id = Column(String, index=True) # Run ID from CALL-E
    
    status = Column(String, default="queued") # queued, ringing, connected, completed, failed, cancelled
    phone_number = Column(String)
    
    duration = Column(Integer, default=0)
    
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    vendor = relationship("Vendor")
    transcript = relationship("CallTranscript", back_populates="call", uselist=False)

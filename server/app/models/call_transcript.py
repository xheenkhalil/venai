from sqlalchemy import Column, String, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

class CallTranscript(Base):
    __tablename__ = "call_transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), unique=True)
    
    transcript = Column(Text)
    summary = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True)
    language = Column(String, default="en")
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    call = relationship("Call", back_populates="transcript")

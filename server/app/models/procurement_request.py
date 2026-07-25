import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class ProcurementRequest(Base):
    __tablename__ = "procurement_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=True)
    budget = Column(String, nullable=True) # E.g. 10000.00
    currency = Column(String, nullable=True)
    location = Column(String, nullable=True)
    requirements = Column(Text, nullable=True)
    
    # Statuses: draft, searching, calling, analyzing, completed, cancelled
    status = Column(String, default="draft", nullable=False)
    
    analysis_result = Column(Text, nullable=True)
    call_results_json = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

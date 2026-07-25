import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class ProcurementRequestVendor(Base):
    __tablename__ = "procurement_request_vendors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    procurement_request_id = Column(UUID(as_uuid=True), ForeignKey("procurement_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

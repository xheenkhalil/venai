from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.base_class import Base

class VendorOffer(Base):
    __tablename__ = "vendor_offers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), index=True)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), index=True)
    procurement_request_id = Column(UUID(as_uuid=True), ForeignKey("procurement_requests.id"), index=True)
    call_id = Column(UUID(as_uuid=True), ForeignKey("calls.id"), nullable=True)
    
    price = Column(Float, nullable=True)
    currency = Column(String, default="USD")
    delivery_time = Column(String, nullable=True)
    warranty = Column(String, nullable=True)
    payment_terms = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    vendor = relationship("Vendor")
    procurement_request = relationship("ProcurementRequest")

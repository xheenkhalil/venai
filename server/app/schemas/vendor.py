from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class VendorContactBase(BaseModel):
    name: str
    position: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class VendorContactCreate(VendorContactBase):
    pass

class VendorContact(VendorContactBase):
    id: UUID
    vendor_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class VendorBase(BaseModel):
    company_name: str
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    source: Optional[str] = None
    verification_status: Optional[str] = "unknown"

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    verification_status: Optional[str] = None

class Vendor(VendorBase):
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class VendorWithContacts(Vendor):
    contacts: List[VendorContact] = []

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID

class ProcurementRequestBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    product_name: str
    quantity: Optional[int] = None
    budget: Optional[str] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    requirements: Optional[str] = None

class ProcurementRequestCreate(ProcurementRequestBase):
    pass

class ProcurementRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    product_name: Optional[str] = None
    quantity: Optional[int] = None
    budget: Optional[str] = None
    currency: Optional[str] = None
    location: Optional[str] = None
    requirements: Optional[str] = None
    status: Optional[str] = None

class ProcurementRequest(ProcurementRequestBase):
    id: UUID
    organization_id: UUID
    created_by: UUID
    status: str
    analysis_result: Optional[str] = None
    call_results_json: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

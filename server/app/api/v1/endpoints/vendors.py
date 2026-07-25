import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.dependencies import get_current_user
from app.db.session import AsyncSessionLocal
from app.models.vendor import Vendor as DBVendor
from app.models.vendor_contact import VendorContact as DBVendorContact
from app.models.procurement_request import ProcurementRequest as DBProcurementRequest
from app.models.procurement_request_vendor import ProcurementRequestVendor
from app.schemas.vendor import Vendor, VendorCreate, VendorWithContacts, VendorUpdate
from app.api.v1.endpoints.procurement_requests import get_or_create_user_org
from app.services.vendor_search import search_for_vendors

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/", response_model=List[Vendor])
async def read_vendors(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("sub")
    email = current_user.get("email", "")
    name = current_user.get("name", "")
    
    user_id, org_id = await get_or_create_user_org(db, clerk_id, email, name)
    
    result = await db.execute(
        select(DBVendor).filter(DBVendor.organization_id == org_id).order_by(DBVendor.created_at.desc())
    )
    return result.scalars().all()

@router.post("/", response_model=Vendor)
async def create_vendor(
    vendor_in: VendorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("sub")
    user_id, org_id = await get_or_create_user_org(db, clerk_id, "", "")
    
    db_vendor = DBVendor(
        **vendor_in.model_dump(),
        organization_id=org_id
    )
    db.add(db_vendor)
    await db.commit()
    await db.refresh(db_vendor)
    return db_vendor

@router.put("/{vendor_id}", response_model=Vendor)
async def update_vendor(
    vendor_id: str,
    vendor_in: VendorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("sub")
    user_id, org_id = await get_or_create_user_org(db, clerk_id, "", "")
    
    try:
        v_uuid = uuid.UUID(vendor_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid vendor ID")
        
    result = await db.execute(select(DBVendor).filter(DBVendor.id == v_uuid, DBVendor.organization_id == org_id))
    db_vendor = result.scalars().first()
    
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    update_data = vendor_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vendor, field, value)
        
    await db.commit()
    await db.refresh(db_vendor)
    return db_vendor

@router.delete("/{vendor_id}")
async def delete_vendor(
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("sub")
    user_id, org_id = await get_or_create_user_org(db, clerk_id, "", "")
    
    try:
        v_uuid = uuid.UUID(vendor_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid vendor ID")
        
    result = await db.execute(select(DBVendor).filter(DBVendor.id == v_uuid, DBVendor.organization_id == org_id))
    db_vendor = result.scalars().first()
    
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    await db.delete(db_vendor)
    await db.commit()
    return {"status": "success", "detail": "Vendor deleted"}

@router.post("/search")
async def search_and_add_vendors(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("sub")
    user_id, org_id = await get_or_create_user_org(db, clerk_id, "", "")
    
    # 1. Fetch procurement request
    try:
        req_uuid = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid request ID format")

    result = await db.execute(
        select(DBProcurementRequest).filter(
            DBProcurementRequest.id == req_uuid,
            DBProcurementRequest.organization_id == org_id
        )
    )
    proc_req = result.scalars().first()
    if not proc_req:
        raise HTTPException(status_code=404, detail="Procurement Request not found")
        
    # 2. Update status to 'searching'
    proc_req.status = "searching"
    await db.commit()
    
    # 3. Perform Tavily Search
    query_str = f"{proc_req.product_name} {proc_req.category or ''} {proc_req.location or ''}"
    try:
        raw_vendors = search_for_vendors(query_str, limit=4)
    except Exception as e:
        proc_req.status = "draft"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
        
    # 4. Save vendors to DB
    saved_vendors = []
    for v_data in raw_vendors:
        phone = v_data.get("phone", "")[:50]
        email = v_data.get("email", "")[:255]
        whatsapp = v_data.get("whatsapp", "")[:50]
        
        # Discard vendor if all contact channels are N/A
        if not phone and not email and not whatsapp:
            continue
            
        db_vendor = DBVendor(
            organization_id=org_id,
            company_name=v_data.get("company_name", "Unknown")[:255],
            description=v_data.get("description", ""),
            website=v_data.get("website", "")[:255],
            phone=phone,
            email=email,
            whatsapp=whatsapp,
            source="tavily_search"
        )
        db.add(db_vendor)
        # Flush to get the db_vendor.id
        await db.flush()
        
        # Link vendor to request
        assoc = ProcurementRequestVendor(
            procurement_request_id=proc_req.id,
            vendor_id=db_vendor.id
        )
        db.add(assoc)
        saved_vendors.append(db_vendor)
        
    # Update status to 'analyzing'
    proc_req.status = "analyzing"
    await db.commit()
    
    return {"status": "success", "vendors_found": len(saved_vendors)}

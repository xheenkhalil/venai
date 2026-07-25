import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.dependencies import get_current_user
from app.db.session import AsyncSessionLocal
from app.models.procurement_request import ProcurementRequest as DBProcurementRequest
from app.models.user import User as DBUser
from app.models.organization import Organization as DBOrganization
from app.models.organization_member import OrganizationMember as DBOrganizationMember
from app.models.vendor import Vendor as DBVendor
from app.models.procurement_request_vendor import ProcurementRequestVendor
from app.schemas.procurement_request import ProcurementRequest, ProcurementRequestCreate, ProcurementRequestUpdate
from app.schemas.vendor import Vendor

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_or_create_user_org(db: AsyncSession, clerk_id: str, email: str, name: str) -> tuple[uuid.UUID, uuid.UUID]:
    """Helper to ensure user and a personal organization exist."""
    # Find user
    result = await db.execute(select(DBUser).filter(DBUser.clerk_id == clerk_id))
    user = result.scalars().first()
    
    if not user:
        user = DBUser(clerk_id=clerk_id, email=email, name=name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    # Find org member
    org_member_result = await db.execute(select(DBOrganizationMember).filter(DBOrganizationMember.user_id == user.id))
    org_member = org_member_result.scalars().first()
    
    if org_member:
        return user.id, org_member.organization_id
        
    # Check if personal org already exists (e.g. if a previous request crashed midway)
    org_clerk_id = f"org_{user.id}"
    org_result = await db.execute(select(DBOrganization).filter(DBOrganization.clerk_id == org_clerk_id))
    org = org_result.scalars().first()
    
    if not org:
        # Create personal org
        org = DBOrganization(clerk_id=org_clerk_id, name=f"{name or 'User'}'s Organization")
        db.add(org)
        await db.commit()
        await db.refresh(org)
    
    member = DBOrganizationMember(organization_id=org.id, user_id=user.id, role="owner")
    db.add(member)
    await db.commit()
    
    return user.id, org.id

@router.get("/", response_model=List[ProcurementRequest])
async def read_requests(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("sub")
    email = current_user.get("email", "")
    name = current_user.get("name", "")
    
    user_id, org_id = await get_or_create_user_org(db, clerk_id, email, name)
    
    result = await db.execute(
        select(DBProcurementRequest)
        .filter(DBProcurementRequest.organization_id == org_id)
        .order_by(DBProcurementRequest.created_at.desc())
    )
    return result.scalars().all()

@router.post("/", response_model=ProcurementRequest)
async def create_request(
    request_in: ProcurementRequestCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("sub")
    email = current_user.get("email", "")
    name = current_user.get("name", "")
    
    user_id, org_id = await get_or_create_user_org(db, clerk_id, email, name)
    
    db_request = DBProcurementRequest(
        **request_in.model_dump(),
        organization_id=org_id,
        created_by=user_id,
        status="draft"
    )
    db.add(db_request)
    await db.commit()
    await db.refresh(db_request)
    return db_request

@router.get("/{request_id}", response_model=ProcurementRequest)
async def read_request(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("sub")
    user_id, org_id = await get_or_create_user_org(db, clerk_id, "", "")
    
    try:
        req_uuid = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = await db.execute(
        select(DBProcurementRequest).filter(
            DBProcurementRequest.id == req_uuid,
            DBProcurementRequest.organization_id == org_id
        )
    )
    proc_req = result.scalars().first()
    if not proc_req:
        raise HTTPException(status_code=404, detail="Procurement Request not found")
    
    return proc_req

@router.get("/{request_id}/vendors", response_model=List[Vendor])
async def read_request_vendors(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("sub")
    user_id, org_id = await get_or_create_user_org(db, clerk_id, "", "")
    
    try:
        req_uuid = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid ID format")

    result = await db.execute(
        select(DBVendor)
        .join(ProcurementRequestVendor, DBVendor.id == ProcurementRequestVendor.vendor_id)
        .filter(
            ProcurementRequestVendor.procurement_request_id == req_uuid,
            DBVendor.organization_id == org_id
        )
        .order_by(DBVendor.created_at.desc())
    )
    return result.scalars().all()

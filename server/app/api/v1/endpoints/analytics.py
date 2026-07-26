from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.procurement_request import ProcurementRequest
from app.models.vendor import Vendor
from app.models.call import Call

from app.api.v1.endpoints.procurement_requests import get_or_create_user_org

router = APIRouter()

@router.get("/")
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    clerk_id = current_user.get("sub")
    user_id, org_id = await get_or_create_user_org(db, clerk_id, f"{clerk_id}@placeholder.com", "User")
    
    # Total Procurement Requests
    req_result = await db.execute(
        select(func.count(ProcurementRequest.id)).where(ProcurementRequest.organization_id == org_id)
    )
    total_requests = req_result.scalar() or 0
    
    # Total Vendors
    ven_result = await db.execute(
        select(func.count(Vendor.id)).where(Vendor.organization_id == org_id)
    )
    total_vendors = ven_result.scalar() or 0
    
    # Total Calls
    call_result = await db.execute(
        select(func.count(Call.id)).where(Call.organization_id == org_id)
    )
    total_calls = call_result.scalar() or 0
    
    # Budget Managed
    # Budget Managed
    budget_result = await db.execute(
        select(ProcurementRequest.budget).where(ProcurementRequest.organization_id == org_id)
    )
    budgets = budget_result.scalars().all()
    total_budget = 0.0
    for b in budgets:
        if b:
            try:
                clean_b = str(b).replace('$', '').replace(',', '').strip()
                total_budget += float(clean_b)
            except ValueError:
                pass
    
    return {
        "total_requests": total_requests,
        "total_vendors": total_vendors,
        "total_calls": total_calls,
        "total_budget": total_budget
    }

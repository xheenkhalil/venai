import uuid
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.dependencies import get_current_user
from app.db.session import AsyncSessionLocal
from app.models.agent_task import AgentTask
from app.models.procurement_request import ProcurementRequest
from app.models.vendor import Vendor
from app.api.v1.endpoints.procurement_requests import get_or_create_user_org
from app.agents.graph import app_graph

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def run_agent_workflow_async(request_id: str, org_id: str, product_name: str, requirements: str, location: str, budget: str, vendors: list):
    initial_state = {
        "request_id": request_id,
        "organization_id": org_id,
        "product_name": product_name,
        "requirements": requirements,
        "location": location,
        "budget": budget,
        "vendors": vendors,
        "call_results": [],
        "analysis_report": "",
        "final_report": "",
        "messages": []
    }
    
    try:
        final_state = await app_graph.ainvoke(initial_state)
        return final_state
    except Exception as e:
        print(f"Workflow failed: {str(e)}")
        raise e

@router.post("/start/{request_id}")
async def start_agent_workflow(
    request_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("sub")
    user_id, org_id = await get_or_create_user_org(db, clerk_id, f"{clerk_id}@placeholder.com", "User")
    
    req_uuid = uuid.UUID(request_id)
    result = await db.execute(
        select(ProcurementRequest).filter(
            ProcurementRequest.id == req_uuid,
            ProcurementRequest.organization_id == org_id
        )
    )
    proc_req = result.scalars().first()
    if not proc_req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    v_result = await db.execute(
        select(Vendor).filter(Vendor.organization_id == org_id)
    )
    db_vendors = v_result.scalars().all()
    vendors_list = [
        {
            "id": str(v.id), 
            "company_name": v.company_name,
            "phone": v.phone or "",
            "email": v.email or "",
            "whatsapp": getattr(v, "whatsapp", "") or ""
        } 
        for v in db_vendors
    ]
    task = AgentTask(
        organization_id=org_id,
        procurement_request_id=req_uuid,
        agent_type="supervisor",
        status="running",
        started_at=datetime.now(timezone.utc)
    )
    db.add(task)
    await db.commit()
    
    try:
        final_state = await run_agent_workflow_async(
            request_id=str(proc_req.id),
            org_id=str(org_id),
            product_name=proc_req.product_name,
            requirements=proc_req.requirements or "",
            location=proc_req.location or "",
            budget=proc_req.budget or "",
            vendors=vendors_list
        )
        
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)
        
        proc_req.analysis_result = final_state.get("final_report", "")
        call_results = final_state.get("call_results", [])
        if call_results:
            proc_req.call_results_json = json.dumps(call_results)
        proc_req.status = "completed"
        
        await db.commit()
        return {"status": "success", "task_id": str(task.id)}
        
    except Exception as e:
        task.status = "failed"
        task.output_data = {"error": str(e)}
        proc_req.status = "failed"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Agent workflow failed: {str(e)}")

@router.post("/call/{request_id}/{vendor_id}")
async def call_single_vendor(
    request_id: str,
    vendor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    clerk_id = current_user.get("sub")
    user_id, org_id = await get_or_create_user_org(db, clerk_id, f"{clerk_id}@placeholder.com", "User")
    
    req_uuid = uuid.UUID(request_id)
    v_uuid = uuid.UUID(vendor_id)
    
    # Get request
    req_res = await db.execute(select(ProcurementRequest).filter(ProcurementRequest.id == req_uuid, ProcurementRequest.organization_id == org_id))
    proc_req = req_res.scalars().first()
    if not proc_req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    # Get vendor
    ven_res = await db.execute(select(Vendor).filter(Vendor.id == v_uuid, Vendor.organization_id == org_id))
    vendor = ven_res.scalars().first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
        
    phone = vendor.phone
    if not phone:
        # Default test phone if none
        phone = "+2347068083455"
        
    goal = f"Call {vendor.company_name} to inquire about purchasing {proc_req.product_name}. Our budget is {proc_req.budget or 'flexible'} and requirements are: {proc_req.requirements or 'standard quality'}."
    
    from app.services.call_e import CallEService
    import asyncio
    
    try:
        start_res = await CallEService.start_call(phone, goal)
        run_id = start_res.get("run_id")
        if not run_id:
            raise Exception("No run_id returned")
            
        def parse_status(data):
            sc = data.get("status_result", {}).get("structuredContent", {})
            if not sc:
                sc = data.get("result", {}).get("structuredContent", {})
            return sc.get("status", "error"), sc.get("message", "")
            
        status, msg = parse_status(start_res)
        
        call_data = start_res
        while status not in ["COMPLETED", "FAILED", "NO_ANSWER", "DECLINED", "CANCELED", "CANCELLED", "VOICEMAIL", "BUSY", "EXPIRED", "error"]:
            await asyncio.sleep(3)
            call_data = await CallEService.get_call_status(run_id)
            status, msg = parse_status(call_data)
            
        if status == "COMPLETED":
            from langchain_google_genai import ChatGoogleGenerativeAI
            from app.core.config import settings
            from pydantic import BaseModel
            
            class ExtractedOffer(BaseModel):
                availability: bool
                price: float
                delivery_days: int
                warranty: str
                notes: str
                
            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1, google_api_key=settings.GEMINI_API_KEY)
            structured_llm = llm.with_structured_output(ExtractedOffer)
            
            raw_text = json.dumps(call_data)
            offer: ExtractedOffer = structured_llm.invoke(f"Extract the vendor offer from this call data:\n{raw_text}")
            
            result = {
                "status": "COMPLETED",
                "available": offer.availability,
                "price": offer.price,
                "delivery": f"{offer.delivery_days} days",
                "notes": offer.notes
            }
        else:
            notes = f"Call failed with status {status}."
            if "Region is not allowed" in msg:
                notes = "Destination country is not currently supported by CALL-E."
            elif msg:
                notes += f" Message: {msg}"
            
            result = {
                "status": "FAILED",
                "notes": notes
            }
            
        return result
        
    except Exception as e:
        return {"status": "FAILED", "notes": f"Error: {str(e)}"}

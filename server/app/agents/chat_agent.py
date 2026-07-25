import uuid
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool

from app.core.config import settings
from app.models.procurement_request import ProcurementRequest
from app.models.chat import ChatMessage, ChatSession
from app.agents.graph import app_graph
import json

def get_chat_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3,
        google_api_key=settings.GEMINI_API_KEY,
    )

class ChatAgent:
    def __init__(self, db: AsyncSession, session_id: uuid.UUID, user_id: uuid.UUID, organization_id: uuid.UUID):
        self.db = db
        self.session_id = session_id
        self.user_id = user_id
        self.organization_id = organization_id
        self.llm = get_chat_llm()
        
    async def get_history(self) -> List[BaseMessage]:
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == self.session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        msgs = result.scalars().all()
        history = []
        for m in msgs:
            if m.role == "user":
                history.append(HumanMessage(content=m.content))
            elif m.role == "ai":
                history.append(AIMessage(content=m.content))
            # System/Tool roles can be appended if needed, but for simplicity we keep AI/User.
        return history
        
    async def create_and_start_workflow(self, product_name: str, budget: float, requirements: str) -> str:
        """Create a new procurement request and trigger the background workflow."""
        req = ProcurementRequest(
            title=f"Procurement for {product_name}",
            product_name=product_name,
            budget=str(budget),
            requirements=requirements,
            organization_id=self.organization_id,
            created_by=self.user_id,
            status="pending"
        )
        self.db.add(req)
        await self.db.commit()
        await self.db.refresh(req)
        
        request_id = str(req.id)
        session_id = self.session_id
        
        import asyncio
        async def run_bg():
            from app.db.session import AsyncSessionLocal
            async with AsyncSessionLocal() as bg_db:
                req_uuid = uuid.UUID(request_id)
                res = await bg_db.execute(select(ProcurementRequest).where(ProcurementRequest.id == req_uuid))
                req = res.scalars().first()
                if req:
                    req.status = "in_progress"
                    await bg_db.commit()
                
                initial_state = {
                    "request_id": request_id,
                    "product_name": req.product_name if req else "",
                    "budget": req.budget if req else 0.0,
                    "requirements": req.requirements if req else "",
                    "vendors": [],
                    "call_results": [],
                    "messages": []
                }
                
                try:
                    final_state = await app_graph.ainvoke(initial_state)
                    res2 = await bg_db.execute(select(ProcurementRequest).where(ProcurementRequest.id == req_uuid))
                    req_update = res2.scalars().first()
                    if req_update:
                        req_update.status = "completed"
                        req_update.call_results_json = final_state.get("call_results", [])
                        if final_state.get("messages"):
                            req_update.analysis_result = final_state["messages"][-1].content
                        await bg_db.commit()
                        
                        ai_text = f"**Final Results for {req_update.product_name}**\n\n{req_update.analysis_result}"
                        ai_msg = ChatMessage(session_id=session_id, role="ai", content=ai_text)
                        bg_db.add(ai_msg)
                        await bg_db.commit()
                except Exception as e:
                    print(f"Workflow error: {e}")
                    res2 = await bg_db.execute(select(ProcurementRequest).where(ProcurementRequest.id == req_uuid))
                    req_update = res2.scalars().first()
                    if req_update:
                        req_update.status = "failed"
                        await bg_db.commit()
                        
                        ai_text = f"**Error for {req_update.product_name}**: The workflow failed. Details: {e}"
                        ai_msg = ChatMessage(session_id=session_id, role="ai", content=ai_text)
                        bg_db.add(ai_msg)
                        await bg_db.commit()

        asyncio.create_task(run_bg())
        return f"Workflow successfully started for {product_name}. Tell the user you are contacting vendors and will post results in this chat shortly."

    async def check_status(self, request_id: str) -> str:
        """Check the status and results of a procurement request."""
        req_uuid = uuid.UUID(request_id)
        res = await self.db.execute(select(ProcurementRequest).where(ProcurementRequest.id == req_uuid))
        req = res.scalars().first()
        if not req:
            return "Request not found."
            
        if req.status != "completed":
            return f"Status is {req.status}."
            
        return f"Status is completed. Results:\n{json.dumps(req.call_results_json, indent=2)}\n\nAnalysis: {req.analysis_result}"

    async def get_recent_requests(self) -> str:
        """Get the user's recent procurement requests with their IDs and statuses."""
        res = await self.db.execute(
            select(ProcurementRequest)
            .where(ProcurementRequest.organization_id == self.organization_id)
            .order_by(ProcurementRequest.created_at.desc())
            .limit(5)
        )
        reqs = res.scalars().all()
        if not reqs:
            return "No recent requests."
        out = []
        for r in reqs:
            out.append(f"ID: {r.id}, Product: {r.product_name}, Status: {r.status}")
        return "\n".join(out)

    async def process_message(self, user_text: str) -> str:
        # Save user message
        user_msg = ChatMessage(session_id=self.session_id, role="user", content=user_text)
        self.db.add(user_msg)
        await self.db.commit()
        
        # Tools definitions for the LLM
        # We define them as standard python functions and use Langchain's bind_tools
        @tool
        async def tool_create_and_start_workflow(product_name: str, budget: float, requirements: str) -> str:
            """Create a new procurement request and start the AI workflow to contact vendors. Use this when the user asks to buy or procure something."""
            return await self.create_and_start_workflow(product_name, budget, requirements)
            
        @tool
        async def tool_check_status(request_id: str) -> str:
            """Check the status, call results, and AI recommendations for a given request ID."""
            return await self.check_status(request_id)
            
        @tool
        async def tool_list_requests() -> str:
            """List recent procurement requests to find their IDs."""
            return await self.get_recent_requests()

        tools = [tool_create_and_start_workflow, tool_check_status, tool_list_requests]
        llm_with_tools = self.llm.bind_tools(tools)
        
        system_prompt = SystemMessage(content='''You are VenAI Copilot, an intelligent procurement assistant.
You help users create procurement requests and contact vendors in the background.
If a user asks to buy something, gather the product name, budget, and requirements, then immediately use tool_create_and_start_workflow. 
Do not ask for permission to start the workflow. Once started, tell the user you are contacting vendors and will post the results in this chat shortly.
Never show database UUIDs to the user. Always refer to requests by their product name (e.g. "2000 Dell laptop computers"). Use markdown hyperlinks if you generate links.
If they ask for status, use tool_list_requests to find the ID, then tool_check_status to get details, but only show the product name to the user.
''')
        
        history = await self.get_history()
        messages = [system_prompt] + history
        
        # Run agent loop
        response = await llm_with_tools.ainvoke(messages)
        
        while response.tool_calls:
            messages.append(response)
            for tc in response.tool_calls:
                func_name = tc["name"]
                args = tc["args"]
                
                if func_name == "tool_create_and_start_workflow":
                    res = await tool_create_and_start_workflow.ainvoke(args)
                elif func_name == "tool_check_status":
                    res = await tool_check_status.ainvoke(args)
                elif func_name == "tool_list_requests":
                    res = await tool_list_requests.ainvoke(args)
                else:
                    res = "Unknown tool"
                    
                messages.append({
                    "role": "tool",
                    "name": func_name,
                    "content": str(res),
                    "tool_call_id": tc["id"]
                })
            
            # Next LLM call
            response = await llm_with_tools.ainvoke(messages)
            
        ai_text = response.content
        if isinstance(ai_text, list):
            # Extract text from list of dicts (Gemini sometimes returns content as a list)
            text_parts = []
            for part in ai_text:
                if isinstance(part, dict) and "text" in part:
                    text_parts.append(part["text"])
                elif isinstance(part, str):
                    text_parts.append(part)
            ai_text = " ".join(text_parts)
            
        if not isinstance(ai_text, str):
            ai_text = str(ai_text)        
        # Save AI message
        ai_msg = ChatMessage(session_id=self.session_id, role="ai", content=ai_text)
        self.db.add(ai_msg)
        await self.db.commit()
        
        return ai_text

import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ChatMessageCreate(BaseModel):
    role: str
    content: str
    
class ChatMessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime
    
class ChatSessionCreate(BaseModel):
    title: str | None = "New Chat"

class ChatSessionResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    updated_at: datetime

class ChatSessionDetailResponse(ChatSessionResponse):
    messages: List[ChatMessageResponse]

from app.api.v1.endpoints.procurement_requests import get_or_create_user_org

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    clerk_id = current_user.get("sub")
    user_id, _ = await get_or_create_user_org(db, clerk_id, "", "")
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
    )
    sessions = result.scalars().all()
    return sessions

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_in: ChatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    clerk_id = current_user.get("sub")
    user_id, org_id = await get_or_create_user_org(db, clerk_id, "", "")
    session = ChatSession(
        user_id=user_id,
        organization_id=org_id,
        title=session_in.title
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session

@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse)
async def get_chat_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    clerk_id = current_user.get("sub")
    user_id, _ = await get_or_create_user_org(db, clerk_id, "", "")
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    clerk_id = current_user.get("sub")
    user_id, _ = await get_or_create_user_org(db, clerk_id, "", "")
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    await db.delete(session)
    await db.commit()
    return {"success": True}

@router.post("/sessions/{session_id}/messages", response_model=ChatMessageResponse)
async def send_chat_message(
    session_id: uuid.UUID,
    message_in: ChatMessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Any:
    clerk_id = current_user.get("sub")
    user_id, org_id = await get_or_create_user_org(db, clerk_id, "", "")
    
    # Verify session
    result = await db.execute(
        select(ChatSession).where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    from app.agents.chat_agent import ChatAgent
    agent = ChatAgent(db, session_id, user_id, org_id)
    
    # Process message through LangGraph/LangChain agent
    ai_response = await agent.process_message(message_in.content)
    
    # Fetch the newly created AI message from DB to return
    res = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(1)
    )
    ai_msg = res.scalars().first()
    return ai_msg

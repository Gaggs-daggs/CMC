"""
Session Management Routes
API endpoints for managing user conversation sessions with database persistence

Features:
- List all sessions for a user
- Create new session
- Get session details with messages
- Switch between sessions
- Delete/archive sessions
- Auto-save messages from conversations
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

from ..utils.database import db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionSummary(BaseModel):
    """Summary of a session for sidebar display"""
    session_id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int
    last_message_preview: Optional[str] = None
    symptom_summary: Optional[str] = None
    symptoms: List[str] = []
    urgency_level: str = "self_care"


class CreateSessionRequest(BaseModel):
    user_phone: Optional[str] = None
    user_id: Optional[str] = None
    language: str = "en"
    title: Optional[str] = None


class ListSessionsRequest(BaseModel):
    user_phone: Optional[str] = None
    user_id: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    title: Optional[str] = None
    is_archived: Optional[bool] = None


class AddMessageRequest(BaseModel):
    role: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


def generate_session_title(messages: List[Dict]) -> str:
    """Generate a title from the first user message"""
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if len(content) > 40:
                return content[:37] + "..."
            return content or "New Chat"
    return "New Chat"


def get_database():
    """Get database instance"""
    return db.get_db()


@router.post("/list")
async def list_sessions(request: ListSessionsRequest):
    """
    List all sessions for a user (for sidebar)
    Returns sessions sorted by last updated (most recent first)
    """
    phone = request.user_phone or request.user_id
    if not phone:
        raise HTTPException(status_code=400, detail="user_phone or user_id required")
    
    database = get_database()
    
    # Find all sessions for this user
    summaries = []
    cursor = database.sessions.find({"user_phone": phone})
    
    async for session_data in cursor:
        if session_data.get("is_archived", False):
            continue
        
        messages = session_data.get("messages", [])
        last_message = messages[-1] if messages else None
        
        # Generate symptom summary from symptoms list
        symptoms = session_data.get("symptoms", [])
        symptom_summary = ", ".join(symptoms[:3]) if symptoms else None
        if symptoms and len(symptoms) > 3:
            symptom_summary += f" +{len(symptoms) - 3} more"
        
        created_at = session_data.get("created_at")
        updated_at = session_data.get("updated_at")
        
        # Handle datetime serialization
        if isinstance(created_at, datetime):
            created_at = created_at.isoformat()
        if isinstance(updated_at, datetime):
            updated_at = updated_at.isoformat()
        
        summaries.append(SessionSummary(
            session_id=session_data.get("session_id"),
            title=session_data.get("title", generate_session_title(messages)),
            created_at=created_at or datetime.now().isoformat(),
            updated_at=updated_at or datetime.now().isoformat(),
            message_count=len(messages),
            last_message_preview=last_message.get("content", "")[:100] if last_message else None,
            symptom_summary=symptom_summary,
            symptoms=symptoms,
            urgency_level=session_data.get("urgency_level", "self_care")
        ))
    
    # Sort by updated_at descending
    summaries.sort(key=lambda x: x.updated_at, reverse=True)
    
    return {"success": True, "sessions": [s.model_dump() for s in summaries]}


@router.post("/create")
async def create_session(request: CreateSessionRequest):
    """
    Create a new conversation session
    """
    phone = request.user_phone or request.user_id
    if not phone:
        raise HTTPException(status_code=400, detail="user_phone or user_id required")
    
    session_id = str(uuid.uuid4())
    now = datetime.now()
    
    database = get_database()
    
    session_data = {
        "session_id": session_id,
        "user_phone": phone,
        "title": request.title or "New Chat",
        "created_at": now,
        "updated_at": now,
        "messages": [],
        "symptoms": [],
        "urgency_level": "self_care",
        "language": request.language,
        "is_archived": False
    }
    
    await database.sessions.insert_one(session_data)
    
    logger.info(f"Created new session {session_id} for user {phone}")
    
    return {
        "success": True,
        "session": {
            "session_id": session_id,
            "title": session_data["title"],
            "created_at": now.isoformat()
        }
    }


@router.get("/{session_id}")
async def get_session(session_id: str, user_id: Optional[str] = None, user_phone: Optional[str] = None):
    """
    Get full session details including all messages
    """
    phone = user_phone or user_id
    if not phone:
        raise HTTPException(status_code=400, detail="user_phone or user_id required")
    
    database = get_database()
    session_data = await database.sessions.find_one({"session_id": session_id, "user_phone": phone})
    
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    created_at = session_data.get("created_at")
    updated_at = session_data.get("updated_at")
    
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()
    if isinstance(updated_at, datetime):
        updated_at = updated_at.isoformat()
    
    return {
        "success": True,
        "session": {
            "session_id": session_id,
            "user_phone": phone,
            "title": session_data.get("title", "Chat"),
            "created_at": created_at,
            "updated_at": updated_at,
            "messages": session_data.get("messages", []),
            "symptoms": session_data.get("symptoms", []),
            "urgency_level": session_data.get("urgency_level", "self_care"),
            "language": session_data.get("language", "en")
        }
    }


@router.put("/{session_id}")
async def update_session(session_id: str, request: UpdateSessionRequest, user_id: Optional[str] = None, user_phone: Optional[str] = None):
    """
    Update session (title, archive status)
    """
    phone = user_phone or user_id
    if not phone:
        raise HTTPException(status_code=400, detail="user_phone or user_id required")
    
    database = get_database()
    
    update_data = {"updated_at": datetime.now()}
    if request.title is not None:
        update_data["title"] = request.title
    if request.is_archived is not None:
        update_data["is_archived"] = request.is_archived
    
    result = await database.sessions.update_one(
        {"session_id": session_id, "user_phone": phone},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True, "status": "updated", "session_id": session_id}


@router.delete("/{session_id}")
async def delete_session(session_id: str, user_id: Optional[str] = None, user_phone: Optional[str] = None):
    """
    Archive a session (soft delete)
    """
    phone = user_phone or user_id
    if not phone:
        raise HTTPException(status_code=400, detail="user_phone or user_id required")
    
    database = get_database()
    
    result = await database.sessions.update_one(
        {"session_id": session_id, "user_phone": phone},
        {"$set": {"is_archived": True, "updated_at": datetime.now()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    logger.info(f"Archived session {session_id}")
    
    return {"success": True, "status": "archived", "session_id": session_id}


# ============================================
# Helper functions for conversation integration
# ============================================

async def get_or_create_session(user_phone: str, session_id: str = None, language: str = "en") -> Dict[str, Any]:
    """
    Get existing session or create new one
    Used by conversation routes to link messages to sessions
    """
    database = get_database()
    
    if session_id:
        # Try to find existing session
        session = await database.sessions.find_one({"session_id": session_id})
        if session:
            return session
    
    # Create new session
    new_session_id = session_id or str(uuid.uuid4())
    now = datetime.now()
    
    session_data = {
        "session_id": new_session_id,
        "user_phone": user_phone,
        "title": "New Chat",
        "created_at": now,
        "updated_at": now,
        "messages": [],
        "symptoms": [],
        "urgency_level": "self_care",
        "language": language,
        "is_archived": False
    }
    
    await database.sessions.insert_one(session_data)
    logger.info(f"Auto-created session {new_session_id} for user {user_phone}")
    
    return session_data


async def save_message_to_session(session_id: str, role: str, content: str, metadata: Dict = None):
    """
    Save a message to the session
    Called after each conversation turn
    """
    database = get_database()
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    # Update session with new message
    result = await database.sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {"messages": message},
            "$set": {"updated_at": datetime.now()}
        }
    )
    
    # Auto-update title if still "New Chat" and this is a user message
    if role == "user":
        session = await database.sessions.find_one({"session_id": session_id})
        if session and session.get("title") == "New Chat":
            new_title = content[:37] + "..." if len(content) > 40 else content
            await database.sessions.update_one(
                {"session_id": session_id},
                {"$set": {"title": new_title}}
            )
    
    return result.modified_count > 0


async def update_session_symptoms(session_id: str, symptoms: List[str], urgency_level: str = None):
    """
    Update session with detected symptoms and urgency
    """
    database = get_database()
    
    update_data = {"updated_at": datetime.now()}
    if symptoms:
        update_data["symptoms"] = symptoms
    if urgency_level:
        update_data["urgency_level"] = urgency_level
    
    await database.sessions.update_one(
        {"session_id": session_id},
        {"$set": update_data}
    )

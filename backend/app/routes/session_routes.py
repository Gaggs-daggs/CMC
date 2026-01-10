"""
Session Management Routes
API endpoints for managing user conversation sessions

Features:
- List all sessions for a user
- Create new session
- Get session details with messages
- Switch between sessions
- Delete/archive sessions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["sessions"])

# In-memory session storage (should be replaced with database in production)
# Structure: { user_phone: { session_id: session_data } }
user_sessions: Dict[str, Dict[str, Dict[str, Any]]] = {}


class SessionSummary(BaseModel):
    """Summary of a session for sidebar display"""
    session_id: str
    title: str  # First message or auto-generated title
    created_at: datetime
    updated_at: datetime
    message_count: int
    last_message_preview: Optional[str] = None
    symptoms: List[str] = []
    urgency_level: str = "self_care"


class SessionDetail(BaseModel):
    """Full session with messages"""
    session_id: str
    user_phone: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[Dict[str, Any]]
    symptoms: List[str] = []
    urgency_level: str = "self_care"
    language: str = "en"


class CreateSessionRequest(BaseModel):
    user_phone: str
    language: str = "en"
    title: Optional[str] = None


class CreateSessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: datetime


class ListSessionsRequest(BaseModel):
    user_phone: str


class UpdateSessionRequest(BaseModel):
    title: Optional[str] = None
    is_archived: Optional[bool] = None


class AddMessageRequest(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    metadata: Optional[Dict[str, Any]] = None


def get_user_sessions(phone: str) -> Dict[str, Dict[str, Any]]:
    """Get all sessions for a user"""
    if phone not in user_sessions:
        user_sessions[phone] = {}
    return user_sessions[phone]


def generate_session_title(messages: List[Dict]) -> str:
    """Generate a title from the first user message"""
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            # Take first 50 chars or first sentence
            if len(content) > 50:
                return content[:47] + "..."
            return content or "New Chat"
    return "New Chat"


@router.post("/list", response_model=List[SessionSummary])
async def list_sessions(request: ListSessionsRequest):
    """
    List all sessions for a user (for sidebar)
    Returns sessions sorted by last updated (most recent first)
    """
    sessions = get_user_sessions(request.user_phone)
    
    summaries = []
    for session_id, session_data in sessions.items():
        if session_data.get("is_archived", False):
            continue  # Skip archived sessions
            
        messages = session_data.get("messages", [])
        last_message = messages[-1] if messages else None
        
        summaries.append(SessionSummary(
            session_id=session_id,
            title=session_data.get("title", generate_session_title(messages)),
            created_at=session_data.get("created_at", datetime.now()),
            updated_at=session_data.get("updated_at", datetime.now()),
            message_count=len(messages),
            last_message_preview=last_message.get("content", "")[:100] if last_message else None,
            symptoms=session_data.get("symptoms", []),
            urgency_level=session_data.get("urgency_level", "self_care")
        ))
    
    # Sort by updated_at descending
    summaries.sort(key=lambda x: x.updated_at, reverse=True)
    
    return summaries


@router.post("/create", response_model=CreateSessionResponse)
async def create_session(request: CreateSessionRequest):
    """
    Create a new conversation session
    """
    session_id = str(uuid.uuid4())
    now = datetime.now()
    
    sessions = get_user_sessions(request.user_phone)
    
    sessions[session_id] = {
        "session_id": session_id,
        "user_phone": request.user_phone,
        "title": request.title or "New Chat",
        "created_at": now,
        "updated_at": now,
        "messages": [],
        "symptoms": [],
        "urgency_level": "self_care",
        "language": request.language,
        "is_archived": False
    }
    
    logger.info(f"Created new session {session_id} for user {request.user_phone}")
    
    return CreateSessionResponse(
        session_id=session_id,
        title=sessions[session_id]["title"],
        created_at=now
    )


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str, user_phone: str):
    """
    Get full session details including all messages
    """
    sessions = get_user_sessions(user_phone)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_data = sessions[session_id]
    
    return SessionDetail(
        session_id=session_id,
        user_phone=user_phone,
        title=session_data.get("title", "Chat"),
        created_at=session_data.get("created_at", datetime.now()),
        updated_at=session_data.get("updated_at", datetime.now()),
        messages=session_data.get("messages", []),
        symptoms=session_data.get("symptoms", []),
        urgency_level=session_data.get("urgency_level", "self_care"),
        language=session_data.get("language", "en")
    )


@router.put("/{session_id}")
async def update_session(session_id: str, user_phone: str, request: UpdateSessionRequest):
    """
    Update session (title, archive status)
    """
    sessions = get_user_sessions(user_phone)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if request.title is not None:
        sessions[session_id]["title"] = request.title
    
    if request.is_archived is not None:
        sessions[session_id]["is_archived"] = request.is_archived
    
    sessions[session_id]["updated_at"] = datetime.now()
    
    return {"status": "updated", "session_id": session_id}


@router.delete("/{session_id}")
async def delete_session(session_id: str, user_phone: str):
    """
    Delete a session (or archive it)
    """
    sessions = get_user_sessions(user_phone)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Archive instead of delete (for safety)
    sessions[session_id]["is_archived"] = True
    sessions[session_id]["updated_at"] = datetime.now()
    
    logger.info(f"Archived session {session_id}")
    
    return {"status": "archived", "session_id": session_id}


@router.post("/{session_id}/message")
async def add_message(session_id: str, user_phone: str, request: AddMessageRequest):
    """
    Add a message to a session (used internally)
    """
    sessions = get_user_sessions(user_phone)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    message = {
        "role": request.role,
        "content": request.content,
        "timestamp": datetime.now().isoformat(),
        "metadata": request.metadata or {}
    }
    
    sessions[session_id]["messages"].append(message)
    sessions[session_id]["updated_at"] = datetime.now()
    
    # Auto-update title if it's still "New Chat" and this is the first user message
    if sessions[session_id]["title"] == "New Chat" and request.role == "user":
        sessions[session_id]["title"] = generate_session_title(sessions[session_id]["messages"])
    
    return {"status": "added", "message_count": len(sessions[session_id]["messages"])}


@router.post("/{session_id}/symptoms")
async def update_symptoms(session_id: str, user_phone: str, symptoms: List[str]):
    """
    Update symptoms for a session
    """
    sessions = get_user_sessions(user_phone)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Merge symptoms without duplicates
    existing = set(sessions[session_id].get("symptoms", []))
    existing.update(symptoms)
    sessions[session_id]["symptoms"] = list(existing)
    sessions[session_id]["updated_at"] = datetime.now()
    
    return {"status": "updated", "symptoms": sessions[session_id]["symptoms"]}


# Import this in main.py and add to app
def get_or_create_session(user_phone: str, language: str = "en") -> str:
    """
    Get the most recent session or create a new one
    Used when user doesn't specify a session
    """
    sessions = get_user_sessions(user_phone)
    
    # Find most recent non-archived session
    recent_sessions = [
        (sid, data) for sid, data in sessions.items()
        if not data.get("is_archived", False)
    ]
    
    if recent_sessions:
        # Sort by updated_at and return most recent
        recent_sessions.sort(key=lambda x: x[1].get("updated_at", datetime.min), reverse=True)
        return recent_sessions[0][0]
    
    # Create new session
    session_id = str(uuid.uuid4())
    now = datetime.now()
    
    sessions[session_id] = {
        "session_id": session_id,
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
    
    return session_id


def save_message_to_session(user_phone: str, session_id: str, role: str, content: str, metadata: Dict = None):
    """
    Save a message to a session
    """
    sessions = get_user_sessions(user_phone)
    
    if session_id not in sessions:
        return False
    
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    
    sessions[session_id]["messages"].append(message)
    sessions[session_id]["updated_at"] = datetime.now()
    
    # Auto-update title
    if sessions[session_id]["title"] == "New Chat" and role == "user":
        sessions[session_id]["title"] = generate_session_title(sessions[session_id]["messages"])
    
    return True

"""
PostgreSQL Session Service
Persistent storage for chat sessions and messages using PostgreSQL
"""

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import uuid
import json

from .postgres_config import db_config

logger = logging.getLogger(__name__)

# Additional schema for sessions
SESSIONS_SCHEMA = """
-- ============================================
-- CHAT SESSIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) UNIQUE NOT NULL,
    user_id UUID REFERENCES user_profiles(id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    title VARCHAR(255) DEFAULT 'New Chat',
    language VARCHAR(10) DEFAULT 'en',
    symptoms TEXT[] DEFAULT '{}',
    urgency_level VARCHAR(50) DEFAULT 'self_care',
    is_archived BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_phone ON chat_sessions(phone_number);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON chat_sessions(session_id);

-- ============================================
-- CHAT MESSAGES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(100) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user' or 'assistant'
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_session ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created ON chat_messages(created_at);

-- Trigger to update session updated_at when messages are added
CREATE OR REPLACE FUNCTION update_session_on_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE chat_sessions 
    SET updated_at = CURRENT_TIMESTAMP 
    WHERE session_id = NEW.session_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_update_session_on_message ON chat_messages;
CREATE TRIGGER trigger_update_session_on_message
    AFTER INSERT ON chat_messages
    FOR EACH ROW
    EXECUTE FUNCTION update_session_on_message();
"""


class PostgresSessionService:
    """
    PostgreSQL-based session service for persistent chat storage
    """
    
    def __init__(self):
        self.connection_string = db_config.connection_string
        self._initialized = False
        self._init_schema()
    
    def _get_connection(self):
        """Get a database connection"""
        return psycopg2.connect(
            host=db_config.host,
            port=db_config.port,
            database=db_config.database,
            user=db_config.user,
            password=db_config.password
        )
    
    def _init_schema(self):
        """Initialize sessions schema"""
        if self._initialized:
            return
            
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(SESSIONS_SCHEMA)
            conn.commit()
            cur.close()
            conn.close()
            self._initialized = True
            logger.info("✅ PostgreSQL Session Service initialized")
        except Exception as e:
            logger.error(f"❌ Session schema initialization failed: {e}")
            # Don't raise - allow fallback to in-memory
    
    # ==========================================
    # SESSION CRUD OPERATIONS
    # ==========================================
    
    def create_session(self, phone_number: str, language: str = "en", title: str = "New Chat", session_id: str = None) -> Dict[str, Any]:
        """Create a new chat session"""
        session_id = session_id or str(uuid.uuid4())
        now = datetime.now()
        
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            # Get user_id from phone if exists
            cur.execute(
                "SELECT id FROM user_profiles WHERE phone_number = %s",
                (phone_number,)
            )
            user_row = cur.fetchone()
            user_id = user_row[0] if user_row else None
            
            cur.execute("""
                INSERT INTO chat_sessions (session_id, user_id, phone_number, title, language, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id, session_id, title, created_at
            """, (session_id, user_id, phone_number, title, language, now, now))
            
            result = cur.fetchone()
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"✅ Created session {session_id} for {phone_number}")
            
            return {
                "session_id": session_id,
                "title": title,
                "created_at": now.isoformat(),
                "phone_number": phone_number
            }
        except Exception as e:
            logger.error(f"❌ Failed to create session: {e}")
            raise
    
    def get_session(self, session_id: str, phone_number: str = None) -> Optional[Dict[str, Any]]:
        """Get session with all messages"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get session
            query = "SELECT * FROM chat_sessions WHERE session_id = %s"
            params = [session_id]
            if phone_number:
                query += " AND phone_number = %s"
                params.append(phone_number)
            
            cur.execute(query, params)
            session = cur.fetchone()
            
            if not session:
                cur.close()
                conn.close()
                return None
            
            # Get messages
            cur.execute("""
                SELECT role, content, metadata, created_at 
                FROM chat_messages 
                WHERE session_id = %s 
                ORDER BY created_at ASC
            """, (session_id,))
            messages = cur.fetchall()
            
            cur.close()
            conn.close()
            
            return {
                "session_id": session["session_id"],
                "user_phone": session["phone_number"],
                "title": session["title"],
                "language": session["language"],
                "symptoms": list(session["symptoms"]) if session["symptoms"] else [],
                "urgency_level": session["urgency_level"],
                "created_at": session["created_at"].isoformat() if session["created_at"] else None,
                "updated_at": session["updated_at"].isoformat() if session["updated_at"] else None,
                "messages": [
                    {
                        "role": m["role"],
                        "content": m["content"],
                        "metadata": m["metadata"] or {},
                        "timestamp": m["created_at"].isoformat() if m["created_at"] else None
                    }
                    for m in messages
                ]
            }
        except Exception as e:
            logger.error(f"❌ Failed to get session: {e}")
            return None
    
    def list_sessions(self, phone_number: str, include_archived: bool = False) -> List[Dict[str, Any]]:
        """List all sessions for a user"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            query = """
                SELECT s.*, 
                       (SELECT COUNT(*) FROM chat_messages WHERE session_id = s.session_id) as message_count,
                       (SELECT content FROM chat_messages WHERE session_id = s.session_id ORDER BY created_at DESC LIMIT 1) as last_message
                FROM chat_sessions s
                WHERE s.phone_number = %s
            """
            if not include_archived:
                query += " AND s.is_archived = false"
            query += " ORDER BY s.updated_at DESC"
            
            cur.execute(query, (phone_number,))
            sessions = cur.fetchall()
            cur.close()
            conn.close()
            
            result = []
            for s in sessions:
                symptoms = list(s["symptoms"]) if s["symptoms"] else []
                symptom_summary = ", ".join(symptoms[:3]) if symptoms else None
                if symptoms and len(symptoms) > 3:
                    symptom_summary += f" +{len(symptoms) - 3} more"
                
                result.append({
                    "session_id": s["session_id"],
                    "title": s["title"],
                    "created_at": s["created_at"].isoformat() if s["created_at"] else None,
                    "updated_at": s["updated_at"].isoformat() if s["updated_at"] else None,
                    "message_count": s["message_count"],
                    "last_message_preview": s["last_message"][:100] if s["last_message"] else None,
                    "symptom_summary": symptom_summary,
                    "symptoms": symptoms,
                    "urgency_level": s["urgency_level"]
                })
            
            return result
        except Exception as e:
            logger.error(f"❌ Failed to list sessions: {e}")
            return []
    
    def update_session_title(self, session_id: str, title: str, phone_number: str = None) -> bool:
        """Update session title"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            query = "UPDATE chat_sessions SET title = %s, updated_at = %s WHERE session_id = %s"
            params = [title, datetime.now(), session_id]
            if phone_number:
                query = "UPDATE chat_sessions SET title = %s, updated_at = %s WHERE session_id = %s AND phone_number = %s"
                params.append(phone_number)
            
            cur.execute(query, params)
            updated = cur.rowcount > 0
            conn.commit()
            cur.close()
            conn.close()
            
            return updated
        except Exception as e:
            logger.error(f"❌ Failed to update session title: {e}")
            return False
    
    def archive_session(self, session_id: str, phone_number: str = None) -> bool:
        """Archive (soft delete) a session"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            query = "UPDATE chat_sessions SET is_archived = true, updated_at = %s WHERE session_id = %s"
            params = [datetime.now(), session_id]
            if phone_number:
                query += " AND phone_number = %s"
                params.append(phone_number)
            
            cur.execute(query, params)
            archived = cur.rowcount > 0
            conn.commit()
            cur.close()
            conn.close()
            
            logger.info(f"📦 Archived session {session_id}")
            return archived
        except Exception as e:
            logger.error(f"❌ Failed to archive session: {e}")
            return False
    
    # ==========================================
    # MESSAGE OPERATIONS
    # ==========================================
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Dict = None) -> bool:
        """Add a message to a session"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO chat_messages (session_id, role, content, metadata, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (session_id, role, content, Json(metadata or {}), datetime.now()))
            
            # Auto-update title from first user message
            if role == "user":
                cur.execute(
                    "SELECT title FROM chat_sessions WHERE session_id = %s",
                    (session_id,)
                )
                current = cur.fetchone()
                if current and current[0] == "New Chat":
                    new_title = content[:50] + "..." if len(content) > 50 else content
                    cur.execute(
                        "UPDATE chat_sessions SET title = %s WHERE session_id = %s",
                        (new_title, session_id)
                    )
            
            conn.commit()
            cur.close()
            conn.close()
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to add message: {e}")
            return False
    
    def update_session_symptoms(self, session_id: str, symptoms: List[str], urgency_level: str = None) -> bool:
        """Update session symptoms and urgency"""
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            
            if urgency_level:
                cur.execute("""
                    UPDATE chat_sessions 
                    SET symptoms = %s, urgency_level = %s, updated_at = %s 
                    WHERE session_id = %s
                """, (symptoms, urgency_level, datetime.now(), session_id))
            else:
                cur.execute("""
                    UPDATE chat_sessions 
                    SET symptoms = %s, updated_at = %s 
                    WHERE session_id = %s
                """, (symptoms, datetime.now(), session_id))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update symptoms: {e}")
            return False
    
    def generate_smart_title(self, session_id: str) -> str:
        """Generate a smart title based on symptoms/first message"""
        try:
            conn = self._get_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get session symptoms
            cur.execute(
                "SELECT symptoms FROM chat_sessions WHERE session_id = %s",
                (session_id,)
            )
            session = cur.fetchone()
            
            if session and session["symptoms"]:
                symptoms = list(session["symptoms"])
                if symptoms:
                    # Create title from symptoms
                    if len(symptoms) == 1:
                        title = f"{symptoms[0].title()} consultation"
                    elif len(symptoms) == 2:
                        title = f"{symptoms[0].title()} & {symptoms[1].title()}"
                    else:
                        title = f"{symptoms[0].title()}, {symptoms[1].title()} +{len(symptoms)-2}"
                    
                    cur.execute(
                        "UPDATE chat_sessions SET title = %s WHERE session_id = %s",
                        (title, session_id)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    return title
            
            # Fallback to first message
            cur.execute("""
                SELECT content FROM chat_messages 
                WHERE session_id = %s AND role = 'user'
                ORDER BY created_at ASC LIMIT 1
            """, (session_id,))
            
            msg = cur.fetchone()
            if msg:
                content = msg["content"]
                title = content[:50] + "..." if len(content) > 50 else content
                cur.execute(
                    "UPDATE chat_sessions SET title = %s WHERE session_id = %s",
                    (title, session_id)
                )
                conn.commit()
            
            cur.close()
            conn.close()
            
            return title if msg else "Health Consultation"
        except Exception as e:
            logger.error(f"❌ Failed to generate title: {e}")
            return "Health Consultation"


# Global instance
postgres_session_service = PostgresSessionService()

import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict
from fastapi import WebSocket

from sqlmodel import select

from src.chat.models import ChatSession, MessageType, ChatMessage
from src.database import Session

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_session(self, user_id: Optional[str] = None) -> ChatSession:
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            session_id=session_id,
            user_id=user_id,
            title="New Chat"
        )
        self.db.add(chat_session)
        self.db.commit()
        self.db.refresh(chat_session)
        return chat_session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self.db.exec(
            select(ChatSession).where(ChatSession.session_id == session_id)
        ).first()

    def save_message(self, session_id: str, message_type: MessageType, content: str) -> ChatMessage:
        message = ChatMessage(
            session_id=session_id,
            message_type=message_type,
            content=content
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)

        session = self.get_session(session_id)
        if session:
            session.updated_at = datetime.utcnow()
            self.db.add(session)
            self.db.commit()

        return message

    def get_chat_history(self, session_id: str, limit: int = 50) -> List[ChatMessage]:
        return self.db.exec(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp.desc())
            .limit(limit)
        ).all()[::-1]

    def get_user_sessions(self, user_id: str) -> List[ChatSession]:
        return self.db.exec(
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .where(ChatSession.is_active == True)
            .order_by(ChatSession.updated_at.desc())
        ).all()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, str] = {}

    async def connect(self, websocket: WebSocket, session_id: str) -> str:
        await websocket.accept()
        user_id = str(uuid.uuid4())
        self.active_connections[user_id] = websocket
        self.session_connections[session_id] = user_id
        return user_id

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

        session_to_remove = None
        for session_id, uid in self.session_connections.items():
            if uid == user_id:
                session_to_remove = session_id
                break
        if session_to_remove:
            del self.session_connections[session_to_remove]

    async def send_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(json.dumps(message))

manager = ConnectionManager()


class AIAssistant:
    def __init__(self):
        pass

    async def get_response(self, message: str, chat_history: List[ChatMessage]) -> str:
        # TODO: implement a more sophisticated AI response generation

        # Simple context-aware response based on history
        history_text = " ".join([msg.content for msg in chat_history[-3:]])

        responses = [
            f"That's interesting! Based on our conversation, I can see you're asking about: '{message}'",
            f"I understand. Let me help you with that question: '{message}'",
            f"Thanks for sharing! Regarding '{message}', here's what I think...",
            f"Great question about '{message}'. Let me provide some insights...",
        ]
        import random
        return random.choice(responses)

ai_assistant = AIAssistant()
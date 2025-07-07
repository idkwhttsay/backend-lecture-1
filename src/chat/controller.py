from fastapi import WebSocket, WebSocketDisconnect, Depends, APIRouter
from sqlalchemy.sql.annotation import Annotated
import json
from datetime import datetime

from src.auth.models import User
from src.auth.service import get_current_active_user
from src.chat.models import MessageType
from src.chat.service import ChatService, manager, ai_assistant
from src.database import SessionDep
from src.main import app

router = APIRouter(prefix="/chat", tags=["chat"])

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, db: SessionDep):
    chat_service = ChatService(db)

    # Get or create chat session
    chat_session = chat_service.get_session(session_id)
    if not chat_session:
        chat_session = chat_service.create_session()
        session_id = chat_session.session_id

    user_id = await manager.connect(websocket, session_id)

    # Load and send chat history
    chat_history = chat_service.get_chat_history(session_id)
    for msg in chat_history:
        history_msg = {
            "type": msg.message_type.value,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat(),
            "session_id": session_id
        }
        await manager.send_message(user_id, history_msg)

    # Send welcome message if new session
    if not chat_history:
        welcome_msg = {
            "type": "system",
            "content": f"Connected to AI Assistant! Session: {session_id}",
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id
        }
        await manager.send_message(user_id, welcome_msg)
        chat_service.save_message(session_id, MessageType.SYSTEM, welcome_msg["content"])

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if "content" not in message_data:
                error_msg = {
                    "type": "error",
                    "content": "Invalid message format",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await manager.send_message(user_id, error_msg)
                continue

            user_message = message_data["content"].strip()
            if not user_message:
                continue

            # Save user message to database
            user_msg_db = chat_service.save_message(session_id, MessageType.USER, user_message)

            # Send user message back to client
            user_msg = {
                "type": "user",
                "content": user_message,
                "timestamp": user_msg_db.timestamp.isoformat(),
                "session_id": session_id
            }
            await manager.send_message(user_id, user_msg)

            # Send typing indicator
            typing_msg = {
                "type": "typing",
                "content": "AI is thinking...",
                "timestamp": datetime.utcnow().isoformat()
            }
            await manager.send_message(user_id, typing_msg)

            # Get AI response with chat history
            recent_history = chat_service.get_chat_history(session_id, limit=10)
            ai_response = await ai_assistant.get_response(user_message, recent_history)

            # Save AI response to database
            ai_msg_db = chat_service.save_message(session_id, MessageType.ASSISTANT, ai_response)

            # Send AI response
            ai_msg = {
                "type": "assistant",
                "content": ai_response,
                "timestamp": ai_msg_db.timestamp.isoformat(),
                "session_id": session_id
            }
            await manager.send_message(user_id, ai_msg)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"User {user_id} disconnected from session {session_id}")
    except Exception as e:
        print(f"Error in websocket connection: {e}")
        manager.disconnect(user_id)


@app.get("/api/sessions/{user_id}")
async def get_user_sessions(user: Annotated[User, Depends(get_current_active_user)], db: SessionDep):
    """Get all chat sessions for a user"""
    chat_service = ChatService(db)
    sessions = chat_service.get_user_sessions(user.id)
    return {"sessions": sessions}


@app.post("/api/sessions")
async def create_new_session( db: SessionDep, user: Annotated[User, Depends(get_current_active_user)]):
    """Create a new chat session"""
    chat_service = ChatService(db)
    session = chat_service.create_session(user.id)
    return {"session": session}


@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, db: SessionDep):
    """Get all messages for a session"""
    chat_service = ChatService(db)
    messages = chat_service.get_chat_history(session_id)
    return {"messages": messages}

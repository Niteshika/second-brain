from fastapi import APIRouter, HTTPException, Depends
from app.models.chat import ChatRequest, ChatResponse
from app.core.rag_chain import ask
from app.core.security import get_current_user
from app.core.models_db import ChatMessage
from langchain_core.messages import HumanMessage, AIMessage
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter()

def load_chat_history(user_id: int, db: Session) -> list:
    data = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(ChatMessage.created_at).all()
    chat_history = []
    for row in data:
        if row.role == "human":
            chat_history.append(HumanMessage(content = row.content))
        else:
            chat_history.append(AIMessage(content = row.content))

    return chat_history

@router.post("", response_model = ChatResponse)
def chat(request: ChatRequest, current_user = Depends(get_current_user), db: Session = Depends(get_db)) -> ChatResponse:
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")
    
    db.add(ChatMessage(user_id = current_user.id, role = "human", content = request.message))
    history = load_chat_history(user_id= current_user.id, db = db)
    answer, sources, updated_history = ask(request.message, chat_history= history)
    db.add(ChatMessage(user_id = current_user.id, role = "ai", content = answer))
    db.commit()
    return ChatResponse(answer=answer)
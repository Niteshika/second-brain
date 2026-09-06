from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.models.chat import ChatRequest
from app.core.rag_chain import ask_streaming
from app.core.security import get_current_user
from app.core.models_db import ChatMessage
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.routers.chat import load_chat_history

router = APIRouter()

@router.post("/stream")
def chat_stream(request: ChatRequest, current_user = Depends(get_current_user), db:Session=Depends(get_db)):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="message cannot be empty")
    
    history = load_chat_history(user_id= current_user.id, db = db)

    def event_generator():
        full_answer = ""
        for chunk in ask_streaming(request.message, chat_history = history):
            full_answer+=chunk
            yield chunk

        db.add(ChatMessage(user_id = current_user.id, role = "human", content = request.message))
        db.add(ChatMessage(user_id = current_user.id, role = "ai", content = full_answer))
        db.commit()
        

   
    return StreamingResponse(event_generator(), media_type="text/plain") 
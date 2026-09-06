from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, health, auth, knowledge_gap, chat_stream
from app.core.database import engine, Base
from app.core import models_db

app = FastAPI(title="Second Brain")

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

app.include_router(health.router)
app.include_router(chat.router, prefix="/chat")
app.include_router(auth.router, tags=["auth"])
app.include_router(knowledge_gap.router, prefix="/knowledge-gap")
app.include_router(chat_stream.router, prefix="/chat")
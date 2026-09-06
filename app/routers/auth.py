from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models_db import User
from app.core.security import hash_password, verify_password, create_access_token
from app.models.auth import UserSignup, UserResponse, UserLogin

router = APIRouter()

@router.post("/signup", response_model = UserResponse)
def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if(existing_user):
        raise HTTPException(status_code=400, detail = "Email already registered")
    email = user_data.email
    hashed_password = hash_password(user_data.password)
    new_user = User(email = email, hashed_password = hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user_data: UserLogin, db: Session=Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if not existing_user:
        raise HTTPException(status_code = 401, detail = "Invalid credentials")
    
    password_check = verify_password(plain_password = user_data.password, hashed_password = existing_user.hashed_password)
    if not password_check:
        raise HTTPException(status_code = 401, detail = "Invalid password")
    
    token = create_access_token(data = {"sub": existing_user.email})
    return {"access_token": token, "token_type": "bearer"}
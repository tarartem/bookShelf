import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from fastapi.security import OAuth2PasswordBearer
from backend.models import User, CreditTransaction
from backend.schemas import (
    UserCreate, UserResponse, UserLogin, Token, 
    PasswordResetRequest, PasswordResetConfirm, NotificationUpdate, CreditTransactionResponse
)
from backend.services.auth_service import (
    hash_password, verify_password, create_access_token, 
    create_verification_token, decode_token, create_reset_token
)
from backend.services.email_service import send_verification_email, send_reset_email

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        is_verified=False,
        credits=3 # Initial credits
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Send verification email
    token = create_verification_token(user.email)
    send_verification_email(user.email, token)
    
    return new_user

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not db_user.is_verified:
        raise HTTPException(status_code=401, detail="Please verify your email first")
        
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/verify/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    email = decode_token(token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_verified = True
    db.commit()
    return {"message": "Email verified successfully"}

@router.post("/forgot-password")
def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        token = create_reset_token(user.email)
        send_reset_email(user.email, token)
    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/reset-password")
def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    email = decode_token(request.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.hashed_password = hash_password(request.new_password)
    db.commit()
    return {"message": "Password reset successfully"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.delete("/me")
def delete_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted"}

@router.post("/notifications", response_model=UserResponse)
def update_notifications(
    update: NotificationUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    current_user.email_notifications = update.enabled
    
    # Award one-time bonus if enabling for the first time
    if update.enabled and not current_user.received_notif_bonus:
        bonus = 10
        current_user.credits += bonus
        current_user.received_notif_bonus = True
        
        # Record transaction
        transaction = CreditTransaction(
            user_id=current_user.id,
            amount=bonus,
            reason="Бонус за підписку на сповіщення"
        )
        db.add(transaction)
        
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/transactions", response_model=List[CreditTransactionResponse])
def get_my_transactions(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    return db.query(CreditTransaction).filter(CreditTransaction.user_id == current_user.id).order_by(CreditTransaction.created_at.desc()).all()

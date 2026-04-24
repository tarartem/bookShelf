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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login") # Standardized

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Користувач з такою електронною поштою вже існує."
        )
    
    # Create new user
    hashed_pwd = hash_password(user_in.password)
    new_user = User(
        email=user_in.email,
        password_hash=hashed_pwd,
        is_verified=False,
        role="user"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Record initial credits transaction
    # Explicitly use 3 if new_user.credits is None to prevent NOT NULL constraint error
    initial_credits = new_user.credits if new_user.credits is not None else 3
    initial_tx = CreditTransaction(
        user_id=new_user.id,
        amount=initial_credits,
        reason="Вітальний бонус при реєстрації"
    )
    db.add(initial_tx)
    try:
        db.commit()
        print(f"DEBUG: Initial transaction created for {new_user.email}")
    except Exception as e:
        print(f"ERROR: Failed to create initial transaction: {e}")
        db.rollback()
    
    print(f"DEBUG: User created: {new_user.email} (ID: {new_user.id})")
    
    # Send verification email
    token = create_verification_token(new_user.email)
    try:
        send_verification_email(new_user.email, token)
    except Exception as e:
        base = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
        print(f"\n\n==========================================================")
        print(f"📧 [DEV MODE] EMAIL SIMULATION FOR: {new_user.email}")
        print(f"Here is your Account Verification Link to continue testing:")
        print(f"{base}/verify.html?token={token}")
        print(f"==========================================================\n\n")
    
    return new_user

@router.get("/verify")
def verify_email(token: str, db: Session = Depends(get_db)):
    payload = decode_token(token)
    if not payload or payload.get("type") != "verification":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Недійсний або застарілий токен."
        )
    
    email = payload.get("sub")
    print(f"DEBUG: Attempting verification for email: {email}")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"DEBUG: User NOT found in database for email: {email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача {email} не знайдено."
        )
    
    if user.is_verified:
        return {"message": "Account already verified."}
    
    user.is_verified = True
    db.commit()
    print(f"DEBUG: User {email} verified successfully.")
    
    return {"message": "Account successfully verified."}

@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if user:
        token = create_reset_token(user.email)
        try:
            send_reset_email(user.email, token)
        except Exception as e:
            base = os.getenv("BASE_URL", "http://localhost:8000").rstrip("/")
            print(f"\n\n==========================================================")
            print(f"📧 [DEV MODE] EMAIL SIMULATION FOR: {user.email}")
            print(f"Could not send real email because SMTP is not configured.")
            print(f"Here is your Password Reset Link to continue testing:")
            print(f"{base}/reset-password.html?token={token}")
            print(f"==========================================================\n\n")
    
    return {"message": "If an account exists with that email, a reset link has been sent."}

@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    payload = decode_token(request.token)
    if not payload or payload.get("type") != "reset":
        raise HTTPException(status_code=400, detail="Недійсний або застарілий токен відновлення.")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено.")
    
    user.password_hash = hash_password(request.new_password)
    db.commit()
    return {"message": "Password updated successfully. You can now login."}

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невірна електронна пошта або пароль.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Будь ласка, підтвердіть електронну пошту перед входом."
        )
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from backend.models import Book
    db.query(Book).filter(Book.uploaded_by == current_user.id).delete()
    db.delete(current_user)
    db.commit()
    return None

@router.post("/notifications", response_model=UserResponse)
def update_notifications(
    update: NotificationUpdate, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    current_user.email_notifications = update.enabled
    if update.enabled and not current_user.received_notif_bonus:
        bonus = 10
        current_user.credits += bonus
        current_user.received_notif_bonus = True
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

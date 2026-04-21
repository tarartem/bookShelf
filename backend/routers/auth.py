from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from fastapi.security import OAuth2PasswordBearer
from backend.models import User
from backend.schemas import (
    UserCreate, UserResponse, UserLogin, Token, 
    PasswordResetRequest, PasswordResetConfirm
)
from backend.services.auth_service import (
    hash_password, verify_password, create_access_token, 
    create_verification_token, decode_token, create_reset_token
)
from backend.services.email_service import send_verification_email, send_reset_email

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login_form") # For swagger

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists."
        )
    
    # Create new user
    hashed_pwd = hash_password(user_in.password)
    new_user = User(
        email=user_in.email,
        hashed_password=hashed_pwd,
        is_verified=False,
        role="user"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
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
            detail="Invalid or expired token."
        )
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    if user.is_verified:
        return {"message": "Account already verified."}
    
    user.is_verified = True
    db.commit()
    
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
            import os
            print(f"\n\n==========================================================")
            print(f"📧 [DEV MODE] EMAIL SIMULATION FOR: {user.email}")
            print(f"Could not send real email because SMTP is not configured.")
            print(f"Here is your Password Reset Link to continue testing:")
            print(f"{base}/reset-password.html?token={token}")
            print(f"==========================================================\n\n")
    
    # Always return 200 for security
    return {"message": "If an account exists with that email, a reset link has been sent."}

@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    payload = decode_token(request.token)
    if not payload or payload.get("type") != "reset":
        raise HTTPException(status_code=400, detail="Invalid or expired reset token.")
    
    email = payload.get("sub")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    
    user.hashed_password = hash_password(request.new_password)
    db.commit()
    return {"message": "Password updated successfully. You can now login."}

@router.post("/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in."
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
    # Delete associated books first to avoid foreign key issues
    from backend.models import Book
    db.query(Book).filter(Book.owner_id == current_user.id).delete()
    
    db.delete(current_user)
    db.commit()
    return None

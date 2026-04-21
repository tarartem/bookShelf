from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: Optional[str] = None
    description: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    epub_filepath: str
    cover_filepath: Optional[str] = None
    file_hash: Optional[str] = None
    status: str
    owner_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_verified: bool
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class BookSendRequest(BaseModel):
    email: EmailStr

class FeedbackCreate(BaseModel):
    message: str

class FeedbackResponse(BaseModel):
    id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True

class BookStats(BaseModel):
    book_id: int
    title: str
    total_sends: int
    unique_users: int

class AdminStatsResponse(BaseModel):
    total_books: int
    total_sends: int
    books_stats: List[BookStats]

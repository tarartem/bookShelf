from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    epub_filepath: str
    cover_filepath: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class BookSendRequest(BaseModel):
    email: EmailStr

class FeedbackCreate(BaseModel):
    message: str

class FeedbackResponse(BaseModel):
    id: int
    message: str
    created_at: datetime

    class Config:
        orm_mode = True
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

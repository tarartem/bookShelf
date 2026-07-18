from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    created_at = Column(DateTime, server_default=func.now())
    is_verified = Column(Boolean, default=False)
    
    # Economics
    credits = Column(Integer, default=3)
    email_notifications = Column(Boolean, default=False)
    received_notif_bonus = Column(Boolean, default=False)

    books_uploaded = relationship("Book", back_populates="uploader")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True)
    description = Column(Text)
    cover_filepath = Column(String)
    epub_filepath = Column(String, nullable=False)
    file_hash = Column(String, index=True, unique=True) # SHA-256 hash for deduplication
    
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="pending") # pending, approved, rejected
    moderation_notes = Column(Text) # Internal AI/Admin notes on why book was rejected/approved
    created_at = Column(DateTime, server_default=func.now())

    uploader = relationship("User", back_populates="books_uploaded")


class BookSendLog(Base):
    __tablename__ = "book_send_logs"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Who requested it
    email = Column(String, nullable=False)
    sent_at = Column(DateTime, server_default=func.now())

    book = relationship("Book")

class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False) # Positive for gain, negative for loss
    reason = Column(String, nullable=False) # e.g., "contribution_approval", "book_request", "notif_bonus", "admin_adjustment"
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User")

class UserLibrary(Base):
    __tablename__ = "user_library"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    unlocked_at = Column(DateTime, server_default=func.now())

    user = relationship("User")
    book = relationship("Book")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
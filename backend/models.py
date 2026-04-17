from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=True)
    description = Column(Text, nullable=True)
    epub_filepath = Column(String, nullable=False)
    cover_filepath = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    send_logs = relationship("BookSendLog", back_populates="book", cascade="all, delete-orphan")


class BookSendLog(Base):
    __tablename__ = "book_send_logs"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    email = Column(String, index=True, nullable=False)
    sent_at = Column(DateTime, server_default=func.now())

    book = relationship("Book", back_populates="send_logs")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

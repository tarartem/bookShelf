from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from backend.database import get_db
from backend.models import Book, BookSendLog
from backend.schemas import BookResponse, BookSendRequest, BookStats
from backend.services.email_service import send_epub_email
from email_validator import validate_email, EmailNotValidError

router = APIRouter()

@router.get("", response_model=List[BookResponse])
def get_books(search: str = "", db: Session = Depends(get_db)):
    query = db.query(Book)
    if search:
        query = query.filter(func.lower(Book.title).contains(search.lower()))
    return query.all()

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.get("/{book_id}/stats", response_model=BookStats)
def get_book_stats(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    total_sends = db.query(BookSendLog).filter(BookSendLog.book_id == book_id).count()
    unique_users = db.query(func.count(func.distinct(BookSendLog.email))).filter(BookSendLog.book_id == book_id).scalar()
    
    return BookStats(
        book_id=book_id,
        title=book.title,
        total_sends=total_sends,
        unique_users=unique_users or 0
    )


def send_book_task(email: str, title: str, author: str, path: str):
    send_epub_email(email, title, author, path)


@router.post("/{book_id}/send")
def send_book(book_id: int, request: BookSendRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Validate Email rigorously
    try:
        valid = validate_email(request.email, check_deliverability=True)
        email = valid.normalized
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Record log
    log = BookSendLog(book_id=book.id, email=email)
    db.add(log)
    db.commit()

    # Background send process
    background_tasks.add_task(send_book_task, email, book.title, book.author, book.epub_filepath)

    return {"message": "Book queued for sending. You should receive it shortly."}

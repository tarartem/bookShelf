from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import os
import hashlib

from backend.database import get_db
from backend.models import Book, BookSendLog, CreditTransaction
from backend.schemas import BookResponse, BookSendRequest, BookStats, CreditTransactionResponse
from backend.services.email_service import send_epub_email
from backend.services.epub_service import extract_epub_metadata
from backend.routers.auth import get_current_user
from backend.routers.admin import get_current_admin
from fastapi.responses import FileResponse
from email_validator import validate_email, EmailNotValidError

router = APIRouter()

@router.get("", response_model=List[BookResponse])
def get_books(search: str = "", db: Session = Depends(get_db)):
    query = db.query(Book).filter(Book.status == "approved")
    if search:
        query = query.filter(func.lower(Book.title).contains(search.lower()))
    return query.all()

@router.get("/my", response_model=List[BookResponse])
def get_my_books(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return db.query(Book).filter(Book.owner_id == current_user.id).all()

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
def send_book(
    book_id: int, 
    request: BookSendRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Check credits
    if current_user.credits <= 0:
        raise HTTPException(
            status_code=403, 
            detail="У вас закінчилися кредити. Завантажте власну книгу, щоб отримати більше!"
        )

    # Validate Email
    try:
        valid = validate_email(request.email, check_deliverability=False)
        email = valid.normalized
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))

    book = db.query(Book).filter(Book.id == book_id, Book.status == "approved").first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Record log
    log = BookSendLog(book_id=book.id, email=email, user_id=current_user.id)
    db.add(log)
    
    # Deduct credit
    current_user.credits -= 1
    
    # Record transaction
    transaction = CreditTransaction(
        user_id=current_user.id,
        amount=-1,
        reason=f"Запит книги: {book.title}"
    )
    db.add(transaction)
    
    db.commit()

    # Background send process
    background_tasks.add_task(send_book_task, email, book.title, book.author, book.epub_filepath)

    return {
        "message": "Book queued for sending.",
        "credits_remaining": current_user.credits
    }

@router.post("/upload", response_model=BookResponse)
async def upload_book(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not file.filename.endswith(".epub"):
        raise HTTPException(status_code=400, detail="Only EPUB files are allowed.")

    os.makedirs("uploads/books", exist_ok=True)
    
    # Read file content for hashing
    content = await file.read()
    file_hash = hashlib.md5(content).hexdigest()

    # Check for duplicates
    existing = db.query(Book).filter(Book.file_hash == file_hash).first()
    if existing:
        raise HTTPException(status_code=400, detail="This book already exists in our library.")

    # Save file
    file_path = f"uploads/books/{file_hash}.epub"
    with open(file_path, "wb") as f:
        f.write(content)

    # Extract metadata
    title, author, cover_path = extract_epub_metadata(file_path)
    
    # Create DB entry
    new_book = Book(
        title=title or file.filename.replace(".epub", ""),
        author=author or "Unknown",
        epub_filepath=file_path,
        cover_filepath=cover_path,
        file_hash=file_hash,
        status="pending",
        owner_id=current_user.id
    )
    
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    return new_book

@router.get("/download/{book_id}")
def download_book_for_review(
    book_id: int,
    db: Session = Depends(get_db),
    admin: str = Depends(get_current_admin)
):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if not os.path.exists(book.epub_filepath):
        raise HTTPException(status_code=404, detail="EPUB file missing on server")
        
    return FileResponse(
        path=book.epub_filepath, 
        filename=os.path.basename(book.epub_filepath),
        media_type='application/epub+zip'
    )

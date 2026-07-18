import os
import shutil
import logging

logger = logging.getLogger(__name__)
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import hashlib

from backend.database import get_db
from backend.models import Book, BookSendLog, CreditTransaction, UserLibrary
from backend.schemas import BookResponse, BookSendRequest, BookStats, CreditTransactionResponse
from backend.services.email_service import send_epub_email
from backend.services.epub_service import extract_epub_metadata
from backend.services.moderation_service import check_ukrainian_language, check_semantic_alignment
from backend.services.credit_service import award_upload_credits
from backend.routers.auth import get_current_user
from backend.routers.admin import get_current_admin
from email_validator import validate_email, EmailNotValidError

router = APIRouter()

UPLOAD_DIR = "uploads/books"
COVER_DIR = "uploads/covers"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(COVER_DIR, exist_ok=True)

@router.get("/", response_model=List[BookResponse])
def get_books(search: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Book).filter(Book.status == "approved")
    if search:
        search = f"%{search}%"
        query = query.filter((Book.title.ilike(search)) | (Book.author.ilike(search)))
    
    # Removed backend randomization so it doesn't shuffle during search inputs.
    books = query.all()
    return books

@router.get("/my", response_model=List[BookResponse])
def get_my_books(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Book).filter(Book.uploaded_by == current_user.id).all()

@router.get("/pending", response_model=List[BookResponse])
def get_pending_books(db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    return db.query(Book).filter(Book.status == "pending").all()


def send_book_task(email: str, title: str, author: str, path: str):
    send_epub_email(email, title, author, path)


@router.post("/{book_id}/unlock")
def unlock_book(
    book_id: int, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Check if already unlocked
    existing = db.query(UserLibrary).filter(
        UserLibrary.user_id == current_user.id,
        UserLibrary.book_id == book_id
    ).first()
    
    if existing:
        return {"message": "Already unlocked", "credits_remaining": current_user.credits}

    # Check credits
    if current_user.credits <= 0 and current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="У вас закінчилися кредити. Завантажте власну книгу, щоб отримати більше!"
        )

    book = db.query(Book).filter(Book.id == book_id, Book.status == "approved").first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Add to library
    new_unlock = UserLibrary(user_id=current_user.id, book_id=book.id)
    db.add(new_unlock)

    # Deduct credit and log transaction (only for regular users who are NOT the uploader)
    is_uploader = (book.uploaded_by == current_user.id)
    if current_user.role != "admin" and not is_uploader:
        current_user.credits -= 1
        transaction = CreditTransaction(
            user_id=current_user.id,
            amount=-1,
            reason=f"Розблокування книги: {book.title}"
        )
        db.add(transaction)
    
    if is_uploader:
        logger.info(f"User {current_user.id} unlocked their own book '{book.title}' for free.")
    
    db.commit()

    return {
        "message": "Book unlocked successfully.",
        "credits_remaining": current_user.credits
    }

@router.get("/library", response_model=List[BookResponse])
def get_user_library(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Return all books the user has unlocked
    unlocked_books = db.query(Book).join(UserLibrary).filter(UserLibrary.user_id == current_user.id).all()
    return unlocked_books

@router.get("/download/{book_id}/user")
def download_user_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Admins bypass check, otherwise verify unlock
    if current_user.role != "admin":
        unlocked = db.query(UserLibrary).filter(
            UserLibrary.user_id == current_user.id,
            UserLibrary.book_id == book_id
        ).first()
        
        if not unlocked:
            raise HTTPException(status_code=403, detail="You must unlock this book first.")
            
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book or not os.path.exists(book.epub_filepath):
        raise HTTPException(status_code=404, detail="Book not found on server")
        
    return FileResponse(
        path=book.epub_filepath, 
        filename=os.path.basename(book.epub_filepath),
        media_type='application/epub+zip'
    )


@router.post("/{book_id}/send")
def send_book(
    book_id: int, 
    request: BookSendRequest, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # We now enforce unlocking before sending
    if current_user.role != "admin":
        unlocked = db.query(UserLibrary).filter(
            UserLibrary.user_id == current_user.id,
            UserLibrary.book_id == book_id
        ).first()
        
        if not unlocked:
             raise HTTPException(status_code=403, detail="You must unlock this book first before sending.")

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
    db.commit()

    # Background send process
    background_tasks.add_task(send_book_task, email, book.title, book.author, book.epub_filepath)

    return {
        "message": "Book queued for sending.",
        "credits_remaining": current_user.credits
    }

def calculate_file_hash(filepath: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

@router.post("/upload")
async def upload_book(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not file.filename.endswith(".epub"):
        raise HTTPException(status_code=400, detail="Only EPUB files are supported.")

    filepath = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save the file temporarily to compute hash and extract metadata
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 1. Duplicate Detection by Hash
    file_hash = calculate_file_hash(filepath)
    
    existing_book = db.query(Book).filter(Book.file_hash == file_hash).first()
    if existing_book:
        os.remove(filepath) # Clean up
        raise HTTPException(
            status_code=409, 
            detail=f"This exact file already exists in the system as '{existing_book.title}'."
        )

    # 2. Linguistic Verification
    mod_result = check_ukrainian_language(filepath)
    if not mod_result.passed:
        os.remove(filepath)
        # Store internal reason if we were logging to DB, 
        # but for upload failure we just return generic error.
        raise HTTPException(
            status_code=400, 
            detail="Файл не відповідає критеріям порталу (мова або формат)."
        )

    # 3. Extract Metadata (returns tuple: title, author, cover_filepath)
    ext_title, ext_author, cover_filepath = extract_epub_metadata(filepath)

    # 4. Semantic Alignment Check
    sem_result = check_semantic_alignment(ext_title, ext_author, filepath)
    if not sem_result.passed:
        os.remove(filepath)
        if cover_filepath and os.path.exists(cover_filepath):
            os.remove(cover_filepath)
        raise HTTPException(
            status_code=400, 
            detail="Файл не відповідає критеріям порталу (невідповідність метаданих)."
        )

    # Normalize path for DB
    db_cover_path = cover_filepath.replace("\\", "/") if cover_filepath else None
    db_epub_path = filepath.replace("\\", "/")

    # 5. Auto-Approval Logic (MOD-05)
    # Status is 'approved' only if both checks are high-confidence.
    # Otherwise, it stays 'pending' for manual review.
    # Criteria: Semantic similarity >= 0.22 (Strong match)
    is_auto_approved = sem_result.passed and sem_result.similarity_score >= 0.22
    book_status = "approved" if is_auto_approved else "pending"

    # Create book entry
    new_book = Book(
        title=ext_title or "Unknown Title",
        author=ext_author or "Unknown Author",
        description="",
        cover_filepath=db_cover_path,
        epub_filepath=db_epub_path,
        file_hash=file_hash,
        uploaded_by=current_user.id,
        status=book_status,
        moderation_notes=sem_result.reason # Store the detailed AI reason here
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    # 5.5 Auto-Unlock for the uploader (Always free for them)
    # Check if already in library (unlikely but safe)
    already_in_library = db.query(UserLibrary).filter(
        UserLibrary.user_id == current_user.id,
        UserLibrary.book_id == new_book.id
    ).first()
    if not already_in_library:
        db.add(UserLibrary(user_id=current_user.id, book_id=new_book.id))
        db.commit()

    # 6. Award Credits for Auto-Approved books
    message = f"Книгу успішно завантажено та відправлено на модерацію."
    if is_auto_approved:
        award_upload_credits(db, current_user.id, new_book.title)
        message = f"Книгу підтверджено ШІ-бібліотекарем! Вам нараховано +1 кредит."

    return {"message": message, "id": new_book.id, "status": book_status}

@router.get("/{book_id}/stats", response_model=BookStats)
def get_book_stats(book_id: int, db: Session = Depends(get_db)):
    logs = db.query(BookSendLog).filter(BookSendLog.book_id == book_id).all()
    unique_users = len(set(log.email for log in logs))
    return {"total_sends": len(logs), "unique_users": unique_users}

# --- ADMIN ENDPOINTS ---

@router.post("/{book_id}/approve")
def approve_book(book_id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    book.status = "approved"
    
    # Grant credit to the uploader
    uploader = book.uploader
    if uploader:
        uploader.credits += 1
        transaction = CreditTransaction(
            user_id=uploader.id,
            amount=1,
            reason=f"Бонус за книгу: {book.title}"
        )
        db.add(transaction)
    
    db.commit()
    return {"message": "Book approved and 1 credit granted to uploader"}

@router.post("/{book_id}/reject")
def reject_book(book_id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    book.status = "rejected"
    # No credits granted.
    db.commit()
    return {"message": "Book rejected"}

@router.get("/download/{book_id}/admin")
def download_book_for_review(book_id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
        
    if not os.path.exists(book.epub_filepath):
        raise HTTPException(status_code=404, detail="File missing from disk")
        
    return FileResponse(
        path=book.epub_filepath, 
        filename=os.path.basename(book.epub_filepath),
        media_type='application/epub+zip'
    )
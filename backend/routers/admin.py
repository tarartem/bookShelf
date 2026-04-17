import os
import shutil
import hashlib
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from backend.database import get_db
from backend.models import Book, BookSendLog
from backend.schemas import BookResponse, AdminStatsResponse, BookStats
from backend.services.epub_service import extract_epub_metadata

router = APIRouter()


def _save_epub(epub: UploadFile) -> str:
    """Save the uploaded EPUB to disk and return its path."""
    os.makedirs("uploads/books", exist_ok=True)
    # Use a hash-based filename to avoid collisions with same-named files
    epub.file.seek(0)
    content = epub.file.read()
    name_hash = hashlib.md5(content).hexdigest()[:10]
    safe_name = epub.filename.replace(" ", "_")
    epub_path = f"uploads/books/{name_hash}_{safe_name}"
    with open(epub_path, "wb") as f:
        f.write(content)
    return epub_path


@router.post("/books", response_model=List[BookResponse])
async def upload_books(
    epubs: List[UploadFile] = File(..., description="One or more EPUB files"),
    db: Session = Depends(get_db)
):
    """
    Upload one or more EPUB files. Title, author and cover are extracted
    automatically. Any file that is not an EPUB is rejected.
    """
    results = []
    for epub_file in epubs:
        if not epub_file.filename.lower().endswith(".epub"):
            raise HTTPException(
                status_code=400,
                detail=f"'{epub_file.filename}' is not an EPUB file. Only .epub files are accepted."
            )

        epub_path = _save_epub(epub_file)

        # Auto-extract metadata
        title, author, cover_filepath = extract_epub_metadata(epub_path)

        # Fallback to filename if metadata missing
        if not title:
            title = os.path.splitext(epub_file.filename)[0].replace("_", " ").replace("-", " ")
        if not author:
            author = "Unknown"

        existing_book = db.query(Book).filter(Book.title == title).first()
        if existing_book:
            # Skip duplicate, clean up extracted files
            try:
                if os.path.exists(epub_path):
                    os.remove(epub_path)
                # Ignore cover cleanup here to prevent accidentally deleting a shared placeholder cover
            except Exception:
                pass
            continue

        book = Book(
            title=title,
            author=author,
            epub_filepath=epub_path,
            cover_filepath=cover_filepath
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        results.append(book)

    return results


@router.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    try:
        if book.epub_filepath and os.path.exists(book.epub_filepath):
            os.remove(book.epub_filepath)
        if book.cover_filepath and os.path.exists(book.cover_filepath):
            os.remove(book.cover_filepath)
    except Exception as e:
        print(f"File cleanup error: {e}")

    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully."}


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(db: Session = Depends(get_db)):
    total_books = db.query(Book).count()
    total_sends = db.query(BookSendLog).count()

    books = db.query(Book).all()
    books_stats = []
    for b in books:
        sends = db.query(BookSendLog).filter(BookSendLog.book_id == b.id).count()
        uniques = db.query(func.count(func.distinct(BookSendLog.email))).filter(BookSendLog.book_id == b.id).scalar()
        books_stats.append(BookStats(
            book_id=b.id,
            title=b.title,
            total_sends=sends,
            unique_users=uniques or 0
        ))

    return AdminStatsResponse(
        total_books=total_books,
        total_sends=total_sends,
        books_stats=books_stats
    )

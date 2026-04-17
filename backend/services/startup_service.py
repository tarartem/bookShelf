import os
import shutil
import hashlib
import logging
from sqlalchemy.orm import Session
from backend.models import Book
from backend.services.epub_service import extract_epub_metadata

logger = logging.getLogger(__name__)

BOOKS_SOURCE_DIR = "books"
BOOKS_UPLOAD_DIR = "uploads/books"
COVERS_UPLOAD_DIR = "uploads/covers"

def setup_directories():
    """Ensure all required directories exist."""
    os.makedirs(BOOKS_UPLOAD_DIR, exist_ok=True)
    os.makedirs(COVERS_UPLOAD_DIR, exist_ok=True)

def load_books_on_startup(db: Session):
    """
    Scans the local 'books' directory and ensures all EPUBs are imported into the app.
    This helps persistence on platforms like Render where the database/uploads might be wiped.
    """
    if not os.path.exists(BOOKS_SOURCE_DIR):
        logger.warning(f"Source directory '{BOOKS_SOURCE_DIR}' not found. Skipping startup import.")
        return

    setup_directories()
    
    epub_files = [f for f in os.listdir(BOOKS_SOURCE_DIR) if f.lower().endswith(".epub")]
    if not epub_files:
        print(f"DEBUG: No EPUB files found in '{BOOKS_SOURCE_DIR}'.")
        return

    print(f"DEBUG: Found {len(epub_files)} books in '{BOOKS_SOURCE_DIR}'. Starting import...")

    # Fetch all existing titles to avoid redundant processing
    try:
        existing_titles = {b.title for b in db.query(Book.title).all()}
    except Exception as e:
        print(f"DEBUG: Failed to fetch existing titles: {e}")
        existing_titles = set()
    
    added_count = 0
    total_processed = 0
    for filename in epub_files:
        total_processed += 1
        source_path = os.path.join(BOOKS_SOURCE_DIR, filename)
        
        try:
            # Quick check: if we already have a book whose title matches the filename (fallback title), skip?
            # Better: use filename as a key for now if we want speed.
            
            with open(source_path, "rb") as f:
                content = f.read()
            
            name_hash = hashlib.md5(content).hexdigest()[:10]
            safe_name = filename.replace(" ", "_")
            epub_path = os.path.join(BOOKS_UPLOAD_DIR, f"{name_hash}_{safe_name}")
            
            if not os.path.exists(epub_path):
                with open(epub_path, "wb") as f:
                    f.write(content)

            # Only extract metadata if not already in DB
            # This is tricky because we don't know the title yet.
            # However, we can use the name_hash + safe_name to see if this PATH is in the DB.
            
            existing_path = db.query(Book).filter(Book.epub_filepath == epub_path).first()
            if existing_path:
                continue

            title, author, cover_filepath = extract_epub_metadata(epub_path)

            if not title:
                title = os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
            if not author:
                author = "Unknown"

            if title in existing_titles:
                continue

            book = Book(
                title=title,
                author=author,
                epub_filepath=epub_path,
                cover_filepath=cover_filepath
            )
            db.add(book)
            existing_titles.add(title)
            added_count += 1
            
            if added_count % 10 == 0:
                db.commit()
                print(f"DEBUG: Progress: {total_processed}/{len(epub_files)} books processed. Added {added_count} so far.")

        except Exception as e:
            print(f"DEBUG: Error importing '{filename}': {e}")
            continue

    if added_count > 0:
        db.commit()
        print(f"DEBUG: Import complete. Added {added_count} new books.")
    else:
        print("DEBUG: Import complete. No new books added.")

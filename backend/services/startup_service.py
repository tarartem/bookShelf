import os
import shutil
import hashlib
import logging
import json
from sqlalchemy.orm import Session
from backend.models import Book
from backend.services.epub_service import extract_epub_metadata

logger = logging.getLogger(__name__)

BOOKS_SOURCE_DIR = "books"
METADATA_FILE = os.path.join(BOOKS_SOURCE_DIR, "metadata.json")
BOOKS_UPLOAD_DIR = "uploads/books"
COVERS_UPLOAD_DIR = "uploads/covers"

def load_metadata():
    """Load the metadata.json file if it exists."""
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"DEBUG: Failed to load metadata.json: {e}")
    return {}

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
    
    metadata = load_metadata()
    epub_files = [f for f in os.listdir(BOOKS_SOURCE_DIR) if f.lower().endswith(".epub")]
    if not epub_files:
        print(f"DEBUG: No EPUB files found in '{BOOKS_SOURCE_DIR}'.")
        return

    print(f"DEBUG: Found {len(epub_files)} books in '{BOOKS_SOURCE_DIR}'. Starting import...")

    # Fetch all existing books to check for updates
    try:
        existing_books_by_path = {b.epub_filepath: b for b in db.query(Book).all()}
        existing_titles = {b.title for b in existing_books_by_path.values()}
    except Exception as e:
        print(f"DEBUG: Failed to fetch existing books: {e}")
        existing_books_by_path = {}
        existing_titles = set()
    
    added_count = 0
    updated_count = 0
    total_processed = 0
    for filename in epub_files:
        total_processed += 1
        source_path = os.path.join(BOOKS_SOURCE_DIR, filename)
        
        try:
            with open(source_path, "rb") as f:
                content = f.read()
            
            name_hash = hashlib.md5(content).hexdigest()[:10]
            safe_name = filename.replace(" ", "_")
            epub_path = os.path.join(BOOKS_UPLOAD_DIR, f"{name_hash}_{safe_name}")
            
            if not os.path.exists(epub_path):
                with open(epub_path, "wb") as f:
                    f.write(content)

            # Check if already in DB
            book_entry = existing_books_by_path.get(epub_path)
            
            # Metadata from JSON (if any)
            file_meta = metadata.get(filename, {})
            json_title = file_meta.get("title")
            json_author = file_meta.get("author")
            json_description = file_meta.get("description")

            if book_entry:
                # Update description if it's in JSON and different
                if json_description and book_entry.description != json_description:
                    book_entry.description = json_description
                    updated_count += 1
                
                # CRITICAL: Re-extract cover if missing from disk (e.g. after Render restart)
                if not book_entry.cover_filepath or not os.path.exists(book_entry.cover_filepath):
                    print(f"DEBUG: Cover missing for '{book_entry.title}', re-extracting...")
                    _, _, new_cover = extract_epub_metadata(epub_path)
                    if new_cover:
                        book_entry.cover_filepath = new_cover
                        db.add(book_entry)
                        updated_count += 1
                continue

            # NEW BOOK IMPORT
            # Extract metadata from EPUB
            ext_title, ext_author, cover_filepath = extract_epub_metadata(epub_path)

            # Logic: JSON > EPUB Extracted > Filename Fallback
            final_title = json_title or ext_title or os.path.splitext(filename)[0].replace("_", " ").replace("-", " ")
            final_author = json_author or ext_author or "Unknown"
            final_description = json_description or ""

            if final_title in existing_titles:
                continue

            book = Book(
                title=final_title,
                author=final_author,
                description=final_description,
                epub_filepath=epub_path,
                cover_filepath=cover_filepath
            )
            db.add(book)
            existing_titles.add(final_title)
            added_count += 1
            
            if (added_count + updated_count) % 10 == 0:
                db.commit()

        except Exception as e:
            print(f"DEBUG: Error importing '{filename}': {e}")
            continue

    db.commit()
    print(f"DEBUG: Import complete. Added {added_count} new books, updated {updated_count} descriptions.")

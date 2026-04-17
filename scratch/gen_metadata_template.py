import os
import json
from ebooklib import epub
import warnings

# Suppress ebooklib warnings
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

BOOKS_DIR = "books"
OUTPUT_FILE = "books/metadata.json"

def get_epub_info(filepath):
    try:
        book = epub.read_epub(filepath)
        title = book.get_metadata('DC', 'title')[0][0] if book.get_metadata('DC', 'title') else os.path.basename(filepath)
        author = book.get_metadata('DC', 'creator')[0][0] if book.get_metadata('DC', 'creator') else "Unknown"
        return title, author
    except:
        return os.path.basename(filepath), "Unknown"

metadata = {}

print("Scanning books...")
for filename in os.listdir(BOOKS_DIR):
    if filename.lower().endswith(".epub"):
        filepath = os.path.join(BOOKS_DIR, filename)
        title, author = get_epub_info(filepath)
        metadata[filename] = {
            "title": title,
            "author": author,
            "description": "" # User will fill this
        }

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=4, ensure_ascii=False)

print(f"Generated template for {len(metadata)} books at {OUTPUT_FILE}")

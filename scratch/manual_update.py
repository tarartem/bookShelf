from backend.database import SessionLocal
from backend.services.startup_service import load_books_on_startup

print("Triggering manual metadata update...")
db = SessionLocal()
try:
    load_books_on_startup(db)
    print("Manual update completed successfully.")
except Exception as e:
    print(f"Manual update failed: {e}")
finally:
    db.close()

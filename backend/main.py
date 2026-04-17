import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import engine, Base, SessionLocal
from backend.routers import books, admin, feedback
from backend.services.startup_service import load_books_on_startup

# Create database tables
Base.metadata.create_all(bind=engine)

import threading

# Startup task: Load books in a background thread to avoid health check timeouts
def run_startup_task():
    print("DEBUG: Starting background startup book loading task...")
    db = SessionLocal()
    try:
        load_books_on_startup(db)
        print("DEBUG: Background startup book loading task finished.")
    except Exception as e:
        print(f"DEBUG: Background startup book loading task failed: {e}")
    finally:
        db.close()

threading.Thread(target=run_startup_task, daemon=True).start()

app = FastAPI(title="BookShelf API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(books.router, prefix="/api/books", tags=["books"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])

# Mount static files for uploads
app.mount("/api/uploads", StaticFiles(directory="uploads"), name="uploads")

# Frontend - catch all others and serve index.html (Vanilla SPA)
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

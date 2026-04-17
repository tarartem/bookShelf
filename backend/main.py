import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.database import engine, Base
from backend.routers import books, admin, feedback

# Create uploaded files directory
os.makedirs("uploads/books", exist_ok=True)
os.makedirs("uploads/covers", exist_ok=True)

# Create database tables
Base.metadata.create_all(bind=engine)

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

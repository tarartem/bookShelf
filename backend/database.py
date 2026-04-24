import os
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bookshelf.db")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

# Handle Turso (libsql) URLs
if DATABASE_URL.startswith("libsql://") or DATABASE_URL.startswith("https://"):
    # SQLAlchemy requires sqlalchemy-libsql for libsql://
    # If using https:// (Turso), we convert it to the expected dialect
    final_url = DATABASE_URL
    if DATABASE_URL.startswith("libsql://"):
        final_url = DATABASE_URL.replace("libsql://", "sqlite+libsql://")
    elif DATABASE_URL.startswith("https://"):
        final_url = DATABASE_URL.replace("https://", "sqlite+libsql://")
        
    engine = create_engine(
        final_url,
        connect_args={"auth_token": TURSO_AUTH_TOKEN} if TURSO_AUTH_TOKEN else {}
    )
else:
    # Standard SQLite
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    )

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if hasattr(dbapi_connection, "create_function"):
        dbapi_connection.create_function("lower", 1, lambda x: x.lower() if x is not None else None)
        dbapi_connection.create_function("upper", 1, lambda x: x.upper() if x is not None else None)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

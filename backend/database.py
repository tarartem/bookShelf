import os
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bookshelf.db")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

# Handle Turso (libsql) URLs
is_remote = DATABASE_URL.startswith("libsql://") or DATABASE_URL.startswith("https://")

if is_remote:
    # Format: sqlite+libsql://[host]?auth_token=[token]
    host = DATABASE_URL.replace("libsql://", "").replace("https://", "")
    # Remove any trailing slashes
    host = host.split('/')[0]
    final_url = f"sqlite+libsql://{host}"
    
    engine = create_engine(
        final_url,
        connect_args={"auth_token": TURSO_AUTH_TOKEN} if TURSO_AUTH_TOKEN else {}
    )
else:
    # Standard local SQLite
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    )

@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    # ONLY apply these to local SQLite connections
    if not is_remote and hasattr(dbapi_connection, "create_function"):
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

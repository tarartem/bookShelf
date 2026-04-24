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
    import libsql_client
    # Turso URLs should be converted to https:// format for the client
    clean_url = DATABASE_URL.replace("libsql://", "https://")
    
    def create_libsql_conn():
        return libsql_client.connect(url=clean_url, auth_token=TURSO_AUTH_TOKEN)
    
    engine = create_engine(
        "sqlite://", # Use dummy sqlite dialect
        creator=create_libsql_conn,
        isolation_level=None
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

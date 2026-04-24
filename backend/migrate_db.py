import os
from sqlalchemy import text
from backend.database import engine, is_sqlite


def migrate():
    print("Connecting to database to check for migrations...")

    with engine.connect() as conn:

        # --- USERS TABLE ---
        print("Ensuring 'users' table exists...")
        if is_sqlite:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR UNIQUE NOT NULL,
                    hashed_password VARCHAR NOT NULL,
                    is_verified BOOLEAN DEFAULT 0,
                    role VARCHAR DEFAULT 'user',
                    credits INTEGER DEFAULT 3,
                    email_notifications BOOLEAN DEFAULT 0,
                    received_notif_bonus BOOLEAN DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            '''))
        else:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR UNIQUE NOT NULL,
                    hashed_password VARCHAR NOT NULL,
                    is_verified BOOLEAN DEFAULT FALSE,
                    role VARCHAR DEFAULT 'user',
                    credits INTEGER DEFAULT 3,
                    email_notifications BOOLEAN DEFAULT FALSE,
                    received_notif_bonus BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            '''))

        for col_name, col_type in [("credits", "INTEGER DEFAULT 3"), ("email_notifications", "BOOLEAN DEFAULT FALSE"), ("received_notif_bonus", "BOOLEAN DEFAULT FALSE")]:
            try:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
            except Exception:
                pass

        # --- BOOKS TABLE ---
        print("Ensuring 'books' table exists...")
        if is_sqlite:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR NOT NULL,
                    author VARCHAR,
                    description TEXT,
                    epub_filepath VARCHAR NOT NULL,
                    cover_filepath VARCHAR,
                    file_hash VARCHAR,
                    status VARCHAR DEFAULT 'approved',
                    owner_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            '''))
        else:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR NOT NULL,
                    author VARCHAR,
                    description TEXT,
                    epub_filepath VARCHAR NOT NULL,
                    cover_filepath VARCHAR,
                    file_hash VARCHAR,
                    status VARCHAR DEFAULT 'approved',
                    owner_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            '''))

        for col_name, col_type in [("file_hash", "VARCHAR"), ("status", "VARCHAR DEFAULT 'approved'"), ("owner_id", "INTEGER")]:
            try:
                conn.execute(text(f"ALTER TABLE books ADD COLUMN IF NOT EXISTS {col_name} {col_type};"))
            except Exception:
                pass

        # --- LOGS TABLE ---
        print("Ensuring 'book_send_logs' table exists...")
        if is_sqlite:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS book_send_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    user_id INTEGER,
                    email VARCHAR NOT NULL,
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (book_id) REFERENCES books(id)
                );
            '''))
        else:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS book_send_logs (
                    id SERIAL PRIMARY KEY,
                    book_id INTEGER NOT NULL,
                    user_id INTEGER,
                    email VARCHAR NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (book_id) REFERENCES books(id)
                );
            '''))

        # --- TRANSACTIONS TABLE ---
        print("Ensuring 'credit_transactions' table exists...")
        if is_sqlite:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS credit_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    reason VARCHAR NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            '''))
        else:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS credit_transactions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    reason VARCHAR NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            '''))

        # --- FEEDBACK TABLE ---
        print("Ensuring 'feedback' table exists...")
        if is_sqlite:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            '''))
        else:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            '''))

        conn.commit()

    print("Migration completed successfully.")


if __name__ == "__main__":
    migrate()

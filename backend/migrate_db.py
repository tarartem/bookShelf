import os
from sqlalchemy import text
from backend.database import engine


def migrate():
    print("Connecting to database to check for migrations...")

    with engine.connect() as conn:

        # --- USERS TABLE ---
        print("Ensuring 'users' table exists...")
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

        # Add missing columns to users (safe no-op if already exists)
        user_columns_to_add = [
            ("credits", "INTEGER DEFAULT 3"),
            ("email_notifications", "BOOLEAN DEFAULT 0"),
            ("received_notif_bonus", "BOOLEAN DEFAULT 0"),
        ]
        for col_name, col_type in user_columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};"))
                print(f"Added column '{col_name}' to 'users'.")
            except Exception:
                pass  # Column already exists

        # --- BOOKS TABLE ---
        print("Ensuring 'books' table exists...")
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

        books_columns_to_add = [
            ("file_hash", "VARCHAR"),
            ("status", "VARCHAR DEFAULT 'approved'"),
            ("owner_id", "INTEGER"),
        ]
        for col_name, col_type in books_columns_to_add:
            try:
                conn.execute(text(f"ALTER TABLE books ADD COLUMN {col_name} {col_type};"))
                print(f"Added column '{col_name}' to 'books'.")
            except Exception:
                pass  # Column already exists

        # --- LOGS TABLE ---
        print("Ensuring 'book_send_logs' table exists...")
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

        # --- TRANSACTIONS TABLE ---
        print("Ensuring 'credit_transactions' table exists...")
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

        # --- FEEDBACK TABLE ---
        print("Ensuring 'feedback' table exists...")
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        '''))

        conn.commit()

    print("Migration completed successfully.")


if __name__ == "__main__":
    migrate()

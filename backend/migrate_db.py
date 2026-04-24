import os
from sqlalchemy import create_engine, text
from backend.database import DATABASE_URL

def run_migrations():
    print(f"Connecting to database: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    is_sqlite = DATABASE_URL.startswith("sqlite")

    with engine.connect() as conn:
        # --- USERS TABLE ---
        print("Ensuring 'users' table exists...")
        if is_sqlite:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email VARCHAR NOT NULL UNIQUE,
                    password_hash VARCHAR NOT NULL,
                    role VARCHAR DEFAULT 'user',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_verified BOOLEAN DEFAULT FALSE,
                    credits INTEGER DEFAULT 3,
                    email_notifications BOOLEAN DEFAULT FALSE,
                    received_notif_bonus BOOLEAN DEFAULT FALSE
                );
            '''))
        else:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR NOT NULL UNIQUE,
                    password_hash VARCHAR NOT NULL,
                    role VARCHAR DEFAULT 'user',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_verified BOOLEAN DEFAULT FALSE,
                    credits INTEGER DEFAULT 3,
                    email_notifications BOOLEAN DEFAULT FALSE,
                    received_notif_bonus BOOLEAN DEFAULT FALSE
                );
            '''))
        
        # --- BOOKS TABLE ---
        print("Ensuring 'books' table exists...")
        if is_sqlite:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title VARCHAR NOT NULL,
                    author VARCHAR,
                    description TEXT,
                    cover_filepath VARCHAR,
                    epub_filepath VARCHAR NOT NULL,
                    uploaded_by INTEGER,
                    status VARCHAR DEFAULT 'pending',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (uploaded_by) REFERENCES users(id)
                );
            '''))
        else:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR NOT NULL,
                    author VARCHAR,
                    description TEXT,
                    cover_filepath VARCHAR,
                    epub_filepath VARCHAR NOT NULL,
                    uploaded_by INTEGER,
                    status VARCHAR DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (uploaded_by) REFERENCES users(id)
                );
            '''))
            
        # --- BOOK SEND LOG TABLE ---
        print("Ensuring 'book_send_logs' table exists...")
        if is_sqlite:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS book_send_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    user_id INTEGER,
                    email VARCHAR NOT NULL,
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (book_id) REFERENCES books(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
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
                    FOREIGN KEY (book_id) REFERENCES books(id),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            '''))

        # --- CREDIT TRANSACTIONS TABLE ---
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

        # --- USER LIBRARY TABLE ---
        print("Ensuring 'user_library' table exists...")
        if is_sqlite:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS user_library (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (book_id) REFERENCES books(id)
                );
            '''))
        else:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS user_library (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (book_id) REFERENCES books(id)
                );
            '''))

        conn.commit()

    print("Migration completed successfully.")

if __name__ == "__main__":
    run_migrations()
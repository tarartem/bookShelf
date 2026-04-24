import os
from sqlalchemy import text, inspect
from backend.database import engine

def migrate():
    print(f"Connecting to database to check for migrations...")
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        
        # --- USERS TABLE ---
        if 'users' not in inspector.get_table_names():
            print("Creating 'users' table...")
            conn.execute(text('''
                CREATE TABLE users (
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
            # Check for missing columns
            existing_columns = [col['name'] for col in inspector.get_columns('users')]
            user_columns_to_add = [
                ("credits", "INTEGER DEFAULT 3"),
                ("email_notifications", "BOOLEAN DEFAULT 0"),
                ("received_notif_bonus", "BOOLEAN DEFAULT 0")
            ]
            for col_name, col_type in user_columns_to_add:
                if col_name not in existing_columns:
                    print(f"Adding column '{col_name}' to 'users' table...")
                    conn.execute(text(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};"))

        # --- BOOKS TABLE ---
        if 'books' not in inspector.get_table_names():
            print("Creating 'books' table...")
            conn.execute(text('''
                CREATE TABLE books (
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
            existing_columns = [col['name'] for col in inspector.get_columns('books')]
            columns_to_add = [
                ("file_hash", "VARCHAR"),
                ("status", "VARCHAR DEFAULT 'approved'"),
                ("owner_id", "INTEGER")
            ]
            for col_name, col_type in columns_to_add:
                if col_name not in existing_columns:
                    print(f"Adding column '{col_name}' to 'books' table...")
                    conn.execute(text(f"ALTER TABLE books ADD COLUMN {col_name} {col_type};"))

        # --- LOGS TABLE ---
        if 'book_send_logs' not in inspector.get_table_names():
            print("Creating 'book_send_logs' table...")
            conn.execute(text('''
                CREATE TABLE book_send_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    user_id INTEGER,
                    email VARCHAR NOT NULL,
                    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (book_id) REFERENCES books(id)
                );
            '''))

        # --- TRANSACTIONS TABLE ---
        if 'credit_transactions' not in inspector.get_table_names():
            print("Creating 'credit_transactions' table...")
            conn.execute(text('''
                CREATE TABLE credit_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount INTEGER NOT NULL,
                    reason VARCHAR NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            '''))

        # --- FEEDBACK TABLE ---
        if 'feedback' not in inspector.get_table_names():
            print("Creating 'feedback' table...")
            conn.execute(text('''
                CREATE TABLE feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
            '''))

        conn.commit()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()

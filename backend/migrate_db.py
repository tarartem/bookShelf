import sqlite3
import os

def migrate():
    # Production support: extract path from DATABASE_URL if it's a sqlite URI
    db_url = os.environ.get("DATABASE_URL", "sqlite:///./bookshelf.db")
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
    else:
        db_path = "bookshelf.db"
    
    # Ensure directory exists if path contains one (e.g. data/bookshelf.db)
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        print(f"Creating directory {db_dir}...")
        os.makedirs(db_dir, exist_ok=True)

    # Note: connect() will create the file if it doesn't exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking for 'users' table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if not cursor.fetchone():
        print("Creating 'users' table...")
        cursor.execute('''
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
        ''')
    else:
        # Add new columns to users if missing
        cursor.execute("PRAGMA table_info(users);")
        existing_user_columns = [col[1] for col in cursor.fetchall()]
        user_columns_to_add = [
            ("credits", "INTEGER DEFAULT 3"),
            ("email_notifications", "BOOLEAN DEFAULT 0"),
            ("received_notif_bonus", "BOOLEAN DEFAULT 0")
        ]
        for col_name, col_type in user_columns_to_add:
            if col_name not in existing_user_columns:
                print(f"Adding column '{col_name}' to 'users' table...")
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type};")

    print("Checking for 'books' table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='books';")
    if not cursor.fetchone():
        print("Creating 'books' table...")
        cursor.execute('''
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
        ''')
    else:
        cursor.execute("PRAGMA table_info(books);")
        existing_columns = [col[1] for col in cursor.fetchall()]
        columns_to_add = [
            ("file_hash", "VARCHAR"),
            ("status", "VARCHAR DEFAULT 'approved'"),
            ("owner_id", "INTEGER")
        ]
        for col_name, col_type in columns_to_add:
            if col_name not in existing_columns:
                print(f"Adding column '{col_name}' to 'books' table...")
                cursor.execute(f"ALTER TABLE books ADD COLUMN {col_name} {col_type};")

    print("Checking for 'book_send_logs' table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='book_send_logs';")
    if not cursor.fetchone():
        print("Creating 'book_send_logs' table...")
        cursor.execute('''
            CREATE TABLE book_send_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                user_id INTEGER,
                email VARCHAR NOT NULL,
                sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books(id)
            );
        ''')

    print("Checking for 'credit_transactions' table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='credit_transactions';")
    if not cursor.fetchone():
        print("Creating 'credit_transactions' table...")
        cursor.execute('''
            CREATE TABLE credit_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                reason VARCHAR NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        ''')

    print("Checking for 'feedback' table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback';")
    if not cursor.fetchone():
        print("Creating 'feedback' table...")
        cursor.execute('''
            CREATE TABLE feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        ''')

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()

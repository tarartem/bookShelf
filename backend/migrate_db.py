import sqlite3
import os

def migrate():
    db_path = "bookshelf.db"
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking for 'users' table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    if not cursor.fetchone():
        print("Creating 'users' table...")
        cursor.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR UNIQUE NOT NULL,
                hashed_password VARCHAR NOT NULL,
                is_verified BOOLEAN DEFAULT 0,
                role VARCHAR DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("'users' table created.")
    else:
        print("'users' table already exists.")

    print("Updating 'books' table...")
    # SQL to add columns if they don't exist
    columns_to_add = [
        ("file_hash", "VARCHAR"),
        ("status", "VARCHAR DEFAULT 'approved'"),
        ("owner_id", "INTEGER")
    ]

    cursor.execute("PRAGMA table_info(books);")
    existing_columns = [col[1] for col in cursor.fetchall()]

    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            print(f"Adding column '{col_name}' to 'books' table...")
            cursor.execute(f"ALTER TABLE books ADD COLUMN {col_name} {col_type};")
        else:
            print(f"Column '{col_name}' already exists in 'books' table.")

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()

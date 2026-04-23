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
        cursor.execute(\"\"\"
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR UNIQUE NOT NULL,
                hashed_password VARCHAR NOT NULL,
                is_verified BOOLEAN DEFAULT 0,
                role VARCHAR DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        \"\"\")
        print("'users' table created.")
    else:
        print("'users' table already exists.")
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

    print("Checking for 'credit_transactions' table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='credit_transactions';")
    if not cursor.fetchone():
        print("Creating 'credit_transactions' table...")
        cursor.execute(\"\"\"
            CREATE TABLE credit_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                reason VARCHAR NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        \"\"\")
        print("'credit_transactions' table created.")

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()

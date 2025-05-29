import sqlite3

DB_NAME = "users.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Drop existing table if exists (for testing/fresh start)
    c.execute("DROP TABLE IF EXISTS users")

    # Create table with email field
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            coins INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()
    print("Database and 'users' table created successfully.")

if __name__ == "__main__":
    create_database()

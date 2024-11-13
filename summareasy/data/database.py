import sqlite3

def get_db_connection():
    """
    Connect to the SQLite database and return the connection object.

    The database name is set in the DATABASE_URL environment variable.
    The row factory is set to sqlite3.Row, which returns rows as dictionaries.
    """
    conn = sqlite3.connect('summareasy.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    """Create the 'emails' table in the database if it does not exist.

    The table has the following columns:
    - id: an auto-incrementing primary key
    - email_id: a unique identifier for the email
    - sender: the email sender
    - subject: the email subject
    - body: the email body content
    - received_at: the timestamp when the email was received, defaults to the current timestamp
    - raw_email: the raw email payload
    """
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT UNIQUE,
            sender TEXT,
            subject TEXT,
            body TEXT,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            raw_email TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
if __name__ == '__main__':
    create_tables()

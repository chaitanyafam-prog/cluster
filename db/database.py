import sqlite3

def init_db():
    conn = sqlite3.connect("learning.db", check_same_thread=False)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS student_profile (
        user_id INTEGER,
        interests TEXT,
        preferred_format TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        topic TEXT,
        math INTEGER,
        reading INTEGER,
        clicks INTEGER,
        cluster INTEGER
    )
    """)

    conn.commit()
    return conn

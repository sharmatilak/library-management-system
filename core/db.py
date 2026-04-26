import sqlite3
import os
from datetime import datetime

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/library.db")
    conn.row_factory = sqlite3.Row  # This makes column access nicer
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Admin table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        login_attempts INTEGER DEFAULT 0,
        locked_until TEXT
    )
    """)

    # Students table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            branch TEXT,
            semester TEXT,
            phone TEXT UNIQUE,
            email TEXT UNIQUE
        )
    """)

    # Books table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS books (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        year TEXT,
        isbn TEXT UNIQUE,
        total_copies INTEGER DEFAULT 1,
        available_copies INTEGER DEFAULT 1
    )
""")

    # Borrow table (updated with due date and fine)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS borrow (
            borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            book_id INTEGER,
            borrow_date TEXT,
            due_date TEXT,
            return_date TEXT,
            fine_amount REAL DEFAULT 0,
            fine_paid INTEGER DEFAULT 0,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(book_id) REFERENCES books(book_id)
        )
    """)
    
    # Activity log for tracking
    cur.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_username TEXT,
            action TEXT,
            details TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()
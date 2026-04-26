from datetime import datetime, timedelta
from core.books import find_book, update_available_copies
from core.students import find_student
from core.db import get_connection

BORROW_DAYS = 14
FINE_PER_DAY = 10

def ensure_borrow_table():
    conn = get_connection()
    cur = conn.cursor()
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
    conn.commit()
    conn.close()

def calculate_fine(borrow_date, return_date=None):
    if isinstance(borrow_date, str):
        borrow_date = datetime.strptime(borrow_date, "%Y-%m-%d")
    
    due_date = borrow_date + timedelta(days=BORROW_DAYS)
    
    if return_date:
        if isinstance(return_date, str):
            return_date = datetime.strptime(return_date, "%Y-%m-%d")
        if return_date > due_date:
            days_over = (return_date - due_date).days
            return days_over * FINE_PER_DAY
    else:
        if datetime.now() > due_date:
            days_over = (datetime.now() - due_date).days
            return days_over * FINE_PER_DAY
    return 0

def is_book_currently_borrowed(book_id):
    ensure_borrow_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM borrow WHERE book_id=? AND return_date IS NULL", (book_id,))
    row = cur.fetchone()
    conn.close()
    return row is not None

def get_available_copies(book_id):
    book = find_book(book_id)
    return book.get("available_copies", 0) if book else 0

def borrow_book(student_id, book_id):
    ensure_borrow_table()
    
    if not find_student(student_id):
        return False, "Student not found."
    
    book = find_book(book_id)
    if not book:
        return False, "Book not found."
    
    if book.get("available_copies", 0) <= 0:
        return False, "No copies available."
    
    now = datetime.now()
    borrow_date = now.strftime("%Y-%m-%d")
    due_date = (now + timedelta(days=BORROW_DAYS)).strftime("%Y-%m-%d")
    
    conn = get_connection()
    cur = conn.cursor()
    

    cur.execute("""
        INSERT INTO borrow (student_id, book_id, borrow_date, due_date) 
        VALUES (?, ?, ?, ?)
    """, (student_id, book_id, borrow_date, due_date))
    
    cur.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ?", (book_id,))
    
    conn.commit()
    conn.close()
    return True, f"Borrow recorded. Due date: {due_date}"

def return_book(borrow_id=None, student_id=None, book_id=None):
    ensure_borrow_table()
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d")
    
    if borrow_id:
        cur.execute("SELECT borrow_date FROM borrow WHERE borrow_id=? AND return_date IS NULL", (borrow_id,))
        row = cur.fetchone()
        if row:
            fine = calculate_fine(row[0], now)
            cur.execute("""
                UPDATE borrow SET return_date=?, fine_amount=?, fine_paid=0 
                WHERE borrow_id=? AND return_date IS NULL
            """, (now, fine, borrow_id))
            
            cur.execute("SELECT book_id FROM borrow WHERE borrow_id=?", (borrow_id,))
            book_row = cur.fetchone()
            if book_row:
                cur.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?", (book_row[0],))
                
    elif student_id and book_id:
        cur.execute("SELECT borrow_date FROM borrow WHERE student_id=? AND book_id=? AND return_date IS NULL", 
                    (student_id, book_id))
        row = cur.fetchone()
        if row:
            fine = calculate_fine(row[0], now)
            cur.execute("""
                UPDATE borrow SET return_date=?, fine_amount=?, fine_paid=0 
                WHERE student_id=? AND book_id=? AND return_date IS NULL
            """, (now, fine, student_id, book_id))
            

            cur.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id = ?", (book_id,))
    else:
        conn.close()
        return False, "No valid identifier provided."
    
    if cur.rowcount > 0:
        conn.commit()
        conn.close()
        fine_msg = f" Fine: ₹{fine}" if fine > 0 else ""
        return True, f"Return recorded.{fine_msg}"
    
    conn.close()
    return False, "No matching active borrow record found."

def list_currently_borrowed():
    ensure_borrow_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM borrow WHERE return_date IS NULL")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def list_all_borrowed():
    ensure_borrow_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM borrow ORDER BY borrow_date DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def books_borrowed_by_student(student_id):
    ensure_borrow_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM borrow WHERE student_id=? ORDER BY borrow_date DESC", (student_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def who_borrowed_book(book_id):
    ensure_borrow_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM borrow WHERE book_id=? ORDER BY borrow_date DESC", (book_id,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_overdue_books():
    ensure_borrow_table()
    conn = get_connection()
    cur = conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT * FROM borrow 
        WHERE return_date IS NULL AND due_date < ?
    """, (today,))
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def collect_fine(borrow_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE borrow SET fine_paid = 1 WHERE borrow_id = ?", (borrow_id,))
    updated = cur.rowcount > 0
    conn.commit()
    conn.close()
    return updated
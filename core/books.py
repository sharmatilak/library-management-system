from core.db import get_connection

def ensure_books_table():
    conn = get_connection()
    cur = conn.cursor()
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
    conn.commit()
    conn.close()

def is_valid_isbn(isbn):
    if not isbn:
        return True
    return isbn.isdigit() and 10 <= len(isbn) <= 13

def is_valid_year(year):
    if not year:
        return True
    return year.isdigit() and len(year) == 4

def is_duplicate_book(title=None, isbn=None, exclude_id=None):
    conn = get_connection()
    cur = conn.cursor()
    
    if exclude_id:
        if title:
            cur.execute("SELECT COUNT(*) FROM books WHERE title = ? AND book_id != ?", (title, exclude_id))
            if cur.fetchone()[0] > 0:
                conn.close()
                return True
        if isbn and isbn.strip():
            cur.execute("SELECT COUNT(*) FROM books WHERE isbn = ? AND book_id != ?", (isbn, exclude_id))
            if cur.fetchone()[0] > 0:
                conn.close()
                return True
    else:
        if title:
            cur.execute("SELECT COUNT(*) FROM books WHERE title = ?", (title,))
            if cur.fetchone()[0] > 0:
                conn.close()
                return True
        if isbn and isbn.strip():
            cur.execute("SELECT COUNT(*) FROM books WHERE isbn = ?", (isbn,))
            if cur.fetchone()[0] > 0:
                conn.close()
                return True
    
    conn.close()
    return False

def add_book(title, author="", year="", isbn="", total_copies=1):
    ensure_books_table()
    
    if not title:
        raise ValueError("Title is required.")
    
    if year and not is_valid_year(year):
        raise ValueError("Year must be 4 digits only.")
    
    if isbn and not is_valid_isbn(isbn):
        raise ValueError("ISBN must be 10–13 digits only.")
    
    if is_duplicate_book(title=title, isbn=isbn):
        raise ValueError("A book with the same title or ISBN already exists.")
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO books (title, author, year, isbn, total_copies, available_copies) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, author, year, isbn, total_copies, total_copies))
    conn.commit()
    bid = cur.lastrowid
    conn.close()
    return bid

def update_book(book_id, title=None, author=None, year=None, isbn=None, total_copies=None):
    ensure_books_table()
    
    if year and not is_valid_year(year):
        raise ValueError("Year must be 4 digits only.")
    
    if isbn and not is_valid_isbn(isbn):
        raise ValueError("ISBN must be 10–13 digits only.")
    
    if title or isbn:
        current_book = find_book(book_id)
        check_title = title if title else current_book.get('title')
        check_isbn = isbn if isbn else current_book.get('isbn')
        
        if is_duplicate_book(title=check_title, isbn=check_isbn, exclude_id=book_id):
            raise ValueError("Another book with the same title or ISBN already exists.")
    
    conn = get_connection()
    cur = conn.cursor()
    fields, values = [], []
    
    if title is not None:
        fields.append("title=?")
        values.append(title)
    if author is not None:
        fields.append("author=?")
        values.append(author)
    if year is not None:
        fields.append("year=?")
        values.append(year)
    if isbn is not None:
        fields.append("isbn=?")
        values.append(isbn)
    if total_copies is not None:
        fields.append("total_copies=?")
        fields.append("available_copies=?")
        values.append(total_copies)
        values.append(total_copies)
    
    values.append(book_id)
    sql = f"UPDATE books SET {', '.join(fields)} WHERE book_id=?"
    cur.execute(sql, values)
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated

def delete_book(book_id):
    ensure_books_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE book_id=?", (book_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted

def find_book(book_id):
    ensure_books_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books WHERE book_id=?", (book_id,))
    row = cur.fetchone()
    conn.close()
    return {"book_id": row[0], "title": row[1], "author": row[2], "year": row[3], "isbn": row[4], "total_copies": row[5], "available_copies": row[6]} if row else None

def load_books():
    ensure_books_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM books")
    rows = cur.fetchall()
    conn.close()
    return [{"book_id": r[0], "title": r[1], "author": r[2], "year": r[3], "isbn": r[4], "total_copies": r[5], "available_copies": r[6]} for r in rows]

def search_books(query):
    ensure_books_table()
    conn = get_connection()
    cur = conn.cursor()
    q = f"%{query}%"
    cur.execute("""SELECT * FROM books 
                   WHERE title LIKE ? OR author LIKE ? OR isbn LIKE ? OR book_id LIKE ?""",
                (q, q, q, q))
    rows = cur.fetchall()
    conn.close()
    return [{"book_id": r[0], "title": r[1], "author": r[2], "year": r[3], "isbn": r[4], "total_copies": r[5], "available_copies": r[6]} for r in rows]

def update_available_copies(book_id, delta):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE books SET available_copies = available_copies + ? WHERE book_id = ? AND available_copies + ? >= 0",
                (delta, book_id, delta))
    updated = cur.rowcount > 0
    conn.commit()
    conn.close()
    return updated
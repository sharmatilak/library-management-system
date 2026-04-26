from core.db import get_connection

def ensure_students_table():
    conn = get_connection()
    cur = conn.cursor()
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
    conn.commit()
    conn.close()

def is_valid_phone(phone):
    if not phone:
        return True
    return phone.isdigit() and len(phone) == 10

def is_valid_email(email):
    if not email:
        return True
    return '@' in email and '.' in email and len(email) > 5

def is_duplicate_student(name=None, phone=None, email=None, exclude_id=None):

    conn = get_connection()
    cur = conn.cursor()
    
    if exclude_id:
        if name:
            cur.execute("SELECT COUNT(*) FROM students WHERE name = ? AND student_id != ?", (name, exclude_id))
            if cur.fetchone()[0] > 0:
                conn.close()
                return True
        if phone and phone.strip():
            cur.execute("SELECT COUNT(*) FROM students WHERE phone = ? AND student_id != ?", (phone, exclude_id))
            if cur.fetchone()[0] > 0:
                conn.close()
                return True
        if email and email.strip():
            cur.execute("SELECT COUNT(*) FROM students WHERE email = ? AND student_id != ?", (email, exclude_id))
            if cur.fetchone()[0] > 0:
                conn.close()
                return True
    else:
        if name:
            cur.execute("SELECT COUNT(*) FROM students WHERE name = ?", (name,))
            if cur.fetchone()[0] > 0:
                conn.close()
                return True
        if phone and phone.strip():
            cur.execute("SELECT COUNT(*) FROM students WHERE phone = ?", (phone,))
            if cur.fetchone()[0] > 0:
                conn.close()
                return True
        if email and email.strip():
            cur.execute("SELECT COUNT(*) FROM students WHERE email = ?", (email,))
            if cur.fetchone()[0] > 0:
                conn.close()
                return True
    
    conn.close()
    return False

def add_student(name, branch="", semester="", phone="", email=""):
    ensure_students_table()
    
    if not name:
        raise ValueError("Name is required.")
    
    if phone and not is_valid_phone(phone):
        raise ValueError("Phone number must contain only digits (10 digits).")
    
    if email and not is_valid_email(email):
        raise ValueError("Invalid email address.")

    if is_duplicate_student(name=name, phone=phone, email=email):
        raise ValueError("A student with the same name, phone number, or email already exists.")
    
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO students (name, branch, semester, phone, email) VALUES (?, ?, ?, ?, ?)", 
                (name, branch, semester, phone, email))
    conn.commit()
    sid = cur.lastrowid
    conn.close()
    return sid

def update_student(student_id, name=None, branch=None, semester=None, phone=None, email=None):
    ensure_students_table()
    
    if phone and not is_valid_phone(phone):
        raise ValueError("Phone number must contain only digits (10 digits).")
    
    if email and not is_valid_email(email):
        raise ValueError("Invalid email address.")
    
    if name or phone or email:
        current = find_student(student_id)
        check_name = name if name else current.get('name')
        check_phone = phone if phone else current.get('phone')
        check_email = email if email else current.get('email')
        
        if is_duplicate_student(name=check_name, phone=check_phone, email=check_email, exclude_id=student_id):
            raise ValueError("Another student with the same name, phone number, or email already exists.")
    
    conn = get_connection()
    cur = conn.cursor()
    fields, values = [], []
    
    if name is not None:
        fields.append("name=?")
        values.append(name)
    if branch is not None:
        fields.append("branch=?")
        values.append(branch)
    if semester is not None:
        fields.append("semester=?")
        values.append(semester)
    if phone is not None:
        fields.append("phone=?")
        values.append(phone)
    if email is not None:
        fields.append("email=?")
        values.append(email)
    
    if not fields:
        return False
    
    values.append(student_id)
    sql = f"UPDATE students SET {', '.join(fields)} WHERE student_id=?"
    cur.execute(sql, values)
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated

def delete_student(student_id):
    ensure_students_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE student_id=?", (student_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted

def find_student(student_id):
    ensure_students_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students WHERE student_id=?", (student_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"student_id": row[0], "name": row[1], "branch": row[2], "semester": row[3], "phone": row[4], "email": row[5]}
    return None

def load_students():
    ensure_students_table()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    rows = cur.fetchall()
    conn.close()
    return [{"student_id": r[0], "name": r[1], "branch": r[2], "semester": r[3], "phone": r[4], "email": r[5]} for r in rows]

def search_students(query):
    ensure_students_table()
    conn = get_connection()
    cur = conn.cursor()
    q = f"%{query}%"
    cur.execute("""SELECT * FROM students 
                   WHERE name LIKE ? OR branch LIKE ? OR semester LIKE ? OR phone LIKE ? OR email LIKE ? OR student_id LIKE ?""",
                (q, q, q, q, q, q))
    rows = cur.fetchall()
    conn.close()
    return [{"student_id": r[0], "name": r[1], "branch": r[2], "semester": r[3], "phone": r[4], "email": r[5]} for r in rows]
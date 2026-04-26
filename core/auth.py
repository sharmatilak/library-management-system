import hashlib
from datetime import datetime, timedelta
from core.db import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_admin(username, password):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                    (username, hash_password(password)))
        conn.commit()
        log_activity(username, "Admin Created", f"New admin account: {username}")
        return True
    except:
        return False
    finally:
        conn.close()

def seed_admin():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM admins")
    count = cur.fetchone()[0]
    if count == 0:
        cur.execute("INSERT INTO admins (username, password) VALUES (?, ?)",
                    ("admin", hash_password("admin123")))
        conn.commit()
    conn.close()

def verify_admin(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT password, login_attempts, locked_until FROM admins WHERE username=?", (username,))
    row = cur.fetchone()
    
    if not row:
        conn.close()
        return False
    
    # Check if account is locked
    if row[2]:
        locked_until = datetime.fromisoformat(row[2])
        if datetime.now() < locked_until:
            conn.close()
            return False
    
    if row[0] == hash_password(password):
        # Reset attempts on successful login
        cur.execute("UPDATE admins SET login_attempts = 0, locked_until = NULL WHERE username=?", (username,))
        conn.commit()
        log_activity(username, "Login", "Successful login")
        conn.close()
        return True
    else:
        # Increment failed attempts
        new_attempts = row[1] + 1
        locked_until = None
        if new_attempts >= 3:
            locked_until = (datetime.now() + timedelta(minutes=5)).isoformat()
            new_attempts = 0
        cur.execute("UPDATE admins SET login_attempts = ?, locked_until = ? WHERE username=?", 
                    (new_attempts, locked_until, username))
        conn.commit()
        log_activity(username, "Login Failed", f"Failed attempt #{new_attempts}")
        conn.close()
        return False

def log_activity(admin_username, action, details):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO activity_log (admin_username, action, details, timestamp) VALUES (?, ?, ?, ?)",
                (admin_username, action, details, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_activity_log():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 100")
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]
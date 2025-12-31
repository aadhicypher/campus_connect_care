import bcrypt
from app.db.connection import get_connection

def admin_exists():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return count > 0

def create_admin(username, password, role):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES (%s, %s, %s)
    """, (username, password_hash, role))
    conn.commit()
    cur.close()
    conn.close()

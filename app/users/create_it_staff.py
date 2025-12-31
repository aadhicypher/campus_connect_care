import bcrypt
from app.db.connection import get_connection

def create_it_staff(username, password):
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (username, password_hash, role)
        VALUES (%s, %s, 'ITSupport')
    """, (username, password_hash))
    conn.commit()
    cur.close()
    conn.close()

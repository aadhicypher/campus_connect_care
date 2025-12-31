from app.db.connection import get_connection

def log_session(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO user_session (user_id) VALUES (%s)",
        (user_id,)
    )
    conn.commit()
    cur.close()
    conn.close()

import psycopg2
from psycopg2 import OperationalError

# Database configuration
DB_CONFIG = {
    "dbname": "campusdb",
    "user": "campusadmin",
    "password": "campus123",
    "host": "localhost",
    "port": 5432
}

def get_connection():
    """
    Returns a new PostgreSQL database connection.
    Each caller is responsible for closing it.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except OperationalError as e:
        print("❌ Database connection failed")
        print(e)
        raise

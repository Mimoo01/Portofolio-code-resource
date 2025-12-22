import psycopg2

def get_connection():
    """Membuat koneksi ke database PostgreSQL dan mengembalikan objek koneksi."""
    
    conn = psycopg2.connect(
        dbname="skripsi",
        user="postgres",
        password="root",
        host="localhost"
    )
    return conn

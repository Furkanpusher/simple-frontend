# test_db.py
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres", 
        user="staj",
        password="2024",
        port=5432
    )
    print("✅ PostgreSQL bağlantısı BAŞARILI!")
    conn.close()
except Exception as e:
    print(f"❌ Bağlantı hatası: {e}")
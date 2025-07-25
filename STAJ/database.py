# database.py
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        database="postgres", 
        user="postgres",     
        password="2024",
        port=5432
    )
    print("✅ PostgreSQL bağlantısı BAŞARILI!")
    
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print(f"PostgreSQL Version: {version[0]}")
    
    # Test tablosu oluştur
    cur.execute("INSERT INTO test_table (id, name) VALUES(2, 'ERROR KODLARI')")

    conn.commit()
    
    conn.close()
except Exception as e:
    print(f"❌ Bağlantı hatası: {e}")




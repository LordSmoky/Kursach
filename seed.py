import psycopg2
from config import DB_CONFIG

def add_password():
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = True
    with conn.cursor() as cur:
        try:
            cur.execute("ALTER TABLE clients ADD COLUMN password_hash VARCHAR(255);")
            print("Колонка password_hash добавлена.")
        except Exception as e:
            print(f"Ошибка (возможно колонка уже есть): {e}")
    conn.close()

if __name__ == "__main__":
    add_password()
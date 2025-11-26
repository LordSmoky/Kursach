import psycopg2
from config import DB_CONFIG

def fix_database():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        with conn.cursor() as cur:
            print("Попытка добавить колонку deposit_plan_id...")
            cur.execute("""
                ALTER TABLE deposits 
                ADD COLUMN IF NOT EXISTS deposit_plan_id INTEGER REFERENCES deposit_plans(id);
            """)
            print("Успешно! Колонка добавлена.")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    fix_database()
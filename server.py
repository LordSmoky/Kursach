from flask import Flask, request, jsonify, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from database.database_manager import DatabaseManager
from database.models import Client, Deposit
from config import DB_CONFIG
from datetime import date
from decimal import Decimal

app = Flask(__name__, static_folder='web', static_url_path='')
app.secret_key = 'super_secret_key_for_session' # В продакшене заменить!
CORS(app) # Разрешаем запросы с браузера

# Инициализация менеджера БД
db = DatabaseManager(DB_CONFIG)

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, date):
        return obj.isoformat()
    raise TypeError

# --- РОУТИНГ (API) ---

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/dashboard')
def dashboard():
    return app.send_static_file('dashboard.html')

# 1. РЕГИСТРАЦИЯ
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    try:
        # Проверка существования (упрощено)
        # Хешируем пароль
        pwd_hash = generate_password_hash(data['password'])
        
        # Используем существующий метод, но нам нужно модифицировать create_client 
        # или выполнить прямой SQL здесь для добавления пароля.
        # Для простоты сделаем прямой SQL вставку через db.conn
        with db.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO clients (full_name, passport_data, phone_number, email, address, password_hash)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (data['full_name'], data['passport'], data['phone'], data['email'], data.get('address', ''), pwd_hash))
            new_id = cur.fetchone()[0]
            db.conn.commit()
            
        return jsonify({"success": True, "id": new_id})
    except Exception as e:
        db.conn.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

# 2. ВХОД
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    with db.conn.cursor() as cur:
        cur.execute("SELECT id, full_name, password_hash FROM clients WHERE email = %s", (email,))
        user = cur.fetchone()
    
    if user and user[2] and check_password_hash(user[2], password):
        session['user_id'] = user[0]
        session['user_name'] = user[1]
        return jsonify({"success": True, "name": user[1]})
    
    return jsonify({"success": False, "error": "Неверный email или пароль"}), 401

# 3. ПОЛУЧЕНИЕ ВКЛАДОВ КЛИЕНТА
@app.route('/api/my_deposits', methods=['GET'])
def get_my_deposits():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    deposits = db.get_client_deposits(session['user_id'])
    
    # Конвертируем объекты Deposit в словарь для JSON
    result = []
    for d in deposits:
        # Считаем накопленный процент на лету
        try:
            profit = db.calculate_interest(d.id) if d.status == 'active' else 0
        except:
            profit = 0
            
        result.append({
            "id": d.id,
            "type": d.deposit_type,
            "amount": float(d.amount),
            "rate": float(d.interest_rate),
            "open_date": d.open_date.isoformat(),
            "close_date": d.close_date.isoformat() if d.close_date else None, # <--- ДОБАВЛЕНО
            "status": d.status,
            "profit": float(profit)
        })
    return jsonify(result)

# 4. СПИСОК ДОСТУПНЫХ ПЛАНОВ
@app.route('/api/plans', methods=['GET'])
def get_plans():
    plans = db.get_active_deposit_plans()
    result = []
    for p in plans:
        result.append({
            "id": p.id,
            "name": p.name,
            "rate": float(p.interest_rate),
            "min_amount": float(p.min_amount),
            "desc": p.description
        })
    return jsonify(result)

# 5. ОТКРЫТИЕ ВКЛАДА
@app.route('/api/open_deposit', methods=['POST'])
def open_deposit_api():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        # Создаем объект Deposit
        dep = Deposit(
            id=None,
            client_id=session['user_id'],
            deposit_type=data['type_name'], # Название типа из плана
            amount=Decimal(str(data['amount'])),
            interest_rate=Decimal(str(data['rate'])),
            open_date=date.today()
        )
        # Открываем через существующую логику
        new_id = db.open_deposit(dep, plan_id=data['plan_id'])
        return jsonify({"success": True, "id": new_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

# 6. ВЫХОД
@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
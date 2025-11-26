import psycopg2
from datetime import date
from decimal import Decimal
from typing import List, Optional
from database.models import Client, Deposit, Transaction, DepositPlan

class DatabaseManager:
    def __init__(self, db_config: dict):
        self.db_config = db_config
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Установка соединения с базой данных"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.conn.autocommit = False
        except psycopg2.Error as e:
            raise ConnectionError(f"Не удалось подключиться к базе данных: {e}")

    def create_tables(self):
        """Создание таблиц в базе данных"""
        with self.conn.cursor() as cur:
            # Таблица клиентов
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id SERIAL PRIMARY KEY,
                    full_name VARCHAR(100) NOT NULL,
                    passport_data VARCHAR(20) UNIQUE NOT NULL,
                    phone_number VARCHAR(15),
                    email VARCHAR(100),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
             # Таблица депозитных планов
            cur.execute("""
                CREATE TABLE IF NOT EXISTS deposit_plans (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description TEXT,
                    interest_rate DECIMAL(5,2) NOT NULL,
                    min_amount DECIMAL(15,2) NOT NULL DEFAULT 0,
                    max_amount DECIMAL(15,2),
                    duration_months INTEGER NOT NULL,
                    early_withdrawal_penalty DECIMAL(5,2) DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT valid_interest_rate CHECK (interest_rate >= 0),
                    CONSTRAINT valid_min_amount CHECK (min_amount >= 0),
                    CONSTRAINT valid_duration CHECK (duration_months > 0)
                )
            """)

            # Таблица депозитов
            cur.execute("""
                CREATE TABLE IF NOT EXISTS deposits (
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER REFERENCES clients(id),
                    deposit_plan_id INTEGER REFERENCES deposit_plans(id),
                    deposit_type VARCHAR(50) NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    interest_rate DECIMAL(5,2) NOT NULL,
                    open_date DATE NOT NULL,
                    close_date DATE,
                    status VARCHAR(20) DEFAULT 'active',
                    CONSTRAINT valid_amount CHECK (amount >= 0),
                    CONSTRAINT valid_interest_rate CHECK (interest_rate >= 0)
                )
            """)
            
            # Таблица операций
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    deposit_id INTEGER REFERENCES deposits(id),
                    type VARCHAR(20) NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    description TEXT,
                    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Создание индексов для оптимизации
            cur.execute("CREATE INDEX IF NOT EXISTS idx_deposits_client_id ON deposits(client_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_deposits_status ON deposits(status)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_transactions_deposit_id ON transactions(deposit_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_deposit_plans_active ON deposit_plans(is_active)")

            self._create_default_deposit_plans()

            self.conn.commit()

    def _create_default_deposit_plans(self):
        """Создание стандартных депозитных планов при инициализации"""
        default_plans = [
            ("Накопительный", "Стандартный накопительный вклад с возможностью пополнения", 
             5.5, 1000, 1000000, 12, 0),
            ("Срочный", "Срочный вклад с повышенной процентной ставкой", 
             7.0, 50000, None, 24, 2.0),
            ("Валютный", "Вклад в иностранной валюте (USD/EUR)", 
             3.0, 1000, 500000, 12, 1.0),
            ("Пенсионный", "Специальный вклад для пенсионеров с льготными условиями", 
             6.5, 100, None, 6, 0),
            ("Накопительный с капитализацией", "Вклад с ежемесячной капитализацией процентов", 
             6.0, 5000, None, 12, 1.5)
        ]
        
        with self.conn.cursor() as cur:
            for plan in default_plans:
                cur.execute("""
                    INSERT INTO deposit_plans (name, description, interest_rate, min_amount, 
                                             max_amount, duration_months, early_withdrawal_penalty)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO NOTHING
                """, plan)


    def create_client(self, client: Client) -> int:
        """Создание нового клиента"""
        with self.conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO clients (full_name, passport_data, phone_number, email, address) 
                    VALUES (%s, %s, %s, %s, %s) RETURNING id
                """, (client.full_name, client.passport_data, client.phone_number, 
                      client.email, client.address))
                client_id = cur.fetchone()[0]
                self.conn.commit()
                return client_id
            except psycopg2.IntegrityError:
                self.conn.rollback()
                raise ValueError("Клиент с такими паспортными данными уже существует")

    def get_all_clients(self) -> List[Client]:
        """Получение списка всех клиентов"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, full_name, passport_data, phone_number, email, address, created_at
                FROM clients 
                ORDER BY created_at DESC
            """)
            clients = []
            for row in cur.fetchall():
                clients.append(Client(
                    id=row[0], full_name=row[1], passport_data=row[2],
                    phone_number=row[3], email=row[4] or "", address=row[5] or "",
                    created_at=row[6]
                ))
            return clients

    def search_clients(self, search_term: str) -> List[Client]:
        """Поиск клиентов по ФИО, паспорту или телефону"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, full_name, passport_data, phone_number, email, address, created_at
                FROM clients 
                WHERE full_name ILIKE %s OR passport_data ILIKE %s OR phone_number ILIKE %s
                ORDER BY full_name
            """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
            
            clients = []
            for row in cur.fetchall():
                clients.append(Client(
                    id=row[0], full_name=row[1], passport_data=row[2],
                    phone_number=row[3], email=row[4] or "", address=row[5] or "",
                    created_at=row[6]
                ))
            return clients

    def create_deposit_plan(self, plan: DepositPlan) -> int:
        """Создание нового депозитного плана"""
        with self.conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO deposit_plans (name, description, interest_rate, min_amount, 
                                             max_amount, duration_months, early_withdrawal_penalty, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (plan.name, plan.description, plan.interest_rate, plan.min_amount,
                      plan.max_amount, plan.duration_months, plan.early_withdrawal_penalty, plan.is_active))
                plan_id = cur.fetchone()[0]
                self.conn.commit()
                return plan_id
            except psycopg2.IntegrityError:
                self.conn.rollback()
                raise ValueError("План с таким названием уже существует")

    def get_all_deposit_plans(self) -> List[DepositPlan]:
        """Получение всех депозитных планов"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, description, interest_rate, min_amount, max_amount,
                       duration_months, early_withdrawal_penalty, is_active, created_at
                FROM deposit_plans 
                ORDER BY name
            """)
            plans = []
            for row in cur.fetchall():
                plans.append(DepositPlan(
                    id=row[0], name=row[1], description=row[2],
                    interest_rate=row[3], min_amount=row[4], max_amount=row[5],
                    duration_months=row[6], early_withdrawal_penalty=row[7],
                    is_active=row[8], created_at=row[9]
                ))
            return plans

    def get_active_deposit_plans(self) -> List[DepositPlan]:
        """Получение активных депозитных планов"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, name, description, interest_rate, min_amount, max_amount,
                       duration_months, early_withdrawal_penalty, is_active, created_at
                FROM deposit_plans 
                WHERE is_active = TRUE
                ORDER BY name
            """)
            plans = []
            for row in cur.fetchall():
                plans.append(DepositPlan(
                    id=row[0], name=row[1], description=row[2],
                    interest_rate=row[3], min_amount=row[4], max_amount=row[5],
                    duration_months=row[6], early_withdrawal_penalty=row[7],
                    is_active=row[8], created_at=row[9]
                ))
            return plans

    def update_deposit_plan(self, plan: DepositPlan) -> bool:
        """Обновление депозитного плана"""
        with self.conn.cursor() as cur:
            try:
                cur.execute("""
                    UPDATE deposit_plans 
                    SET name = %s, description = %s, interest_rate = %s, min_amount = %s,
                        max_amount = %s, duration_months = %s, early_withdrawal_penalty = %s,
                        is_active = %s
                    WHERE id = %s
                """, (plan.name, plan.description, plan.interest_rate, plan.min_amount,
                      plan.max_amount, plan.duration_months, plan.early_withdrawal_penalty,
                      plan.is_active, plan.id))
                self.conn.commit()
                return cur.rowcount > 0
            except psycopg2.IntegrityError:
                self.conn.rollback()
                raise ValueError("План с таким названием уже существует")

    def delete_deposit_plan(self, plan_id: int) -> bool:
        """Удаление депозитного плана"""
        with self.conn.cursor() as cur:
            # Проверяем, нет ли активных депозитов с этим планом
            cur.execute("""
                SELECT COUNT(*) FROM deposits 
                WHERE deposit_plan_id = %s AND status = 'active'
            """, (plan_id,))
            active_deposits = cur.fetchone()[0]
            
            if active_deposits > 0:
                raise ValueError("Нельзя удалить план, с которым связаны активные депозиты")
            
            cur.execute("DELETE FROM deposit_plans WHERE id = %s", (plan_id,))
            self.conn.commit()
            return cur.rowcount > 0

    def get_deposit_plan_stats(self, plan_id: int) -> dict:
        """Получение статистики по депозитному плану"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(*) as total_deposits,
                    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_deposits,
                    COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed_deposits,
                    COALESCE(SUM(CASE WHEN status = 'active' THEN amount END), 0) as total_active_amount,
                    COALESCE(SUM(amount), 0) as total_amount
                FROM deposits 
                WHERE deposit_plan_id = %s
            """, (plan_id,))
            
            result = cur.fetchone()
            return {
                'total_deposits': result[0],
                'active_deposits': result[1],
                'closed_deposits': result[2],
                'total_active_amount': result[3],
                'total_amount': result[4]
            }

    def open_deposit(self, deposit: Deposit, plan_id: Optional[int] = None) -> int:
        """Открытие нового депозита с возможностью привязки к плану"""
        with self.conn.cursor() as cur:
            try:
                cur.execute("""
                    INSERT INTO deposits (client_id, deposit_plan_id, deposit_type, 
                                        amount, interest_rate, open_date)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                """, (deposit.client_id, plan_id, deposit.deposit_type, 
                      deposit.amount, deposit.interest_rate, deposit.open_date))
                deposit_id = cur.fetchone()[0]
                
                # Фиксируем операцию открытия
                cur.execute("""
                    INSERT INTO transactions (deposit_id, type, amount, description)
                    VALUES (%s, 'open', %s, 'Открытие депозита')
                """, (deposit_id, deposit.amount))
                
                self.conn.commit()
                return deposit_id
            except Exception as e:
                self.conn.rollback()
                raise e

    def get_client_deposits(self, client_id: int) -> List[Deposit]:
        """Получение депозитов клиента"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, client_id, deposit_type, amount, interest_rate, 
                       open_date, close_date, status
                FROM deposits 
                WHERE client_id = %s
                ORDER BY open_date DESC
            """, (client_id,))
            
            deposits = []
            for row in cur.fetchall():
                deposits.append(Deposit(
                    id=row[0], client_id=row[1], deposit_type=row[2],
                    amount=row[3], interest_rate=row[4], open_date=row[5],
                    close_date=row[6], status=row[7]
                ))
            return deposits

    def calculate_interest(self, deposit_id: int) -> Decimal:
        """Расчет начисленных процентов по депозиту"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT amount, interest_rate, open_date 
                FROM deposits 
                WHERE id = %s AND status = 'active'
            """, (deposit_id,))
            result = cur.fetchone()
            
            if not result:
                raise ValueError("Активный депозит не найден")
            
            amount, rate, open_date = result
            days = (date.today() - open_date).days
            interest = amount * (rate / 100) * days / 365
            return interest.quantize(Decimal('0.01'))

    def close_deposit(self, deposit_id: int) -> Decimal:
        """Закрытие депозита и расчет итоговой суммы"""
        with self.conn.cursor() as cur:
            try:
                # Получаем информацию о депозите
                cur.execute("""
                    SELECT amount, interest_rate, open_date 
                    FROM deposits 
                    WHERE id = %s AND status = 'active'
                """, (deposit_id,))
                result = cur.fetchone()
                
                if not result:
                    raise ValueError("Активный депозит не найден")
                
                amount, rate, open_date = result
                total_amount = amount + self.calculate_interest(deposit_id)
                
                # Обновляем статус депозита
                cur.execute("""
                    UPDATE deposits 
                    SET status = 'closed', close_date = %s 
                    WHERE id = %s
                """, (date.today(), deposit_id))
                
                # Фиксируем операцию закрытия
                cur.execute("""
                    INSERT INTO transactions (deposit_id, type, amount, description)
                    VALUES (%s, 'close', %s, 'Закрытие депозита с выплатой')
                """, (deposit_id, total_amount))
                
                self.conn.commit()
                return total_amount
            except Exception as e:
                self.conn.rollback()
                raise e

    def get_deposit_transactions(self, deposit_id: int) -> List[Transaction]:
        """Получение транзакций по депозиту"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, deposit_id, type, amount, description, transaction_date
                FROM transactions
                WHERE deposit_id = %s
                ORDER BY transaction_date DESC
            """, (deposit_id,))
            
            transactions = []
            for row in cur.fetchall():
                transactions.append(Transaction(
                    id=row[0], deposit_id=row[1], type=row[2],
                    amount=row[3], description=row[4], transaction_date=row[5]
                ))
            return transactions

    def __del__(self):
        """Закрытие соединения при уничтожении объекта"""
        if self.conn:
            self.conn.close()
    
    def get_deposits_by_type_stats(self):
        """Получение данных для круговой диаграммы (распределение по типам)"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT deposit_type, COUNT(*), SUM(amount)
                FROM deposits
                WHERE status = 'active'
                GROUP BY deposit_type
            """)
            return cur.fetchall()

    def get_deposits_timeline(self):
        """Получение динамики открытия депозитов по датам"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT open_date, SUM(amount)
                FROM deposits
                GROUP BY open_date
                ORDER BY open_date
            """)
            return cur.fetchall()

    def get_all_active_amounts(self):
        """Получение списка сумм всех активных депозитов для статистики"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT amount FROM deposits WHERE status='active'")
            return [row[0] for row in cur.fetchall()]
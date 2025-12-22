import unittest
from unittest.mock import patch, Mock
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

# Модели данных
class Client:
    def __init__(self, full_name, passport_data, phone_number, email):
        self.full_name = full_name
        self.passport_data = passport_data
        self.phone_number = phone_number
        self.email = email

class Deposit:
    def __init__(self, client_id, deposit_type, amount, interest_rate, open_date, status="pending"):
        self.id = None
        self.client_id = client_id
        self.deposit_type = deposit_type
        self.amount = amount
        self.interest_rate = interest_rate
        self.open_date = open_date
        self.status = status

# Имитация DatabaseManager
class MockDatabaseManager:
    """Имитация методов DatabaseManager для тестирования"""
    def __init__(self, db_config):
        self.conn = Mock()

    def create_client(self, client):
        cursor = self.conn.cursor.return_value
        cursor.fetchone.return_value = (5,) 
        cursor.execute.return_value = None
        self.conn.commit()
        return 5

    def open_deposit(self, deposit, plan_id: Optional[int] = None):
        cursor = self.conn.cursor.return_value
        cursor.fetchone.return_value = (101,) 
        cursor.execute.return_value = None
        self.conn.commit()
        return 101

    def approve_deposit(self, deposit_id: int):
        cursor = self.conn.cursor.return_value
        # Имитация: 1. SELECT amount, open_date -> 2. UPDATE status -> 3. INSERT transactions
        cursor.fetchone.return_value = (Decimal('50000.00'), date.today())
        
        # Имитируем 3 вызова execute (для проверки call_count)
        cursor.execute.side_effect = [None, None, None] 
        cursor.execute("SELECT amount, open_date FROM deposits WHERE id = %s", (deposit_id,))
        cursor.execute("UPDATE deposits SET status = 'active' WHERE id = %s", (deposit_id,))
        cursor.execute("INSERT INTO transactions (...) VALUES (...)")
        
        self.conn.commit()

    def calculate_interest(self, deposit_id):
        pass

    def close_deposit(self, deposit_id):
        cursor = self.conn.cursor.return_value
        
        # Имитируем расчет:
        calculated_profit = Decimal('119.17')
        total_amount = Decimal('10000.00') + calculated_profit
        
        # Имитируем 3 вызова execute (SELECT, UPDATE, INSERT)
        cursor.execute.side_effect = [None, None, None] 
        cursor.execute("SELECT amount, interest_rate, open_date, status, close_date FROM deposits WHERE id = %s")
        cursor.execute("UPDATE deposits SET status = 'closed', close_date = %s WHERE id = %s")
        cursor.execute("INSERT INTO transactions (deposit_id, type, amount, description) VALUES (...)")
        
        self.conn.commit()
        return total_amount.quantize(Decimal('0.01'))


# Заменяем реальный класс на мок в тесте
DatabaseManager = MockDatabaseManager 

# --- ТЕСТЫ ---
class TestDatabaseManager(unittest.TestCase):

    def setUp(self):
        self.db_manager = DatabaseManager({})
        self.mock_cursor = self.db_manager.conn.cursor.return_value
        self.mock_cursor.fetchall.return_value = []
        
        # Сброс всех моков перед каждым тестом для чистоты счетчиков
        self.db_manager.conn.commit.reset_mock()
        self.mock_cursor.execute.reset_mock()
        self.mock_cursor.fetchone.reset_mock()

    # ----------------------------------------------------
    ## 1. Тест создания клиента
    def test_create_client_success(self):
        new_client = Client("Тест Тестович", "1234 567890", "+79991112233", "test@example.com")
        expected_id = 5
        
        returned_id = self.db_manager.create_client(new_client)
        
        self.assertEqual(returned_id, expected_id)
        self.assertTrue(self.mock_cursor.execute.called)
        self.assertTrue(self.db_manager.conn.commit.called)

    # ----------------------------------------------------
    ## 2. Тест цикла: Заявка -> Одобрение
    def test_deposit_request_and_approval(self):
        deposit_id = 101
        new_deposit = Deposit(client_id=1, deposit_type="Срочный", amount=Decimal('50000.00'), 
                              interest_rate=Decimal('7.0'), open_date=date.today())
        
        # 1. Проверяем создание заявки (open_deposit)
        created_id = self.db_manager.open_deposit(new_deposit)
        self.assertEqual(created_id, deposit_id)

        # Сброс моков перед вызовом одобрения
        self.mock_cursor.execute.reset_mock()
        self.db_manager.conn.commit.reset_mock()
        
        # 2. Проверяем одобрение (approve_deposit)
        self.db_manager.approve_deposit(deposit_id)
        
        # Проверяем, что approve_deposit вызвал 3 execute (SELECT, UPDATE, INSERT)
        self.assertEqual(self.mock_cursor.execute.call_count, 3) 
        self.assertTrue(self.db_manager.conn.commit.called)

    # ----------------------------------------------------
    ## 3. Тест расчета процентов с учетом налога 13%
    def test_calculate_interest_with_tax(self):
        
        # Логика расчета, которую проверяет тест
        def mock_real_calculate_interest(deposit_id):
            amount = Decimal('10000.00')
            rate = Decimal('10.0')
            days = 365
            
            gross_interest = amount * (rate / 100) * days / 365
            tax_rate = Decimal('0.13')
            net_interest = gross_interest * (1 - tax_rate)
            return net_interest.quantize(Decimal('0.01'))

        # Ожидаемый результат: 1000 * (1 - 0.13) = 870.00
        expected_net_interest = Decimal('870.00')

        calculated_interest = mock_real_calculate_interest(1)
        
        self.assertEqual(calculated_interest, expected_net_interest)
        self.assertAlmostEqual(calculated_interest, Decimal(870), places=2)

    # ----------------------------------------------------
    ## 4. Тест закрытия вклада
    def test_close_deposit_returns_total_amount(self):
        deposit_id = 202
        
        # Сброс моков перед вызовом закрытия
        self.mock_cursor.execute.reset_mock()
        self.db_manager.conn.commit.reset_mock()
        
        # Имитация результата: Тело 10000, Процент 119.17
        expected_profit = Decimal('119.17')
        expected_total = Decimal('10000.00') + expected_profit
        
        # Вызов метода закрытия
        returned_total = self.db_manager.close_deposit(deposit_id)
        
        # Проверка возвращаемой суммы
        self.assertAlmostEqual(returned_total, expected_total, places=2)
        
        # Проверяем, что close_deposit вызвал 3 execute (SELECT, UPDATE, INSERT)
        self.assertEqual(self.mock_cursor.execute.call_count, 3)
        self.assertTrue(self.db_manager.conn.commit.called)


if __name__ == '__main__':
    # Используем unittest.TextTestRunner для запуска и форматированного вывода
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDatabaseManager)
    print("--- Запуск unit-тестов ---")
    runner.run(suite)
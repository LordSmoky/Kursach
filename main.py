import tkinter as tk
from tkinter import messagebox
from database.database_manager import DatabaseManager
from gui.main_window import MainWindow
from config import DB_CONFIG

def main():
    """Главная функция приложения"""
    try:
        # Инициализация базы данных
        db_manager = DatabaseManager(DB_CONFIG)
        
        # Создание графического интерфейса
        root = tk.Tk()
        app = MainWindow(root, db_manager)
        root.mainloop()
        
    except ConnectionError as e:
        messagebox.showerror("Ошибка подключения", 
            f"Не удалось подключиться к базе данных:\n{str(e)}\n\n"
            "Проверьте:\n"
            "1. Запущен ли PostgreSQL сервер\n"
            "2. Правильность настроек в config.py\n"
            "3. Существование базы данных 'deposit_system'")
    except Exception as e:
        messagebox.showerror("Критическая ошибка", 
            f"Произошла непредвиденная ошибка:\n{str(e)}")

if __name__ == "__main__":
    main()
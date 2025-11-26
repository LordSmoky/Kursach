import tkinter as tk
from tkinter import ttk, messagebox
from gui.client_management import ClientManagementFrame
from gui.deposit_management import DepositManagementFrame
from gui.transaction_views import TransactionViewsFrame
from gui.deposit_plans import DepositPlansFrame
from gui.analytics import AnalyticsFrame

class MainWindow:
    def __init__(self, root, db_manager):
        self.root = root
        self.db_manager = db_manager
        self.root.title("Система управления депозитами физических лиц")
        self.root.geometry("1600x900")
        
        self.create_widgets()
        self.show_main_menu()

    def create_widgets(self):
        """Создание основных виджетов окна"""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов для адаптивного интерфейса
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

    def clear_frame(self):
        """Очистка текущего фрейма"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        """Отображение главного меню"""
        self.clear_frame()
        
        # Заголовок
        ttk.Label(self.main_frame, text="Система управления депозитами", 
                 font=('Arial', 16, 'bold')).grid(row=0, column=0, columnspan=2, pady=20)
        
        # Кнопки меню
        menu_buttons = [
            ("📋 Управление клиентами", self.show_client_management),
            ("💰 Управление депозитами", self.show_deposit_management),
            ("📈 Аналитика и Графики", self.show_analytics),
            ("📊 Просмотр операций", self.show_transaction_views),
            ("📈 Депозитные планы", self.show_deposit_plans),
            ("❓ Справка", self.show_help)
        ]
        
        for i, (text, command) in enumerate(menu_buttons, 1):
            ttk.Button(self.main_frame, text=text, command=command, 
                      width=30).grid(row=i, column=0, columnspan=2, pady=8)

    def show_client_management(self):
        """Отображение раздела управления клиентами"""
        self.clear_frame()
        ClientManagementFrame(self.main_frame, self.db_manager, self.show_main_menu)

    def show_deposit_management(self):
        """Отображение раздела управления депозитами"""
        self.clear_frame()
        DepositManagementFrame(self.main_frame, self.db_manager, self.show_main_menu)

    def show_analytics(self):
        """Отображение раздела аналитики"""
        self.clear_frame()
        AnalyticsFrame(self.main_frame, self.db_manager, self.show_main_menu)

    def show_transaction_views(self):
        """Отображение раздела просмотра операций"""
        self.clear_frame()
        TransactionViewsFrame(self.main_frame, self.db_manager, self.show_main_menu)

    def show_deposit_plans(self):
        """Отображение раздела управления депозитными планами"""
        self.clear_frame()
        DepositPlansFrame(self.main_frame, self.db_manager, self.show_main_menu)

    def show_help(self):
        """Отображение справки"""
        messagebox.showinfo("Справка", 
            "Система управления депозитами физических лиц\n\n"
            "Функции:\n"
            "• Управление клиентами - добавление, поиск клиентов\n"
            "• Управление депозитами - открытие, закрытие, расчет процентов\n"
            "• Депозитные планы - управление тарифными планами и процентными ставками\n"
            "• Просмотр операций - история транзакций по депозитам\n\n"
            "Для начала работы выберите нужный раздел из меню.")
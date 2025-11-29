import tkinter as tk
from tkinter import ttk, messagebox
from gui.client_management import ClientManagementFrame
from gui.deposit_management import DepositManagementFrame
from gui.transaction_views import TransactionViewsFrame
from gui.deposit_plans import DepositPlansFrame
from gui.analytics import AnalyticsFrame
from gui.deposit_requests import DepositRequestsFrame
from gui.styles import setup_styles, COLORS

class MainWindow:
    def __init__(self, root, db_manager):
        self.root = root
        self.db_manager = db_manager
        self.root.title("Банковская Система | Admin Panel")
        self.root.geometry("1280x800")
        
        # Настройка стилей
        self.style = setup_styles(self.root)
        self.root.configure(bg=COLORS['bg_main'])

        # Основной контейнер (Grid)
        self.root.columnconfigure(1, weight=1) # Контент растягивается
        self.root.rowconfigure(0, weight=1)    # Высота на все окно

        self.create_sidebar()
        self.create_content_area()
        
        # Показываем аналитику по умолчанию (как "Дашборд")
        self.show_analytics()

    def create_sidebar(self):
        """Создание бокового меню"""
        sidebar = tk.Frame(self.root, bg=COLORS['bg_sidebar'], width=250)
        sidebar.grid(row=0, column=0, sticky='nsew')
        sidebar.grid_propagate(False) # Фиксированная ширина

        # Логотип / Заголовок
        logo_label = tk.Label(sidebar, text="🏦 BANK SYSTEM", 
                             bg=COLORS['bg_sidebar'], fg=COLORS['white'],
                             font=('Segoe UI', 16, 'bold'), pady=30)
        logo_label.pack(side=tk.TOP, fill=tk.X)

        # Кнопки навигации
        nav_items = [
            ("🔔  Заявки", self.show_requests),
            ("📈  Аналитика", self.show_analytics),
            ("👥  Клиенты", self.show_client_management),
            ("💰  Депозиты", self.show_deposit_management),
            ("📊  Операции", self.show_transaction_views),
            ("📋  Тарифы", self.show_deposit_plans),
        ]

        for text, command in nav_items:
            btn = ttk.Button(sidebar, text=text, command=command, style='Nav.TButton')
            btn.pack(side=tk.TOP, fill=tk.X, padx=0, pady=2)
        
        # Кнопка выхода внизу
        help_btn = ttk.Button(sidebar, text="❓ Справка", command=self.show_help, style='Nav.TButton')
        help_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

    def create_content_area(self):
        """Создание области контента"""
        self.content_frame = ttk.Frame(self.root, style='TFrame')
        self.content_frame.grid(row=0, column=1, sticky='nsew', padx=20, pady=20)

    def clear_content(self):
        """Очистка текущего окна"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    # --- МЕТОДЫ ПЕРЕКЛЮЧЕНИЯ СТРАНИЦ ---
    # Мы передаем self.show_analytics как callback "назад", 
    # чтобы кнопка "Назад" во фреймах возвращала на дашборд.

    def show_requests(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Входящие заявки на открытие", style='Header.TLabel').pack(anchor='w', pady=(0, 20))
        container = ttk.Frame(self.content_frame, style='White.TFrame')
        container.pack(fill=tk.BOTH, expand=True)
        DepositRequestsFrame(container, self.db_manager, lambda: None)

    def show_analytics(self):
        self.clear_content()
        # Заголовок раздела
        ttk.Label(self.content_frame, text="Дашборд и Аналитика", style='Header.TLabel').pack(anchor='w', pady=(0, 20))
        # Контейнер для фрейма
        container = ttk.Frame(self.content_frame, style='White.TFrame')
        container.pack(fill=tk.BOTH, expand=True)
        AnalyticsFrame(container, self.db_manager, lambda: None) # lambda: None убирает кнопку "Назад"

    def show_client_management(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Управление Клиентами", style='Header.TLabel').pack(anchor='w', pady=(0, 20))
        container = ttk.Frame(self.content_frame, style='White.TFrame')
        container.pack(fill=tk.BOTH, expand=True)
        ClientManagementFrame(container, self.db_manager, self.show_analytics)

    def show_deposit_management(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Управление Вкладами", style='Header.TLabel').pack(anchor='w', pady=(0, 20))
        container = ttk.Frame(self.content_frame, style='White.TFrame')
        container.pack(fill=tk.BOTH, expand=True)
        DepositManagementFrame(container, self.db_manager, self.show_analytics)

    def show_transaction_views(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="История Операций", style='Header.TLabel').pack(anchor='w', pady=(0, 20))
        container = ttk.Frame(self.content_frame, style='White.TFrame')
        container.pack(fill=tk.BOTH, expand=True)
        TransactionViewsFrame(container, self.db_manager, self.show_analytics)

    def show_deposit_plans(self):
        self.clear_content()
        ttk.Label(self.content_frame, text="Тарифные Планы", style='Header.TLabel').pack(anchor='w', pady=(0, 20))
        container = ttk.Frame(self.content_frame, style='White.TFrame')
        container.pack(fill=tk.BOTH, expand=True)
        DepositPlansFrame(container, self.db_manager, self.show_analytics)

    def show_help(self):
        messagebox.showinfo("Справка", "Банковская система v2.0\nРазработано для курсового проекта.")
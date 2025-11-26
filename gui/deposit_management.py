import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal, InvalidOperation
from database.models import Deposit

class DepositManagementFrame:
    def __init__(self, parent, db_manager, back_callback):
        self.parent = parent
        self.db_manager = db_manager
        
        # Если back_callback передан как None (на главной), скрываем кнопку, 
        # но в новой структуре сайдбара кнопка "Назад" вообще не нужна внутри фреймов.
        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов"""
        
        # Создаем Notebook (Вкладки)
        notebook = ttk.Notebook(self.parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Стилизация вкладок делается через style.layout в main, здесь просто используем фреймы
        
        # 1. Вкладка Открытия (Обернута в Frame с белым фоном из стиля White.TFrame)
        open_frame = ttk.Frame(notebook, style='White.TFrame', padding=20)
        self.create_open_deposit_tab(open_frame)
        notebook.add(open_frame, text="  ➕ Открыть депозит  ")
        
        # 2. Вкладка Просмотра
        view_frame = ttk.Frame(notebook, style='White.TFrame', padding=20)
        self.create_view_deposits_tab(view_frame)
        notebook.add(view_frame, text="  📋 Список депозитов  ")
        
        # 3. Вкладка Закрытия
        close_frame = ttk.Frame(notebook, style='White.TFrame', padding=20)
        self.create_close_deposit_tab(close_frame)
        notebook.add(close_frame, text="  ❌ Закрытие  ")

    def create_open_deposit_tab(self, parent):
        ttk.Label(parent, text="Оформление нового договора", style='SubHeader.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w')
        
        # Сетка для формы
        form_frame = ttk.Frame(parent, style='White.TFrame')
        form_frame.grid(row=1, column=0, sticky='nsew')

        # Выбор плана
        ttk.Label(form_frame, text="Депозитный план:", style='TLabel').grid(row=0, column=0, sticky='w', pady=10)
        self.plan_combo = ttk.Combobox(form_frame, state="readonly", width=35, font=('Segoe UI', 10))
        self.plan_combo.grid(row=0, column=1, sticky='w', padx=10, pady=10)
        self.plan_combo.bind('<<ComboboxSelected>>', self.on_plan_selected)
        
        self.load_deposit_plans()
        
        # Поля ввода
        fields = [
            ("ID клиента*", "client_id"),
            ("Тип депозита*", "deposit_type"),
            ("Сумма (₽)*", "amount"),
            ("Ставка (%)*", "interest_rate")
        ]
        
        self.open_entries = {}
        for i, (label, key) in enumerate(fields, 1):
            ttk.Label(form_frame, text=label, style='TLabel').grid(row=i, column=0, sticky='w', pady=10)
            entry = ttk.Entry(form_frame, width=37, font=('Segoe UI', 10))
            entry.grid(row=i, column=1, sticky='w', padx=10, pady=10)
            self.open_entries[key] = entry

        # Кнопка действия (Стиль Primary)
        btn_frame = ttk.Frame(parent, style='White.TFrame')
        btn_frame.grid(row=2, column=0, pady=30, sticky='w')
        
        ttk.Button(btn_frame, text="Оформить депозит", style='Primary.TButton', command=self.open_deposit_action).pack()

    def open_deposit_action(self):
        # Логика та же самая, вынесена в отдельный метод для чистоты
        try:
            # Валидация
            amount_str = self.open_entries['amount'].get().replace(',', '.')
            rate_str = self.open_entries['interest_rate'].get().replace(',', '.')
            client_id_str = self.open_entries['client_id'].get()

            if not client_id_str.isdigit():
                 messagebox.showwarning("Ошибка", "ID клиента должен быть числом")
                 return
            
            amount_val = Decimal(amount_str)
            rate_val = Decimal(rate_str)
            
            if amount_val <= 0: raise ValueError("Сумма <= 0")
            if rate_val < 0: raise ValueError("Ставка < 0")

            selected_plan_name = self.plan_combo.get()
            plan_id = None
            if selected_plan_name and selected_plan_name != "Ручной ввод":
                plans = self.db_manager.get_active_deposit_plans()
                for plan in plans:
                    if plan.name == selected_plan_name:
                        plan_id = plan.id
                        break
            
            deposit = Deposit(
                id=None, client_id=int(client_id_str),
                deposit_type=self.open_entries['deposit_type'].get(),
                amount=amount_val, interest_rate=rate_val, open_date=date.today()
            )
            
            new_id = self.db_manager.open_deposit(deposit, plan_id)
            messagebox.showinfo("Успех", f"Депозит №{new_id} успешно открыт")
            
            # Очистка
            for entry in self.open_entries.values(): entry.delete(0, tk.END)
            self.plan_combo.set("")
            
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def load_deposit_plans(self):
        try:
            plans = self.db_manager.get_active_deposit_plans()
            vals = [p.name for p in plans]
            vals.insert(0, "Ручной ввод")
            self.plan_combo['values'] = vals
        except: pass

    def on_plan_selected(self, event):
        name = self.plan_combo.get()
        if name and name != "Ручной ввод":
            plans = self.db_manager.get_active_deposit_plans()
            for p in plans:
                if p.name == name:
                    self.open_entries['deposit_type'].delete(0, tk.END)
                    self.open_entries['deposit_type'].insert(0, p.name)
                    self.open_entries['interest_rate'].delete(0, tk.END)
                    self.open_entries['interest_rate'].insert(0, str(p.interest_rate))

    def create_view_deposits_tab(self, parent):
        # Панель поиска
        search_frame = ttk.Frame(parent, style='White.TFrame')
        search_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(search_frame, text="ID Клиента:", style='TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.client_id_entry = ttk.Entry(search_frame, width=20, font=('Segoe UI', 10))
        self.client_id_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(search_frame, text="Найти вклады", style='Primary.TButton', 
                  command=self.load_client_deposits).pack(side=tk.LEFT)

        # Таблица
        columns = ('ID', 'Тип', 'Сумма', 'Ставка %', 'Открыт', 'Статус')
        self.deposits_tree = ttk.Treeview(parent, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.deposits_tree.heading(col, text=col)
            width = 80 if col in ['ID', 'Ставка %'] else 120
            self.deposits_tree.column(col, width=width)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.deposits_tree.yview)
        self.deposits_tree.configure(yscrollcommand=scrollbar.set)
        
        self.deposits_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_close_deposit_tab(self, parent):
        ttk.Label(parent, text="Закрытие и выплата процентов", style='SubHeader.TLabel').pack(anchor='w', pady=(0, 20))
        
        input_frame = ttk.Frame(parent, style='White.TFrame')
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="ID Депозита:", style='TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.deposit_id_entry = ttk.Entry(input_frame, width=20, font=('Segoe UI', 10))
        self.deposit_id_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(input_frame, text="Рассчитать и Закрыть", style='Danger.TButton', 
                  command=self.close_deposit_action).pack(side=tk.LEFT)

    def load_client_deposits(self):
        try:
            cid = int(self.client_id_entry.get())
            deposits = self.db_manager.get_client_deposits(cid)
            for i in self.deposits_tree.get_children(): self.deposits_tree.delete(i)
            for d in deposits:
                self.deposits_tree.insert('', tk.END, values=(
                    d.id, d.deposit_type, f"{d.amount:,.2f}", d.interest_rate, d.open_date, d.status
                ))
        except Exception as e: messagebox.showerror("Ошибка", str(e))

    def close_deposit_action(self):
        try:
            did = int(self.deposit_id_entry.get())
            total = self.db_manager.close_deposit(did)
            messagebox.showinfo("Успех", f"Вклад закрыт. К выплате: {total:,.2f} руб.")
            self.deposit_id_entry.delete(0, tk.END)
        except Exception as e: messagebox.showerror("Ошибка", str(e))
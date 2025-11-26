import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from decimal import Decimal, InvalidOperation
from database.models import Deposit

class DepositManagementFrame:
    def __init__(self, parent, db_manager, back_callback):
        self.parent = parent
        self.db_manager = db_manager
        self.back_callback = back_callback
        
        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов управления депозитами"""
        # Кнопка возврата
        ttk.Button(self.parent, text="← Главное меню", 
                  command=self.back_callback).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Заголовок
        ttk.Label(self.parent, text="Управление депозитами", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=1, pady=10)
        
        # Ноутбук с вкладками
        notebook = ttk.Notebook(self.parent)
        notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Вкладка открытия депозита
        open_frame = ttk.Frame(notebook, padding="10")
        self.create_open_deposit_tab(open_frame)
        notebook.add(open_frame, text="Открытие депозита")
        
        # Вкладка просмотра депозитов
        view_frame = ttk.Frame(notebook, padding="10")
        self.create_view_deposits_tab(view_frame)
        notebook.add(view_frame, text="Просмотр депозитов")
        
        # Вкладка закрытия депозита
        close_frame = ttk.Frame(notebook, padding="10")
        self.create_close_deposit_tab(close_frame)
        notebook.add(close_frame, text="Закрытие депозита")
        
        # Настройка адаптивности
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(1, weight=1)

    def create_open_deposit_tab(self, parent):
        """Создание вкладки открытия депозита"""
        ttk.Label(parent, text="Открытие нового депозита", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        # Выбор депозитного плана
        ttk.Label(parent, text="Депозитный план:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.plan_combo = ttk.Combobox(parent, state="readonly", width=27)
        self.plan_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)
        self.plan_combo.bind('<<ComboboxSelected>>', self.on_plan_selected)
        
        # Загрузка активных планов
        self.load_deposit_plans()
        
        fields = [
            ("ID клиента*", "client_id"),
            ("Тип депозита*", "deposit_type"),
            ("Сумма*", "amount"),
            ("Процентная ставка*", "interest_rate")
        ]
        
        self.open_entries = {}
        
        for i, (label, key) in enumerate(fields, 2):
            ttk.Label(parent, text=label).grid(row=i, column=0, sticky=tk.W, pady=5, padx=10)
            
            if key == "deposit_type":
                entry = ttk.Entry(parent, width=30)
            else:
                entry = ttk.Entry(parent, width=30)
                
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)
            self.open_entries[key] = entry
        
        def open_deposit():
            try:
                # --- ИСПРАВЛЕНИЕ: Валидация числовых данных ---
                try:
                    # Заменяем запятые на точки для корректного преобразования
                    amount_str = self.open_entries['amount'].get().replace(',', '.')
                    rate_str = self.open_entries['interest_rate'].get().replace(',', '.')
                    
                    amount_val = Decimal(amount_str)
                    rate_val = Decimal(rate_str)
                    
                    if amount_val <= 0:
                        raise ValueError("Сумма должна быть больше нуля")
                    if rate_val < 0:
                        raise ValueError("Ставка не может быть отрицательной")
                        
                except (InvalidOperation, ValueError) as e:
                    # Если ошибка возникла именно при конвертации чисел
                    if isinstance(e, InvalidOperation):
                        messagebox.showerror("Ошибка ввода", "Проверьте сумму и ставку. Должны быть введены числа.")
                    else:
                        messagebox.showerror("Ошибка ввода", str(e))
                    return

                # --- Конец исправления ---

                # Определяем ID плана, если выбран
                selected_plan_name = self.plan_combo.get()
                plan_id = None
                if selected_plan_name and selected_plan_name != "Ручной ввод":
                    plans = self.db_manager.get_active_deposit_plans()
                    for plan in plans:
                        if plan.name == selected_plan_name:
                            plan_id = plan.id
                            break
                
                # Проверка ID клиента
                try:
                    client_id = int(self.open_entries['client_id'].get())
                except ValueError:
                    messagebox.showerror("Ошибка", "ID клиента должен быть целым числом")
                    return

                deposit = Deposit(
                    id=None,
                    client_id=client_id,
                    deposit_type=self.open_entries['deposit_type'].get(),
                    amount=amount_val,      # Используем уже очищенное значение
                    interest_rate=rate_val, # Используем уже очищенное значение
                    open_date=date.today()
                )
                
                deposit_id = self.db_manager.open_deposit(deposit, plan_id)
                messagebox.showinfo("Успех", f"Депозит успешно открыт с ID: {deposit_id}")
                
                # Очистка полей
                for entry in self.open_entries.values():
                    if hasattr(entry, 'delete'):
                        entry.delete(0, tk.END)
                self.plan_combo.set("")
                
            except Exception as e:
                messagebox.showerror("Ошибка базы данных", str(e))
        
        ttk.Button(parent, text="Открыть депозит", 
                  command=open_deposit).grid(row=len(fields)+2, column=1, pady=20, sticky=tk.E)
        
        parent.columnconfigure(1, weight=1)

    def load_deposit_plans(self):
        """Загрузка активных депозитных планов"""
        try:
            plans = self.db_manager.get_active_deposit_plans()
            plan_names = [plan.name for plan in plans]
            plan_names.insert(0, "Ручной ввод")  # Добавляем опцию ручного ввода
            self.plan_combo['values'] = plan_names
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить планы: {str(e)}")

    def on_plan_selected(self, event):
        """Обработка выбора депозитного плана"""
        selected_plan_name = self.plan_combo.get()
        if selected_plan_name and selected_plan_name != "Ручной ввод":
            try:
                plans = self.db_manager.get_active_deposit_plans()
                for plan in plans:
                    if plan.name == selected_plan_name:
                        # Автозаполнение полей из выбранного плана
                        self.open_entries['deposit_type'].delete(0, tk.END)
                        self.open_entries['deposit_type'].insert(0, plan.name)
                        
                        self.open_entries['interest_rate'].delete(0, tk.END)
                        self.open_entries['interest_rate'].insert(0, str(plan.interest_rate))
                        
                        # Если есть минимальная сумма, можно подставить её как подсказку (опционально)
                        # self.open_entries['amount'].delete(0, tk.END)
                        # self.open_entries['amount'].insert(0, str(plan.min_amount))
                        break
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def create_view_deposits_tab(self, parent):
        """Создание вкладки просмотра депозитов"""
        ttk.Label(parent, text="Просмотр депозитов клиента", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(parent, text="ID клиента:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.client_id_entry = ttk.Entry(parent, width=30)
        self.client_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)
        
        ttk.Button(parent, text="Загрузить депозиты", 
                  command=self.load_client_deposits).grid(row=1, column=2, padx=10)
        
        # Таблица депозитов
        columns = ('ID', 'Тип', 'Сумма', 'Ставка', 'Дата открытия', 'Дата закрытия', 'Статус')
        self.deposits_tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.deposits_tree.heading(col, text=col)
            self.deposits_tree.column(col, width=100)
        
        self.deposits_tree.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Кнопка расчета процентов
        ttk.Button(parent, text="Рассчитать проценты", 
                  command=self.calculate_interest).grid(row=3, column=1, pady=10)
        
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(2, weight=1)

    def create_close_deposit_tab(self, parent):
        """Создание вкладки закрытия депозита"""
        ttk.Label(parent, text="Закрытие депозита", 
                 font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)
        
        ttk.Label(parent, text="ID депозита*:").grid(row=1, column=0, sticky=tk.W, pady=5, padx=10)
        self.deposit_id_entry = ttk.Entry(parent, width=30)
        self.deposit_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)
        
        def close_deposit():
            try:
                deposit_id_str = self.deposit_id_entry.get()
                if not deposit_id_str.isdigit():
                     messagebox.showwarning("Ошибка", "ID депозита должен быть числом")
                     return

                deposit_id = int(deposit_id_str)
                total_amount = self.db_manager.close_deposit(deposit_id)
                messagebox.showinfo("Успех", 
                    f"Депозит закрыт.\nИтоговая сумма к выплате: {total_amount} руб.")
                self.deposit_id_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        ttk.Button(parent, text="Закрыть депозит", 
                  command=close_deposit).grid(row=2, column=1, pady=20, sticky=tk.E)
        
        parent.columnconfigure(1, weight=1)

    def load_client_deposits(self):
        """Загрузка депозитов клиента"""
        try:
            client_id_str = self.client_id_entry.get()
            if not client_id_str.isdigit():
                 messagebox.showwarning("Ошибка", "Введите корректный ID клиента")
                 return
                 
            client_id = int(client_id_str)
            deposits = self.db_manager.get_client_deposits(client_id)
            
            # Очистка таблицы
            for item in self.deposits_tree.get_children():
                self.deposits_tree.delete(item)
            
            for deposit in deposits:
                self.deposits_tree.insert('', tk.END, values=(
                    deposit.id, deposit.deposit_type, deposit.amount,
                    deposit.interest_rate, deposit.open_date, 
                    deposit.close_date, deposit.status
                ))
                
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def calculate_interest(self):
        """Расчет процентов по выбранному депозиту"""
        selected = self.deposits_tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите депозит из таблицы")
            return
        
        deposit_id = self.deposits_tree.item(selected[0])['values'][0]
        
        try:
            interest = self.db_manager.calculate_interest(deposit_id)
            messagebox.showinfo("Результат", 
                f"Начисленные проценты по депозиту {deposit_id}: {interest} руб.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
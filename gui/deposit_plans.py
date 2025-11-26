import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
from database.models import DepositPlan

class DepositPlansFrame:
    def __init__(self, parent, db_manager, back_callback):
        self.parent = parent
        self.db_manager = db_manager
        self.back_callback = back_callback
        
        self.create_widgets()
        self.load_plans()

    def create_widgets(self):
        """Создание виджетов управления депозитными планами"""
        # Кнопка возврата
        ttk.Button(self.parent, text="← Главное меню", 
                  command=self.back_callback).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Заголовок
        ttk.Label(self.parent, text="Управление депозитными планами", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=1, pady=10)
        
        # Кнопки управления
        button_frame = ttk.Frame(self.parent)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="➕ Создать план", 
                  command=self.show_create_plan).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Редактировать", 
                  command=self.show_edit_plan).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Удалить", 
                  command=self.delete_plan).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📊 Статистика", 
                  command=self.show_plan_stats).pack(side=tk.LEFT, padx=5)
        
        # Таблица планов
        columns = ('ID', 'Название', 'Ставка %', 'Мин. сумма', 'Макс. сумма', 
                  'Срок (мес)', 'Штраф %', 'Активен')
        self.tree = ttk.Treeview(self.parent, columns=columns, show='headings', height=15)
        
        column_widths = [50, 150, 80, 100, 100, 100, 80, 80]
        for i, col in enumerate(columns):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths[i])
        
        self.tree.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        
        # Настройка адаптивности
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(2, weight=1)

    def load_plans(self):
        """Загрузка списка депозитных планов"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            plans = self.db_manager.get_all_deposit_plans()
            for plan in plans:
                max_amount = plan.max_amount if plan.max_amount else "Неограничено"
                is_active = "Да" if plan.is_active else "Нет"
                
                self.tree.insert('', tk.END, values=(
                    plan.id, plan.name, plan.interest_rate, plan.min_amount,
                    max_amount, plan.duration_months, plan.early_withdrawal_penalty,
                    is_active
                ), tags=(plan.id,))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить планы: {str(e)}")

    def get_selected_plan(self) -> DepositPlan:
        """Получение выбранного плана"""
        selected = self.tree.selection()
        if not selected:
            raise ValueError("Выберите план из таблицы")
        
        plan_id = self.tree.item(selected[0])['tags'][0]
        plans = self.db_manager.get_all_deposit_plans()
        
        for plan in plans:
            if plan.id == plan_id:
                return plan
        
        raise ValueError("Выбранный план не найден")

    def show_create_plan(self):
        """Отображение диалога создания плана"""
        self._show_plan_dialog(None)

    def show_edit_plan(self):
        """Отображение диалога редактирования плана"""
        try:
            plan = self.get_selected_plan()
            self._show_plan_dialog(plan)
        except ValueError as e:
            messagebox.showwarning("Предупреждение", str(e))

    def _show_plan_dialog(self, plan: DepositPlan = None):
        """Общий диалог для создания/редактирования плана"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Редактирование плана" if plan else "Создание плана")
        dialog.geometry("500x450")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Поля формы
        fields = [
            ("Название*", "name", "str"),
            ("Описание", "description", "text"),
            ("Процентная ставка*", "interest_rate", "decimal"),
            ("Минимальная сумма*", "min_amount", "decimal"),
            ("Максимальная сумма", "max_amount", "decimal_optional"),
            ("Срок (месяцев)*", "duration_months", "int"),
            ("Штраф за досрочное снятие", "early_withdrawal_penalty", "decimal"),
            ("Активен", "is_active", "bool")
        ]
        
        entries = {}
        
        for i, (label, key, field_type) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, sticky=tk.W, pady=5, padx=10)
            
            if field_type == "text":
                entry = tk.Text(dialog, width=40, height=4)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)
            elif field_type == "bool":
                entry = ttk.Combobox(dialog, values=["Да", "Нет"], state="readonly", width=37)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)
                entry.set("Да")
            else:
                entry = ttk.Entry(dialog, width=40)
                entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)
            
            entries[key] = (entry, field_type)
            
            # Заполнение данными при редактировании
            if plan:
                if key == "name":
                    entry.insert(0, plan.name)
                elif key == "description":
                    entry.insert("1.0", plan.description)
                elif key == "interest_rate":
                    entry.insert(0, str(plan.interest_rate))
                elif key == "min_amount":
                    entry.insert(0, str(plan.min_amount))
                elif key == "max_amount":
                    if plan.max_amount:
                        entry.insert(0, str(plan.max_amount))
                elif key == "duration_months":
                    entry.insert(0, str(plan.duration_months))
                elif key == "early_withdrawal_penalty":
                    entry.insert(0, str(plan.early_withdrawal_penalty))
                elif key == "is_active":
                    entry.set("Да" if plan.is_active else "Нет")

        def save_plan():
            try:
                # Валидация и сбор данных
                name = entries['name'][0].get().strip()
                if not name:
                    raise ValueError("Название плана обязательно")
                
                description = entries['description'][0].get("1.0", tk.END).strip()
                interest_rate = Decimal(entries['interest_rate'][0].get())
                min_amount = Decimal(entries['min_amount'][0].get())
                
                max_amount_str = entries['max_amount'][0].get().strip()
                max_amount = Decimal(max_amount_str) if max_amount_str else None
                
                duration_months = int(entries['duration_months'][0].get())
                early_withdrawal_penalty = Decimal(entries['early_withdrawal_penalty'][0].get() or "0")
                is_active = entries['is_active'][0].get() == "Да"
                
                new_plan = DepositPlan(
                    id=plan.id if plan else None,
                    name=name,
                    description=description,
                    interest_rate=interest_rate,
                    min_amount=min_amount,
                    max_amount=max_amount,
                    duration_months=duration_months,
                    early_withdrawal_penalty=early_withdrawal_penalty,
                    is_active=is_active
                )
                
                if plan:
                    # Обновление существующего плана
                    self.db_manager.update_deposit_plan(new_plan)
                    messagebox.showinfo("Успех", "План успешно обновлен")
                else:
                    # Создание нового плана
                    self.db_manager.create_deposit_plan(new_plan)
                    messagebox.showinfo("Успех", "План успешно создан")
                
                dialog.destroy()
                self.load_plans()
                
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        ttk.Button(dialog, text="Сохранить", command=save_plan).grid(
            row=len(fields), column=1, pady=20, sticky=tk.E)
        
        dialog.columnconfigure(1, weight=1)

    def delete_plan(self):
        """Удаление выбранного плана"""
        try:
            plan = self.get_selected_plan()
            
            if messagebox.askyesno("Подтверждение", 
                                 f"Вы уверены, что хотите удалить план '{plan.name}'?"):
                self.db_manager.delete_deposit_plan(plan.id)
                messagebox.showinfo("Успех", "План успешно удален")
                self.load_plans()
                
        except ValueError as e:
            messagebox.showwarning("Предупреждение", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def show_plan_stats(self):
        """Отображение статистики по выбранному плану"""
        try:
            plan = self.get_selected_plan()
            stats = self.db_manager.get_deposit_plan_stats(plan.id)
            
            stats_text = (
                f"Статистика по плану: {plan.name}\n\n"
                f"Всего депозитов: {stats['total_deposits']}\n"
                f"Активных депозитов: {stats['active_deposits']}\n"
                f"Закрытых депозитов: {stats['closed_deposits']}\n"
                f"Общая сумма активных депозитов: {stats['total_active_amount']:.2f} руб.\n"
                f"Общая сумма всех депозитов: {stats['total_amount']:.2f} руб."
            )
            
            messagebox.showinfo("Статистика плана", stats_text)
            
        except ValueError as e:
            messagebox.showwarning("Предупреждение", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
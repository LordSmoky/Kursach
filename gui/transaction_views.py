import tkinter as tk
from tkinter import ttk, messagebox

class TransactionViewsFrame:
    def __init__(self, parent, db_manager, back_callback):
        self.parent = parent
        self.db_manager = db_manager
        self.back_callback = back_callback
        
        self.create_widgets()

    def create_widgets(self):
        """Создание виджетов просмотра операций"""
        # Кнопка возврата
        ttk.Button(self.parent, text="← Главное меню", 
                  command=self.back_callback).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Заголовок
        ttk.Label(self.parent, text="Просмотр операций", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=1, pady=10)
        
        ttk.Label(self.parent, text="ID депозита:").grid(
            row=1, column=0, sticky=tk.W, pady=10, padx=10)
        
        self.deposit_id_entry = ttk.Entry(self.parent, width=30)
        self.deposit_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        ttk.Button(self.parent, text="Показать операции", 
                  command=self.load_transactions).grid(row=1, column=2, padx=10)
        
        # Таблица транзакций
        columns = ('ID', 'Тип операции', 'Сумма', 'Описание', 'Дата операции')
        self.transactions_tree = ttk.Treeview(self.parent, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.transactions_tree.heading(col, text=col)
            self.transactions_tree.column(col, width=120)
        
        self.transactions_tree.grid(
            row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.transactions_tree.yview)
        self.transactions_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        
        # Настройка адаптивности
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(2, weight=1)

    def load_transactions(self):
        """Загрузка транзакций по депозиту"""
        try:
            deposit_id = int(self.deposit_id_entry.get())
            transactions = self.db_manager.get_deposit_transactions(deposit_id)
            
            # Очистка таблицы
            for item in self.transactions_tree.get_children():
                self.transactions_tree.delete(item)
            
            for transaction in transactions:
                self.transactions_tree.insert('', tk.END, values=(
                    transaction.id, transaction.type, transaction.amount,
                    transaction.description, transaction.transaction_date
                ))
                
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
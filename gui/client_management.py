import tkinter as tk
from tkinter import ttk, messagebox
from database.models import Client

class ClientManagementFrame:
    def __init__(self, parent, db_manager, back_callback):
        self.parent = parent
        self.db_manager = db_manager
        self.back_callback = back_callback
        
        self.create_widgets()
        self.load_clients()

    def create_widgets(self):
        """Создание виджетов управления клиентами"""
        # Кнопка возврата
        ttk.Button(self.parent, text="← Главное меню", 
                  command=self.back_callback).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Заголовок
        ttk.Label(self.parent, text="Управление клиентами", 
                 font=('Arial', 14, 'bold')).grid(row=0, column=1, pady=10)
        
        # Поиск
        search_frame = ttk.Frame(self.parent)
        search_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(search_frame, text="Поиск:").grid(row=0, column=0, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)
        ttk.Button(search_frame, text="Найти", 
                  command=self.search_clients).grid(row=0, column=2, padx=5)
        ttk.Button(search_frame, text="Показать всех", 
                  command=self.load_clients).grid(row=0, column=3, padx=5)
        
        # Кнопка добавления клиента
        ttk.Button(self.parent, text="➕ Добавить клиента", 
                  command=self.show_add_client).grid(row=1, column=2, pady=10, padx=10)
        
        # Таблица клиентов
        columns = ('ID', 'ФИО', 'Паспорт', 'Телефон', 'Email', 'Дата регистрации')
        self.tree = ttk.Treeview(self.parent, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        self.tree.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Scrollbar для таблицы
        scrollbar = ttk.Scrollbar(self.parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=3, sticky=(tk.N, tk.S))
        
        # Настройка адаптивности
        self.parent.columnconfigure(1, weight=1)
        self.parent.rowconfigure(2, weight=1)

    def load_clients(self):
        """Загрузка списка клиентов"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            clients = self.db_manager.get_all_clients()
            for client in clients:
                self.tree.insert('', tk.END, values=(
                    client.id, client.full_name, client.passport_data,
                    client.phone_number, client.email, client.created_at
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить клиентов: {str(e)}")

    def search_clients(self):
        """Поиск клиентов"""
        search_term = self.search_entry.get().strip()
        if not search_term:
            self.load_clients()
            return
            
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            clients = self.db_manager.search_clients(search_term)
            for client in clients:
                self.tree.insert('', tk.END, values=(
                    client.id, client.full_name, client.passport_data,
                    client.phone_number, client.email, client.created_at
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка поиска: {str(e)}")

    def show_add_client(self):
        """Отображение диалога добавления клиента"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Добавление клиента")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Поля формы
        fields = [
            ("ФИО*", "full_name"),
            ("Паспортные данные*", "passport"),
            ("Телефон*", "phone"),
            ("Email", "email"),
            ("Адрес", "address")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(dialog, text=label).grid(row=i, column=0, sticky=tk.W, pady=5, padx=10)
            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5, padx=10)
            entries[key] = entry
        
        def save_client():
            try:
                client = Client(
                    id=None,
                    full_name=entries['full_name'].get().strip(),
                    passport_data=entries['passport'].get().strip(),
                    phone_number=entries['phone'].get().strip(),
                    email=entries['email'].get().strip(),
                    address=entries['address'].get().strip()
                )
                
                if not client.full_name or not client.passport_data or not client.phone_number:
                    messagebox.showwarning("Предупреждение", "Поля с * обязательны для заполнения")
                    return
                
                client_id = self.db_manager.create_client(client)
                messagebox.showinfo("Успех", f"Клиент успешно добавлен с ID: {client_id}")
                dialog.destroy()
                self.load_clients()
                
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        ttk.Button(dialog, text="Сохранить", command=save_client).grid(
            row=len(fields), column=1, pady=20, sticky=tk.E)
        
        dialog.columnconfigure(1, weight=1)
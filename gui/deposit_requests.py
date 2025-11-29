import tkinter as tk
from tkinter import ttk, messagebox
from gui.styles import COLORS

class DepositRequestsFrame:
    def __init__(self, parent, db_manager, back_callback):
        self.parent = parent
        self.db_manager = db_manager
        self.create_widgets()
        self.load_requests()

    def create_widgets(self):
        # Панель действий
        action_panel = ttk.Frame(self.parent, style='White.TFrame')
        action_panel.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(action_panel, text="✅ Одобрить", style='Primary.TButton', 
                  command=self.approve_selected).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_panel, text="❌ Отклонить", style='Danger.TButton', 
                  command=self.reject_selected).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(action_panel, text="🔄 Обновить", style='Nav.TButton', 
                  command=self.load_requests).pack(side=tk.RIGHT, padx=5)

        # Таблица
        columns = ('ID', 'Клиент', 'Тип вклада', 'Сумма', 'Дата заявки')
        self.tree = ttk.Treeview(self.parent, columns=columns, show='headings', height=15)
        
        self.tree.heading('ID', text='ID')
        self.tree.column('ID', width=50)
        self.tree.heading('Клиент', text='ФИО Клиента')
        self.tree.column('Клиент', width=200)
        self.tree.heading('Тип вклада', text='Продукт')
        self.tree.column('Тип вклада', width=150)
        self.tree.heading('Сумма', text='Сумма (BYN)')
        self.tree.heading('Дата заявки', text='Дата подачи')

        self.tree.pack(fill=tk.BOTH, expand=True)

    def load_requests(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        requests = self.db_manager.get_pending_deposits()
        for req in requests:
            # req: (id, full_name, type, amount, date)
            self.tree.insert('', tk.END, values=(
                req[0], req[1], req[2], f"{req[3]:,.2f}", req[4]
            ))

    def approve_selected(self):
        selected = self.tree.selection()
        if not selected: return
        
        if messagebox.askyesno("Подтверждение", "Одобрить выбранные заявки?"):
            try:
                for item in selected:
                    dep_id = self.tree.item(item)['values'][0]
                    self.db_manager.approve_deposit(dep_id)
                messagebox.showinfo("Успех", "Заявки одобрены, депозиты активированы.")
                self.load_requests()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))

    def reject_selected(self):
        selected = self.tree.selection()
        if not selected: return
        
        if messagebox.askyesno("Подтверждение", "Отклонить заявки?"):
            try:
                for item in selected:
                    dep_id = self.tree.item(item)['values'][0]
                    self.db_manager.reject_deposit(dep_id)
                self.load_requests()
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
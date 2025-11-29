import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
from decimal import Decimal

class AnalyticsFrame:
    def __init__(self, parent, db_manager, back_callback):
        self.parent = parent
        self.db_manager = db_manager
        self.back_callback = back_callback
        
        self.create_widgets()
        self.calculate_math_stats()
        self.draw_charts()

    def create_widgets(self):
        # Верхняя панель
        top_panel = ttk.Frame(self.parent)
        top_panel.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        ttk.Button(top_panel, text="← Назад", command=self.back_callback).pack(side=tk.LEFT)
        ttk.Label(top_panel, text="Аналитика и Прогнозы", font=('Arial', 14, 'bold')).pack(side=tk.LEFT, padx=20)

        # Панель статистики (Математический аппарат)
        self.stats_frame = ttk.LabelFrame(self.parent, text="Математический анализ портфеля")
        self.stats_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        self.stats_label = ttk.Label(self.stats_frame, text="Загрузка данных...", font=('Consolas', 10))
        self.stats_label.pack(padx=10, pady=10)

        # Панель для графиков
        self.charts_frame = ttk.Frame(self.parent)
        self.charts_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

    def calculate_math_stats(self):
        """Выполнение математических расчетов (Мат. аппарат)"""
        try:
            amounts = self.db_manager.get_all_active_amounts()
            amounts_float = [float(x) for x in amounts]
            
            if not amounts_float:
                self.stats_label.config(text="Нет данных для анализа")
                return

            # 1. Базовая статистика
            n = len(amounts_float)
            mean_val = np.mean(amounts_float)
            median_val = np.median(amounts_float)
            std_dev = np.std(amounts_float) # Стандартное отклонение
            
            # 2. Прогноз (упрощенный пример: если бы мы росли на 5% в месяц)
            # Расчет сложного процента для всего портфеля на год вперед
            # Формула: A = P(1 + r/n)^(nt)
            projected_growth = sum(amounts_float) * ((1 + 0.06/12)**(12))

            stats_text = (
                f"ВСЕГО ДЕПОЗИТОВ (N): {n}\n"
                f"СРЕДНИЙ ЧЕК (Mean):   {mean_val:,.2f} руб.\n"
                f"МЕДИАНА (Median):     {median_val:,.2f} руб.\n"
                f"ДИСПЕРСИЯ (Std Dev):  {std_dev:,.2f}\n"
                f"--------------------------------------------------\n"
                f"ПРОГНОЗ ПОРТФЕЛЯ (через 12 мес. при 6%): {projected_growth:,.2f} руб."
            )
            self.stats_label.config(text=stats_text)

        except Exception as e:
            self.stats_label.config(text=f"Ошибка расчета: {e}")

    def draw_charts(self):
        """Отрисовка графиков (FIX: Устранено наложение текста и подписей)"""
        # Очистка фрейма
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        # Создание двух графиков в одной фигуре. Увеличиваем размер для лучшей читаемости.
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), dpi=100)
        fig.suptitle('Аналитика портфеля', fontsize=16, fontweight='bold')

        # --- График 1: Круговая диаграмма (Объем по типам) ---
        type_data = self.db_manager.get_deposits_by_type_stats()
        
        if type_data:
            labels = [row[0] for row in type_data]
            sizes = [row[2] for row in type_data]
            
            # FIX 1: Убираем подписи и проценты с круга, чтобы он был чистым
            wedges, texts = ax1.pie(sizes, startangle=90) # Убрали labels и autopct
            
            ax1.set_title('Объем средств по типам вкладов', fontsize=12)
            
            # Используем легенду для отображения названий и долей
            ax1.legend(wedges, labels, title="Типы", loc="center left", 
                       # FIX 2: Увеличиваем отступ легенды, чтобы не накладывалась на второй график
                       bbox_to_anchor=(0.95, 0, 0.5, 1)) 
            ax1.axis('equal')  # Делаем круг идеальным

        # --- График 2: Динамика открытий ---
        timeline_data = self.db_manager.get_deposits_timeline()
        
        if timeline_data:
            dates = [row[0] for row in timeline_data]
            values = [float(row[1]) for row in timeline_data]
            
            ax2.plot(dates, values, marker='o', markersize=4, label='Приток средств', color='#667eea')
            
            # Добавление линии тренда
            x_nums = np.arange(len(dates))
            if len(dates) > 1:
                z = np.polyfit(x_nums, values, 1)
                p = np.poly1d(z)
                ax2.plot(dates, p(x_nums), "r--", alpha=0.7, label='Тренд')

            ax2.set_title('Динамика открытий депозитов', fontsize=12)
            ax2.set_ylabel('Объем открытых депозитов (BYN))')
            ax2.grid(axis='y', alpha=0.5, linestyle='--')
            ax2.legend()

            # FIX 3: Автоматический поворот и форматирование дат, чтобы они не наезжали друг на друга
            fig.autofmt_xdate(rotation=45)

        # FIX 4: Убедимся, что элементы не накладываются друг на друга на общем холсте
        plt.tight_layout(rect=[0, 0.03, 1, 0.95]) 

        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
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
        """Отрисовка графиков с использованием Matplotlib"""
        # Очистка предыдущих графиков
        for widget in self.charts_frame.winfo_children():
            widget.destroy()

        # Создание фигуры Matplotlib (1 строка, 2 колонки)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=100)
        fig.suptitle('Визуализация данных', fontsize=12)

        # --- График 1: Круговая диаграмма (Типы депозитов) ---
        type_data = self.db_manager.get_deposits_by_type_stats()
        if type_data:
            labels = [row[0] for row in type_data]
            sizes = [row[2] for row in type_data] # Используем сумму денег, а не кол-во
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax1.set_title('Объем средств по типам вкладов')

        # --- График 2: Линейный тренд (Динамика) + Линия регрессии ---
        timeline_data = self.db_manager.get_deposits_timeline()
        if timeline_data:
            dates = [row[0] for row in timeline_data]
            values = [float(row[1]) for row in timeline_data]
            
            # Построение основного графика
            ax2.plot(dates, values, marker='o', label='Фактические данные')
            
            # --- МАТЕМАТИЧЕСКИЙ АППАРАТ: Линейная регрессия (Тренд) ---
            # Преобразуем даты в числа для регрессии
            x_nums = np.arange(len(dates))
            
            # Вычисляем коэффициенты полинома 1-й степени (y = mx + b)
            if len(dates) > 1:
                z = np.polyfit(x_nums, values, 1) 
                p = np.poly1d(z)
                ax2.plot(dates, p(x_nums), "r--", label=f'Тренд (y={z[0]:.2f}x+{z[1]:.0f})')

            ax2.set_title('Динамика привлечения средств')
            ax2.tick_params(axis='x', rotation=45)
            ax2.legend()
            ax2.grid(True)

        # Интеграция в Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
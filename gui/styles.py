import tkinter as tk
from tkinter import ttk

# ЦВЕТОВАЯ ПАЛИТРА (Совпадает с веб-версией)
COLORS = {
    'primary': '#667eea',      # Основной фиолетовый
    'primary_dark': '#5a67d8', # При наведении
    'secondary': '#764ba2',    # Акцент
    'bg_main': '#F3F4F6',      # Светло-серый фон
    'bg_sidebar': '#1F2937',   # Темный сайдбар
    'white': '#FFFFFF',
    'text_dark': '#111827',
    'text_light': '#F9FAFB',
    'danger': '#EF4444',
    'success': '#10B981'
}

FONTS = {
    'h1': ('Segoe UI', 20, 'bold'),
    'h2': ('Segoe UI', 14, 'bold'),
    'body': ('Segoe UI', 10),
    'nav': ('Segoe UI', 11)
}

def setup_styles(root):
    """Настройка глобальных стилей приложения"""
    style = ttk.Style(root)
    
    # Используем тему 'clam', так как она позволяет менять цвета кнопок и полос прокрутки
    try:
        style.theme_use('clam')
    except:
        pass # Если тема недоступна, останется стандартная

    # 1. ОСНОВНЫЕ ФОНЫ
    style.configure('TFrame', background=COLORS['bg_main'])
    style.configure('White.TFrame', background=COLORS['white'], relief='flat')
    
    # 2. МЕТКИ (LABELS)
    style.configure('TLabel', background=COLORS['bg_main'], foreground=COLORS['text_dark'], font=FONTS['body'])
    style.configure('Header.TLabel', font=FONTS['h1'], background=COLORS['bg_main'])
    style.configure('SubHeader.TLabel', font=FONTS['h2'], background=COLORS['white'])
    style.configure('Sidebar.TLabel', background=COLORS['bg_sidebar'], foreground=COLORS['text_light'])

    # 3. КНОПКИ (BUTTONS)
    # Основная кнопка (Primary)
    style.configure('Primary.TButton', 
                   font=FONTS['body'],
                   borderwidth=0,
                   background=COLORS['primary'],
                   foreground=COLORS['white'],
                   padding=10)
    
    style.map('Primary.TButton',
              background=[('active', COLORS['primary_dark']), ('pressed', COLORS['secondary'])])

    # Кнопка меню (Sidebar)
    style.configure('Nav.TButton',
                   font=FONTS['nav'],
                   background=COLORS['bg_sidebar'],
                   foreground=COLORS['white'],
                   borderwidth=0,
                   anchor='w', # Текст слева
                   padding=12)
    
    style.map('Nav.TButton',
              background=[('active', '#374151')], # Светлее при наведении
              foreground=[('active', COLORS['white'])])

    # Кнопка опасного действия
    style.configure('Danger.TButton', background=COLORS['danger'], foreground='white')

    # 4. ТАБЛИЦЫ (TREEVIEW)
    style.configure("Treeview",
                    background=COLORS['white'],
                    fieldbackground=COLORS['white'],
                    foreground=COLORS['text_dark'],
                    rowheight=30,
                    font=FONTS['body'],
                    borderwidth=0)
    
    style.configure("Treeview.Heading",
                    background=COLORS['bg_main'],
                    foreground=COLORS['text_dark'],
                    font=('Segoe UI', 10, 'bold'),
                    relief="flat")
    
    style.map("Treeview", background=[('selected', COLORS['primary'])])

    # 5. TNotebook (Вкладки)
    style.configure("TNotebook", background=COLORS['bg_main'], borderwidth=0)
    style.configure("TNotebook.Tab", 
                   padding=[15, 5], 
                   font=FONTS['body'],
                   background=COLORS['bg_main'])
    style.map("TNotebook.Tab", 
              background=[("selected", COLORS['white'])],
              foreground=[("selected", COLORS['primary'])])

    return style
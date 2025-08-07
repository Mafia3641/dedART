"""
Статусная панель
"""

from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtCore import Qt


class StatusBar(QStatusBar):
    """Статусная панель приложения"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_widgets()
    
    def init_widgets(self):
        """Инициализация виджетов статусной панели"""
        # Основное сообщение
        self.message_label = QLabel("Готов")
        self.addWidget(self.message_label)
        
        # Разделитель
        self.addPermanentWidget(QLabel("|"))
        
        # Позиция курсора
        self.cursor_label = QLabel("Строка: 1, Колонка: 1")
        self.addPermanentWidget(self.cursor_label)
        
        # Разделитель
        self.addPermanentWidget(QLabel("|"))
        
        # Количество строк
        self.line_count_label = QLabel("Строк: 0")
        self.addPermanentWidget(self.line_count_label)
        
        # Разделитель
        self.addPermanentWidget(QLabel("|"))
        
        # Кодировка
        self.encoding_label = QLabel("UTF-8")
        self.addPermanentWidget(self.encoding_label)
    
    def set_message(self, message: str):
        """Установка сообщения в статусной панели"""
        self.message_label.setText(message)
    
    def update_cursor_position(self, line: int, column: int):
        """Обновление позиции курсора"""
        self.cursor_label.setText(f"Строка: {line}, Колонка: {column}")
    
    def update_line_count(self, line_count: int):
        """Обновление количества строк"""
        self.line_count_label.setText(f"Строк: {line_count}")
    
    def update_encoding(self, encoding: str):
        """Обновление информации о кодировке"""
        self.encoding_label.setText(encoding) 
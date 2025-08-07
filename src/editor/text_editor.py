"""
Текстовый редактор
"""

from PyQt6.QtWidgets import QPlainTextEdit
from PyQt6.QtGui import QFont, QTextCursor, QColor, QPalette
from PyQt6.QtCore import Qt, pyqtSignal


class TextEditor(QPlainTextEdit):
    """Основной текстовый редактор"""
    
    # Сигналы
    text_changed = pyqtSignal()
    cursor_position_changed = pyqtSignal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_editor()
        self.setup_connections()
    
    def init_editor(self):
        """Инициализация редактора"""
        # Настройка шрифта
        font = QFont("Consolas", 12)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Настройка отступов
        self.setTabStopDistance(font.pointSize() * 4)
        
        # Настройка цветовой схемы
        self.setup_color_scheme()
        
        # Настройка поведения
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Настройка курсора
        self.setCursorWidth(2)
    
    def setup_color_scheme(self):
        """Настройка цветовой схемы"""
        palette = self.palette()
        
        # Цвет фона (более темный для центральной области)
        palette.setColor(QPalette.ColorRole.Base, QColor("#1e1e1e"))
        
        # Цвет текста
        palette.setColor(QPalette.ColorRole.Text, QColor("#d4d4d4"))
        
        # Цвет выделения
        palette.setColor(QPalette.ColorRole.Highlight, QColor("#264f78"))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        
        # Цвет курсора
        palette.setColor(QPalette.ColorRole.WindowText, QColor("#d4d4d4"))
        
        self.setPalette(palette)
    
    def setup_connections(self):
        """Настройка сигналов и слотов"""
        self.textChanged.connect(self.on_text_changed)
        self.cursorPositionChanged.connect(self.on_cursor_position_changed)
    
    def on_text_changed(self):
        """Обработчик изменения текста"""
        self.text_changed.emit()
    
    def on_cursor_position_changed(self):
        """Обработчик изменения позиции курсора"""
        cursor = self.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self.cursor_position_changed.emit(line, column)
    
    # Удалены неиспользуемые методы:
    # get_selected_text, has_selection, select_all, goto_line,
    # get_current_line_number, get_total_lines, insert_text_at_cursor,
    # replace_selection, duplicate_line, delete_line, toggle_comment 
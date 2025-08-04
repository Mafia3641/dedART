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
        self.parent = parent
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
    
    def get_selected_text(self) -> str:
        """Получение выделенного текста"""
        cursor = self.textCursor()
        return cursor.selectedText()
    
    def has_selection(self) -> bool:
        """Проверка наличия выделения"""
        cursor = self.textCursor()
        return cursor.hasSelection()
    
    def select_all(self):
        """Выделить весь текст"""
        cursor = self.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        self.setTextCursor(cursor)
    
    def goto_line(self, line_number: int):
        """Переход к указанной строке"""
        if line_number > 0:
            # Получаем блок документа
            document = self.document()
            if line_number <= document.blockCount():
                block = document.findBlockByLineNumber(line_number - 1)
                cursor = self.textCursor()
                cursor.setPosition(block.position())
                self.setTextCursor(cursor)
                self.ensureCursorVisible()
    
    def get_current_line_number(self) -> int:
        """Получение номера текущей строки"""
        cursor = self.textCursor()
        return cursor.blockNumber() + 1
    
    def get_total_lines(self) -> int:
        """Получение общего количества строк"""
        return self.document().blockCount()
    
    def insert_text_at_cursor(self, text: str):
        """Вставка текста в позицию курсора"""
        cursor = self.textCursor()
        cursor.insertText(text)
    
    def replace_selection(self, text: str):
        """Замена выделенного текста"""
        cursor = self.textCursor()
        cursor.insertText(text)
    
    def duplicate_line(self):
        """Дублирование текущей строки"""
        cursor = self.textCursor()
        block = cursor.block()
        line_text = block.text()
        
        # Переходим в конец строки
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
        
        # Вставляем новую строку с тем же текстом
        cursor.insertText('\n' + line_text)
        
        # Переходим на новую строку
        cursor.movePosition(QTextCursor.MoveOperation.Up)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine)
        self.setTextCursor(cursor)
    
    def delete_line(self):
        """Удаление текущей строки"""
        cursor = self.textCursor()
        block = cursor.block()
        
        # Выделяем всю строку
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, 
                          QTextCursor.MoveMode.KeepAnchor)
        
        # Удаляем строку
        cursor.removeSelectedText()
        
        # Удаляем символ новой строки, если он есть
        if not cursor.atEnd():
            cursor.deleteChar()
    
    def toggle_comment(self):
        """Переключение комментария для текущей строки"""
        cursor = self.textCursor()
        block = cursor.block()
        line_text = block.text()
        
        # Определяем тип комментария на основе расширения файла
        # Для простоты используем #
        comment_char = "# "
        
        if line_text.strip().startswith(comment_char):
            # Убираем комментарий
            new_text = line_text.replace(comment_char, "", 1)
        else:
            # Добавляем комментарий
            new_text = comment_char + line_text
        
        # Заменяем строку
        cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
        cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, 
                          QTextCursor.MoveMode.KeepAnchor)
        cursor.insertText(new_text) 
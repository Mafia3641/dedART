"""
Кастомный виджет с центрированными вкладками
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ..editor.text_editor import TextEditor


class CustomTabWidget(QWidget):
    """Кастомный виджет с центрированными вкладками"""
    
    # Сигналы
    text_changed = pyqtSignal()
    cursor_position_changed = pyqtSignal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.current_editor = None
        self.current_index = 1  # ЭДИТОР по умолчанию
        self.init_ui()
        self.setup_style()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем панель вкладок
        self.tab_bar = self.create_tab_bar()
        layout.addWidget(self.tab_bar)
        
        # Создаем стек виджетов для содержимого
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Создаем вкладки
        self.create_tabs()
        
        # Устанавливаем текущую вкладку
        self.set_current_tab(1)  # ЭДИТОР
    
    def create_tab_bar(self):
        """Создание панели вкладок"""
        tab_bar = QWidget()
        tab_layout = QHBoxLayout(tab_bar)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        
        # Добавляем растягивающийся виджет слева для центрирования
        tab_layout.addStretch()
        
        # Создаем кнопки вкладок
        self.chat_button = self.create_tab_button("ЧАТ", 0)
        self.editor_button = self.create_tab_button("ЭДИТОР", 1)
        self.preview_button = self.create_tab_button("ПРЕДПРОСМОТР", 2)
        
        tab_layout.addWidget(self.chat_button)
        tab_layout.addWidget(self.editor_button)
        tab_layout.addWidget(self.preview_button)
        
        # Добавляем растягивающийся виджет справа для центрирования
        tab_layout.addStretch()
        
        return tab_bar
    
    def create_tab_button(self, text, index):
        """Создание кнопки вкладки"""
        button = QPushButton(text)
        button.setCheckable(True)
        button.setProperty("tab_index", index)
        button.clicked.connect(lambda: self.set_current_tab(index))
        return button
    
    def create_tabs(self):
        """Создание содержимого вкладок"""
        # Вкладка ЧАТ
        self.chat_tab = self.create_chat_tab()
        self.stacked_widget.addWidget(self.chat_tab)
        
        # Вкладка ЭДИТОР
        self.editor_tab = self.create_editor_tab()
        self.stacked_widget.addWidget(self.editor_tab)
        
        # Вкладка ПРЕДПРОСМОТР
        self.preview_tab = self.create_preview_tab()
        self.stacked_widget.addWidget(self.preview_tab)
    
    def create_chat_tab(self):
        """Создание вкладки ЧАТ"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Заголовок
        title = QLabel("Чат с ИИ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #a9b7c6;
                padding: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Область чата
        chat_area = QLabel("Здесь будет интерфейс чата с ИИ\n\nФункция в разработке...")
        chat_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chat_area.setStyleSheet("""
            QLabel {
                color: #a9b7c6;
                font-size: 14px;
                padding: 40px;
                background-color: #2b2b2b;
                border: 1px solid #3c3f41;
                border-radius: 8px;
                margin: 20px;
            }
        """)
        layout.addWidget(chat_area)
        
        # Кнопка для демонстрации
        demo_button = QPushButton("Демо: Отправить сообщение")
        demo_button.setStyleSheet("""
            QPushButton {
                background-color: #3c3f41;
                color: #a9b7c6;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4c4f51;
            }
            QPushButton:pressed {
                background-color: #2c2f31;
            }
        """)
        layout.addWidget(demo_button)
        
        layout.addStretch()
        return tab
    
    def create_editor_tab(self):
        """Создание вкладки ЭДИТОР"""
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем сплиттер для изменения размера панелей
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #3c3f41;
            }
            QSplitter::handle:hover {
                background-color: #4c4f51;
            }
        """)
        
        # Левая панель (будущие настройки)
        self.left_panel = self.create_left_panel()
        splitter.addWidget(self.left_panel)
        
        # Центральная область с редактором
        self.center_panel = self.create_center_panel()
        splitter.addWidget(self.center_panel)
        
        # Правая панель (будущие настройки)
        self.right_panel = self.create_right_panel()
        splitter.addWidget(self.right_panel)
        
        # Устанавливаем пропорции панелей
        splitter.setSizes([250, 800, 250])
        
        layout.addWidget(splitter)
        return tab
    
    def create_left_panel(self):
        """Создание левой панели"""
        panel = QWidget()
        panel.setMinimumWidth(200)
        panel.setMaximumWidth(400)
        panel.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-right: 1px solid #3c3f41;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Заголовок панели
        title = QLabel("Панель инструментов")
        title.setStyleSheet("""
            QLabel {
                color: #a9b7c6;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
                background-color: #3c3f41;
                border-radius: 3px;
            }
        """)
        layout.addWidget(title)
        
        # Заглушка для будущих инструментов
        placeholder = QLabel("Здесь будут инструменты\nи настройки редактора")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #6a6a6a;
                font-size: 11px;
                padding: 20px;
                background-color: #2b2b2b;
                border: 1px dashed #3c3f41;
                border-radius: 5px;
            }
        """)
        layout.addWidget(placeholder)
        
        layout.addStretch()
        return panel
    
    def create_center_panel(self):
        """Создание центральной панели с редактором"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        
        # Контейнер для редактора с закругленными краями
        editor_container = QWidget()
        editor_container.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border: 1px solid #3c3f41;
                border-radius: 8px;
            }
        """)
        
        editor_layout = QVBoxLayout(editor_container)
        editor_layout.setContentsMargins(15, 15, 15, 15)
        editor_layout.setSpacing(0)
        
        # Создаем текстовый редактор
        self.editor = TextEditor()
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        editor_layout.addWidget(self.editor)
        
        # Подключаем сигналы редактора
        self.editor.textChanged.connect(self.on_editor_text_changed)
        self.editor.cursorPositionChanged.connect(self.on_editor_cursor_changed)
        
        layout.addWidget(editor_container)
        return panel
    
    def create_right_panel(self):
        """Создание правой панели"""
        panel = QWidget()
        panel.setMinimumWidth(200)
        panel.setMaximumWidth(400)
        panel.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                border-left: 1px solid #3c3f41;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Заголовок панели
        title = QLabel("Свойства")
        title.setStyleSheet("""
            QLabel {
                color: #a9b7c6;
                font-weight: bold;
                font-size: 12px;
                padding: 5px;
                background-color: #3c3f41;
                border-radius: 3px;
            }
        """)
        layout.addWidget(title)
        
        # Заглушка для будущих свойств
        placeholder = QLabel("Здесь будут свойства\nи параметры файла")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #6a6a6a;
                font-size: 11px;
                padding: 20px;
                background-color: #2b2b2b;
                border: 1px dashed #3c3f41;
                border-radius: 5px;
            }
        """)
        layout.addWidget(placeholder)
        
        layout.addStretch()
        return panel
    
    def create_preview_tab(self):
        """Создание вкладки ПРЕДПРОСМОТР"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Заголовок
        title = QLabel("Предварительный просмотр")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #a9b7c6;
                padding: 20px;
            }
        """)
        layout.addWidget(title)
        
        # Область предпросмотра
        preview_area = QLabel("Здесь будет отображаться предварительный просмотр\n\nФункция в разработке...")
        preview_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_area.setStyleSheet("""
            QLabel {
                color: #a9b7c6;
                font-size: 14px;
                padding: 40px;
                background-color: #2b2b2b;
                border: 1px solid #3c3f41;
                border-radius: 8px;
                margin: 20px;
            }
        """)
        layout.addWidget(preview_area)
        
        # Кнопка для демонстрации
        demo_button = QPushButton("Демо: Обновить предпросмотр")
        demo_button.setStyleSheet("""
            QPushButton {
                background-color: #3c3f41;
                color: #a9b7c6;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4c4f51;
            }
            QPushButton:pressed {
                background-color: #2c2f31;
            }
        """)
        layout.addWidget(demo_button)
        
        layout.addStretch()
        return tab
    
    def set_current_tab(self, index):
        """Установка текущей вкладки"""
        # Сбрасываем все кнопки
        self.chat_button.setChecked(False)
        self.editor_button.setChecked(False)
        self.preview_button.setChecked(False)
        
        # Устанавливаем активную кнопку
        if index == 0:
            self.chat_button.setChecked(True)
            self.current_editor = None
        elif index == 1:
            self.editor_button.setChecked(True)
            self.current_editor = self.editor
        elif index == 2:
            self.preview_button.setChecked(True)
            self.current_editor = None
        
        # Переключаем содержимое
        self.stacked_widget.setCurrentIndex(index)
        self.current_index = index
    
    def setup_style(self):
        """Настройка стиля вкладок"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
            }
            
            QPushButton {
                background-color: #3c3f41;
                color: #a9b7c6;
                border: none;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            
            QPushButton:checked {
                background-color: #2b2b2b;
                border-bottom: 2px solid #4caf50;
            }
            
            QPushButton:hover {
                background-color: #4c4f51;
            }
            
            QPushButton:!checked {
                background-color: #3c3f41;
            }
        """)
    
    def on_editor_text_changed(self):
        """Обработчик изменения текста в редакторе"""
        self.text_changed.emit()
    
    def on_editor_cursor_changed(self):
        """Обработчик изменения позиции курсора в редакторе"""
        if self.current_editor:
            cursor = self.current_editor.textCursor()
            line = cursor.blockNumber() + 1
            column = cursor.columnNumber() + 1
            self.cursor_position_changed.emit(line, column)
    
    def new_file(self):
        """Создание нового файла"""
        if self.current_editor:
            self.current_editor.clear()
    
    def set_content(self, content: str):
        """Установка содержимого в редактор"""
        if self.current_editor:
            self.current_editor.setPlainText(content)
    
    def get_content(self) -> str:
        """Получение содержимого из редактора"""
        if self.current_editor:
            return self.current_editor.toPlainText()
        return ""
    
    def is_modified(self) -> bool:
        """Проверка наличия изменений"""
        if self.current_editor:
            return self.current_editor.document().isModified()
        return False
    
    def get_line_count(self) -> int:
        """Получение количества строк"""
        if self.current_editor:
            return self.current_editor.document().blockCount()
        return 0
    
    def set_font(self, font_family: str, font_size: int):
        """Установка шрифта"""
        if self.current_editor:
            font = QFont(font_family, font_size)
            font.setFixedPitch(True)
            self.current_editor.setFont(font)
    
    def get_font(self) -> tuple:
        """Получение текущего шрифта"""
        if self.current_editor:
            font = self.current_editor.font()
            return font.family(), font.pointSize()
        return "Consolas", 12 
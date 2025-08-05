"""
Кастомный виджет с центрированными вкладками
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QSplitter,
    QTextEdit, QLineEdit, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from ..editor.text_editor import TextEditor


class ChatTextEdit(QTextEdit):
    """Кастомный QTextEdit для чата с обработкой Enter"""
    
    send_message_signal = pyqtSignal()
    
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        from PyQt6.QtCore import Qt
        
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                # Ctrl+Enter - новая строка
                super().keyPressEvent(event)
            else:
                # Enter - отправить сообщение
                self.send_message_signal.emit()
                event.accept()
        else:
            super().keyPressEvent(event)


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
        
        # Создаем панель вкладок (перемещаем выше)
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
        """Создание вкладки ЧАТ (центрированный чат)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Центрируем область сообщений
        messages_row = QWidget()
        messages_row_layout = QHBoxLayout(messages_row)
        messages_row_layout.setContentsMargins(0, 0, 0, 0)
        messages_row_layout.setSpacing(0)
        messages_row_layout.addStretch()
        self.messages_area = self.create_messages_area()
        messages_row_layout.addWidget(self.messages_area)
        messages_row_layout.addStretch()
        layout.addWidget(messages_row, stretch=1)

        # Центрируем область ввода
        input_row = QWidget()
        input_row_layout = QHBoxLayout(input_row)
        input_row_layout.setContentsMargins(0, 0, 0, 0)
        input_row_layout.setSpacing(0)
        input_row_layout.addStretch()
        self.input_area = self.create_input_area()
        input_row_layout.addWidget(self.input_area)
        input_row_layout.addStretch()
        layout.addWidget(input_row, stretch=0)

        return tab
    
    def create_messages_area(self):
        """Создание области сообщений в современном стиле"""
        container = QWidget()
        container.setFixedWidth(600)  # Половина экрана примерно
        container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        
        # Заголовок чата в современном стиле
        title = QLabel("Чат с ИИ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: 600;
                color: #ffffff;
                padding: 24px 0;
                margin-bottom: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        layout.addWidget(title)
        
        # Область прокрутки для сообщений с улучшенным дизайном
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #1e1e1e;
                width: 10px;
                border-radius: 5px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #404040;
                border-radius: 5px;
                min-height: 30px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #505050;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
        """)
        
        # Виджет для сообщений
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(16)
        self.messages_layout.addStretch()  # Растягивающийся виджет в конце
        
        scroll_area.setWidget(self.messages_widget)
        layout.addWidget(scroll_area)
        
        return container
    
    def create_input_area(self):
        """Создание области ввода сообщения в стиле Cursor AI"""
        container = QWidget()
        container.setFixedWidth(600)  # Та же ширина, что и область сообщений
        container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        
        # Основной контейнер для поля ввода с современным дизайном
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border: none;
                border-radius: 16px;
                padding: 0px;
            }
        """)
        input_container.setFixedHeight(90)
        
        # Компактный layout для input_container
        input_layout = QVBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(2)

        # Add Context
        context_button = QPushButton("@ Add Context")
        context_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 2px 4px;
                font-size: 11px;
                font-weight: 500;
                text-align: left;
                min-height: 16px;
                max-height: 18px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #505050;
            }
            QPushButton:pressed {
                background-color: #252525;
            }
        """)
        context_button.setFixedHeight(18)
        context_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        context_button.adjustSize()
        input_layout.addWidget(context_button, alignment=Qt.AlignmentFlag.AlignLeft)

        # Поле для ввода
        self.chat_input = ChatTextEdit()
        self.chat_input.setPlaceholderText("Plan, search, build anything")
        self.chat_input.setMaximumHeight(28)
        self.chat_input.setMinimumHeight(28)
        self.chat_input.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #ffffff;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 0px;
            }
            QTextEdit::placeholder {
                color: #888888;
            }
        """)
        self.chat_input.send_message_signal.connect(self.send_message)
        input_layout.addWidget(self.chat_input)

        # Нижняя секция с элементами управления
        bottom_section = QWidget()
        bottom_section.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        bottom_layout = QHBoxLayout(bottom_section)
        bottom_layout.setContentsMargins(8, 6, 8, 6)
        bottom_layout.setSpacing(8)
        
        # Левая группа элементов управления
        left_controls = QWidget()
        left_layout = QHBoxLayout(left_controls)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # Кнопка ∞ Ctrl+I с уменьшенной высотой
        infinity_button = QPushButton("∞ Ctrl+I")
        infinity_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #888888;
                border: 1px solid #404040;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 500;
                padding: 2px 8px;
                min-height: 16px;
                max-height: 20px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: #cccccc;
                border-color: #505050;
            }
        """)
        infinity_button.setFixedHeight(20)
        left_layout.addWidget(infinity_button)
        
        # Кнопка Auto с уменьшенной высотой
        auto_button = QPushButton("Auto")
        auto_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #888888;
                border: 1px solid #404040;
                border-radius: 6px;
                font-size: 11px;
                font-weight: 500;
                padding: 2px 8px;
                min-height: 16px;
                max-height: 20px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                color: #cccccc;
                border-color: #505050;
            }
        """)
        auto_button.setFixedHeight(20)
        left_layout.addWidget(auto_button)
        
        left_layout.addStretch()
        bottom_layout.addWidget(left_controls)
        
        # Правая группа элементов управления
        right_controls = QWidget()
        right_layout = QHBoxLayout(right_controls)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # Кнопка изображения (скрытая, как в Cursor AI)
        image_button = QPushButton("")
        image_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                min-width: 24px;
                min-height: 24px;
            }
        """)
        image_button.setVisible(False)  # Скрываем кнопку изображения
        right_layout.addWidget(image_button)
        
        # Кнопка отправки в стиле Cursor AI
        send_button = QPushButton("↑")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                border: none;
                border-radius: 50%;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
                min-width: 32px;
                min-height: 32px;
                margin-left: 4px;
            }
            QPushButton:hover {
                background-color: #0098ff;
                min-width: 34px;
                min-height: 34px;
            }
            QPushButton:pressed {
                background-color: #005a9e;
                min-width: 30px;
                min-height: 30px;
            }
        """)
        right_layout.addWidget(send_button)
        
        bottom_layout.addWidget(right_controls)
        input_layout.addWidget(bottom_section)
        
        layout.addWidget(input_container)
        
        # Подключаем сигналы
        send_button.clicked.connect(self.send_message)
        
        return container
    
    def send_message(self):
        """Отправка сообщения"""
        text = self.chat_input.toPlainText().strip()
        if text:
            # Добавляем сообщение пользователя
            self.add_message(text, is_user=True)
            # Очищаем поле ввода
            self.chat_input.clear()
            # Имитируем ответ ИИ
            self.add_message("Это демо-ответ от ИИ. Функция чата в разработке...", is_user=False)
    
    def add_message(self, text: str, is_user: bool = True):
        """Добавление сообщения в чат в современном стиле"""
        # Удаляем растягивающийся виджет
        if self.messages_layout.count() > 0:
            self.messages_layout.removeItem(self.messages_layout.itemAt(self.messages_layout.count() - 1))
        
        # Создаем виджет сообщения
        message_widget = QWidget()
        message_layout = QHBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(12)
        
        if is_user:
            # Сообщение пользователя справа в стиле Cursor AI
            message_layout.addStretch()
            message_text = QLabel(text)
            message_text.setWordWrap(True)
            message_text.setStyleSheet("""
                QLabel {
                    background-color: #007acc;
                    color: white;
                    border-radius: 16px;
                    padding: 12px 18px;
                    font-size: 14px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    max-width: 420px;
                    border: 1px solid #0098ff;
                }
            """)
            message_layout.addWidget(message_text)
        else:
            # Сообщение ИИ слева в стиле Cursor AI
            message_text = QLabel(text)
            message_text.setWordWrap(True)
            message_text.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border-radius: 16px;
                    padding: 12px 18px;
                    font-size: 14px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    max-width: 420px;
                    border: 1px solid #404040;
                }
            """)
            message_layout.addWidget(message_text)
            message_layout.addStretch()
        
        # Добавляем сообщение
        self.messages_layout.addWidget(message_widget)
        
        # Добавляем растягивающийся виджет обратно
        self.messages_layout.addStretch()
        
        # Прокручиваем к новому сообщению
        QTimer.singleShot(100, lambda: self.scroll_to_bottom())
    
    def scroll_to_bottom(self):
        """Прокрутка к последнему сообщению"""
        if hasattr(self, 'messages_area'):
            # Находим QScrollArea в messages_area
            for child in self.messages_area.findChildren(QScrollArea):
                scrollbar = child.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
    

    
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
        title = QLabel("Inspector")
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
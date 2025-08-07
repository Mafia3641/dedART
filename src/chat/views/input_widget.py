"""
Виджет для ввода сообщений
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QLabel, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextOption


class ChatInputWidget(QTextEdit):
    """
    Кастомное поле ввода для чата
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за ввод текста
    - Open/Closed: может быть расширено дополнительными функциями
    """
    
    # Сигналы
    send_message_requested = pyqtSignal(str)
    typing_started = pyqtSignal()
    typing_stopped = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.typing_timer = QTimer()
        self.typing_timer.setSingleShot(True)
        self.typing_timer.timeout.connect(self.typing_stopped.emit)
        self.is_typing = False
        
        # Флаг для предотвращения бесконечной рекурсии при обработке текста
        self.processing_text = False
        
        self.init_editor()
        self.setup_connections()
    
    def init_editor(self):
        """Инициализация редактора"""
        self.setPlaceholderText("Start chatting with AI...")
        self.setMaximumHeight(100)
        
        # Настройка поведения
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        
        # Автоматическое изменение высоты
        self.document().contentsChanged.connect(self._adjust_height)
    
    def setup_connections(self):
        """Настройка сигналов"""
        self.textChanged.connect(self._on_text_changed)
    
    def keyPressEvent(self, event):
        """Обработка нажатий клавиш"""
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                # Ctrl+Enter - новая строка
                super().keyPressEvent(event)
            else:
                # Enter - отправить сообщение
                self._send_message()
                event.accept()
        else:
            super().keyPressEvent(event)
    
    def _send_message(self):
        """Отправка сообщения"""
        text = self.toPlainText().strip()
        if text:
            self.send_message_requested.emit(text)
            self.clear()
            if self.is_typing:
                self.typing_stopped.emit()
                self.is_typing = False
    
    def _on_text_changed(self):
        """Обработка изменения текста"""
        if not self.is_typing and self.toPlainText().strip():
            self.typing_started.emit()
            self.is_typing = True
        
        # Обрабатываем длинные слова
        if not self.processing_text:
            self._process_long_words_in_input()
        
        # Перезапуск таймера печати
        self.typing_timer.start(2000)  # 2 секунды без изменений = остановка печати
    
    def _adjust_height(self):
        """Автоматическое изменение высоты"""
        doc_height = self.document().size().height()
        margins = self.contentsMargins()
        new_height = int(doc_height + margins.top() + margins.bottom() + 10)
        
        # Ограничиваем высоту
        min_height = 40
        max_height = 120
        new_height = max(min_height, min(new_height, max_height))
        
        if new_height != self.height():
            self.setFixedHeight(new_height)
    
    def insert_text(self, text: str):
        """Вставка текста в позицию курсора"""
        cursor = self.textCursor()
        cursor.insertText(text)
    
    def clear_and_focus(self):
        """Очистка и установка фокуса"""
        self.clear()
        self.setFocus()
    
    def _process_long_words_in_input(self):
        """Обработка длинных слов в поле ввода"""
        current_text = self.toPlainText()
        if not current_text:
            return
        
        # Получаем позицию курсора
        cursor = self.textCursor()
        cursor_position = cursor.position()
        
        # Обрабатываем текст
        processed_text = self._process_long_words(current_text)
        
        # Если текст изменился
        if processed_text != current_text:
            self.processing_text = True
            
            # Сохраняем позицию курсора относительно длины текста
            position_ratio = cursor_position / len(current_text) if current_text else 0
            
            # Устанавливаем обработанный текст
            self.setPlainText(processed_text)
            
            # Восстанавливаем позицию курсора
            new_position = int(position_ratio * len(processed_text))
            cursor = self.textCursor()
            cursor.setPosition(min(new_position, len(processed_text)))
            self.setTextCursor(cursor)
            
            self.processing_text = False
    
    def _process_long_words(self, text: str) -> str:
        """Обработка длинных слов для корректного отображения"""
        lines = text.split('\n')
        processed_lines = []
        
        for line in lines:
            words = line.split(' ')
            processed_words = []
            
            for word in words:
                if len(word) > 25:  # Очень длинное слово
                    # Разбиваем длинное слово на части с помощью zero-width space
                    processed_word = self._break_long_word(word)
                    processed_words.append(processed_word)
                else:
                    processed_words.append(word)
            
            processed_lines.append(' '.join(processed_words))
        
        return '\n'.join(processed_lines)
    
    def _break_long_word(self, word: str) -> str:
        """Разбивка длинного слова на части"""
        if len(word) <= 25:
            return word
        
        # Разбиваем каждые 20 символов, добавляя zero-width space для переноса
        result = ""
        for i in range(0, len(word), 20):
            chunk = word[i:i+20]
            result += chunk
            # Добавляем zero-width space если это не последний кусок
            if i + 20 < len(word):
                result += "\u200B"  # Zero-width space для переноса
        
        return result


class InputWidget(QWidget):
    """
    Виджет области ввода сообщений в стиле современных чатов
    
    Следует принципам SOLID:
    - Single Responsibility: управляет вводом и отправкой сообщений
    - Open/Closed: может быть расширен новыми элементами управления
    """
    
    # Сигналы
    send_message = pyqtSignal(str)
    attach_file = pyqtSignal()
    change_model = pyqtSignal()
    change_mode = pyqtSignal()
    typing_started = pyqtSignal()
    typing_stopped = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.setup_connections()
        self.setup_style()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        
        # Основной контейнер для поля ввода
        self.input_container = QWidget()
        self.input_container.setFixedHeight(132)
        
        input_layout = QVBoxLayout(self.input_container)
        input_layout.setContentsMargins(10, 6, 10, 6)
        input_layout.setSpacing(0)
        
        # Кнопка добавления контекста
        self.context_button = QPushButton("@ Add Context")
        self.context_button.setFixedHeight(18)
        self.context_button.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        input_layout.addWidget(self.context_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Поле для ввода
        self.chat_input = ChatInputWidget()
        input_layout.addWidget(self.chat_input)
        
        # Нижняя секция с элементами управления
        bottom_section = self._create_bottom_section()
        input_layout.addWidget(bottom_section)
        
        layout.addWidget(self.input_container)
    
    def _create_bottom_section(self) -> QWidget:
        """Создание нижней секции с кнопками"""
        bottom_section = QWidget()
        bottom_layout = QHBoxLayout(bottom_section)
        bottom_layout.setContentsMargins(8, 6, 8, 6)
        bottom_layout.setSpacing(0)
        
        # Левая группа элементов управления
        left_controls = self._create_left_controls()
        bottom_layout.addWidget(left_controls)
        
        # Правая группа элементов управления
        right_controls = self._create_right_controls()
        bottom_layout.addWidget(right_controls)
        
        return bottom_section
    
    def _create_left_controls(self) -> QWidget:
        """Создание левой группы элементов управления"""
        left_controls = QWidget()
        left_layout = QHBoxLayout(left_controls)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # Кнопка режима AI
        self.ai_mode_button = QPushButton("AI mode")
        self.ai_mode_button.setFixedHeight(20)
        self.ai_mode_button.clicked.connect(self.change_mode.emit)
        left_layout.addWidget(self.ai_mode_button)
        
        # Кнопка выбора модели
        self.model_button = QPushButton("Model")
        self.model_button.setFixedHeight(20)
        self.model_button.clicked.connect(self.change_model.emit)
        left_layout.addWidget(self.model_button)
        
        left_layout.addStretch()
        return left_controls
    
    def _create_right_controls(self) -> QWidget:
        """Создание правой группы элементов управления"""
        right_controls = QWidget()
        right_layout = QHBoxLayout(right_controls)
        right_layout.setContentsMargins(4, 4, 4, 4)
        right_layout.setSpacing(0)
        
        # Кнопка прикрепления файла
        self.attach_button = QPushButton("+")
        self.attach_button.setFixedSize(100, 20)
        self.attach_button.clicked.connect(self.attach_file.emit)
        right_layout.addWidget(self.attach_button)
        
        # Кнопка отправки
        self.send_button = QPushButton("↑")
        self.send_button.setFixedSize(20, 20)
        self.send_button.clicked.connect(self._send_message)
        right_layout.addWidget(self.send_button)
        
        return right_controls
    
    def setup_connections(self):
        """Настройка сигналов и слотов"""
        self.chat_input.send_message_requested.connect(self.send_message.emit)
        self.chat_input.typing_started.connect(self.typing_started.emit)
        self.chat_input.typing_stopped.connect(self.typing_stopped.emit)
        
        # Подключение кнопки контекста
        self.context_button.clicked.connect(self._add_context)
    
    def setup_style(self):
        """Настройка стилей"""
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        
        # Стили для контейнера
        self.input_container.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border: none;
                border-radius: 16px;
                padding: 0px;
            }
        """)
        
        # Стили для кнопки контекста
        self.context_button.setStyleSheet("""
            QPushButton {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #404040;
                border-radius: 8px;
                padding: 2px 4px;
                font-size: 12px;
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
        
        # Стили для поля ввода
        self.chat_input.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
                color: #ffffff;
                font-size: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
                padding: 0px;
            }
        """)
        
        # Стили для кнопок управления
        control_button_style = """
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
        """
        
        self.ai_mode_button.setStyleSheet(control_button_style)
        self.model_button.setStyleSheet(control_button_style)
        
        # Стили для кнопки прикрепления
        self.attach_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #888888;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #cccccc;
            }
        """)
        
        # Стили для кнопки отправки
        self.send_button.setStyleSheet("""
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
    
    def _send_message(self):
        """Отправка сообщения"""
        text = self.chat_input.toPlainText().strip()
        if text:
            self.send_message.emit(text)
            self.chat_input.clear_and_focus()
    
    def _add_context(self):
        """Добавление контекста (заглушка)"""
        # TODO: Реализовать добавление контекста
        pass
    
    def set_enabled(self, enabled: bool):
        """Включение/отключение ввода"""
        self.chat_input.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        
        if enabled:
            self.chat_input.setPlaceholderText("Start chatting with AI...")
        else:
            self.chat_input.setPlaceholderText("Generating response...")
    
    def clear_input(self):
        """Очистка поля ввода"""
        self.chat_input.clear_and_focus()
    
    def get_input_text(self) -> str:
        """Получение текста из поля ввода"""
        return self.chat_input.toPlainText().strip()
    
    def set_input_text(self, text: str):
        """Установка текста в поле ввода"""
        self.chat_input.setPlainText(text)
    
    def focus_input(self):
        """Установка фокуса на поле ввода"""
        self.chat_input.setFocus()
    
    def update_model_info(self, model_name: str):
        """Обновление информации о модели"""
        self.model_button.setText(f"Model: {model_name}")
    
    def update_mode_info(self, mode_name: str):
        """Обновление информации о режиме"""
        self.ai_mode_button.setText(f"{mode_name} mode")

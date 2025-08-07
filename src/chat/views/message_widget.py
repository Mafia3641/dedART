"""
Виджет для отображения сообщений чата
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QFontMetrics

from ..models.chat_message import ChatMessage, MessageRole, MessageType
from ..utils.message_formatter import MessageFormatter


class MessageWidget(QWidget):
    """
    Виджет для отображения одного сообщения
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за отображение сообщения
    - Open/Closed: может быть расширен для новых типов сообщений
    """
    
    # Сигналы
    copy_requested = pyqtSignal(str)  # Копирование текста
    edit_requested = pyqtSignal(str)  # Редактирование сообщения
    delete_requested = pyqtSignal(str)  # Удаление сообщения
    
    def __init__(self, message: ChatMessage, parent=None):
        super().__init__(parent)
        self.message = message
        self.formatter = MessageFormatter()
        
        # Таймер для отложенного обновления размеров (исправление бага первого сообщения)
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self._delayed_resize)
        
        # Флаг для отслеживания первого показа
        self.first_show = True
        
        self.init_ui()
        self.setup_style()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Основной контейнер для сообщения
        self.message_container = QFrame()
        self.message_container.setFrameStyle(QFrame.Shape.NoFrame)
        
        # Layout для контейнера
        container_layout = QHBoxLayout(self.message_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(12)
        
        # Создаем содержимое в зависимости от роли
        if self.message.is_user_message:
            self._create_user_message_layout(container_layout)
        else:
            self._create_assistant_message_layout(container_layout)
        
        layout.addWidget(self.message_container)
    
    def _create_user_message_layout(self, layout: QHBoxLayout):
        """Создание layout для сообщения пользователя"""
        # Растягивающийся виджет слева (больше места)
        layout.addStretch(1)
        
        # Контейнер для сообщения (правое выравнивание)
        message_content = self._create_message_content()
        layout.addWidget(message_content, 0, Qt.AlignmentFlag.AlignRight)
    
    def _create_assistant_message_layout(self, layout: QHBoxLayout):
        """Создание layout для сообщения ассистента"""
        # Контейнер для сообщения (левое выравнивание)
        message_content = self._create_message_content()
        layout.addWidget(message_content, 0, Qt.AlignmentFlag.AlignLeft)
        
        # Растягивающийся виджет справа (больше места)
        layout.addStretch(1)
    
    def _create_message_content(self) -> QWidget:
        """Создание содержимого сообщения"""
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(8)
        
        # Фиксируем политику размера для предотвращения растягивания
        from PyQt6.QtWidgets import QSizePolicy
        content_widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        
        # Основное содержимое
        self.content_label = QLabel()
        self.content_label.setWordWrap(True)
        self.content_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        # Принудительный перенос длинных слов
        self.content_label.setScaledContents(False)
        
        # Устанавливаем правильную политику размера для QLabel
        from PyQt6.QtWidgets import QSizePolicy
        label_policy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.content_label.setSizePolicy(label_policy)
        
        # Устанавливаем содержимое с обработкой длинных слов
        processed_text = self._process_long_words(self.message.content)
        formatted_message = self.formatter.format_message_for_display_custom(processed_text)
        self.content_label.setText(formatted_message)
        
        # Настраиваем динамический размер
        self._setup_dynamic_sizing()
        
        # Принудительно обрабатываем события layout для первого отображения
        from PyQt6.QtWidgets import QApplication
        QApplication.processEvents()
        
        content_layout.addWidget(self.content_label)
        
        # Метаинформация (время, кнопки)
        meta_widget = self._create_meta_info()
        content_layout.addWidget(meta_widget)
        
        # Еще одна попытка правильно установить размеры после добавления в layout
        QApplication.processEvents()
        self._setup_dynamic_sizing()
        
        return content_widget
    
    def _create_meta_info(self) -> QWidget:
        """Создание виджета с метаинформацией"""
        meta_widget = QWidget()
        meta_layout = QHBoxLayout(meta_widget)
        meta_layout.setContentsMargins(0, 0, 0, 0)
        meta_layout.setSpacing(8)
        
        # Время сообщения
        time_label = QLabel(self.message.formatted_timestamp)
        time_label.setObjectName("timestamp")
        meta_layout.addWidget(time_label)
        
        # Добавляем кнопки действий для сообщений ассистента
        if self.message.is_assistant_message:
            self._add_action_buttons(meta_layout)
        
        meta_layout.addStretch()
        
        return meta_widget
    
    def _add_action_buttons(self, layout: QHBoxLayout):
        """Добавление кнопок действий"""
        # Кнопка копирования
        copy_btn = QPushButton("📋")
        copy_btn.setObjectName("actionButton")
        copy_btn.setToolTip("Копировать")
        copy_btn.setFixedSize(24, 24)
        copy_btn.clicked.connect(lambda: self.copy_requested.emit(self.message.content))
        layout.addWidget(copy_btn)
        
        # Кнопка редактирования (если это пользовательское сообщение)
        if self.message.is_user_message:
            edit_btn = QPushButton("✏️")
            edit_btn.setObjectName("actionButton")
            edit_btn.setToolTip("Редактировать")
            edit_btn.setFixedSize(24, 24)
            edit_btn.clicked.connect(lambda: self.edit_requested.emit(self.message.message_id))
            layout.addWidget(edit_btn)
    
    def setup_style(self):
        """Настройка стилей"""
        if self.message.is_user_message:
            self._apply_user_message_style()
        else:
            self._apply_assistant_message_style()
        
        # Общие стили
        self.setStyleSheet(self.styleSheet() + """
            QLabel#timestamp {
                color: #888888;
                font-size: 11px;
            }
            
            QPushButton#actionButton {
                background-color: transparent;
                border: none;
                font-size: 12px;
                border-radius: 12px;
            }
            
            QPushButton#actionButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
    
    def _apply_user_message_style(self):
        """Применение стилей для сообщения пользователя"""
        self.content_label.setStyleSheet("""
            QLabel {
                background-color: #007acc;
                color: white;
                border-radius: 16px;
                padding: 12px 18px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 1px solid #0098ff;
            }
        """)
    
    def _apply_assistant_message_style(self):
        """Применение стилей для сообщения ассистента"""
        self.content_label.setStyleSheet("""
            QLabel {
                background-color: #2d2d2d;
                color: #ffffff;
                border-radius: 16px;
                padding: 12px 18px;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 1px solid #404040;
            }
        """)
    
    def update_message(self, message: ChatMessage):
        """Обновление отображаемого сообщения"""
        self.message = message
        processed_text = self._process_long_words(message.content)
        formatted_message = self.formatter.format_message_for_display_custom(processed_text)
        self.content_label.setText(formatted_message)
        # Пересчитываем размеры для нового содержимого
        self._setup_dynamic_sizing()
    
    def get_message_id(self) -> str:
        """Получение ID сообщения"""
        return self.message.message_id
    
    def set_highlight(self, highlighted: bool):
        """Установка подсветки сообщения"""
        if highlighted:
            self.message_container.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 0, 0.1);
                    border-left: 3px solid #ffeb3b;
                }
            """)
        else:
            self.message_container.setStyleSheet("")
    
    def _setup_dynamic_sizing(self):
        """Настройка динамического размера пузыря сообщения"""
        text = self.message.content.strip()
        
        # Вычисляем оптимальный размер на основе длины текста
        optimal_width = self._calculate_optimal_width(text)
        
        # Устанавливаем только ширину - высота подстроится автоматически
        self.content_label.setFixedWidth(optimal_width[1])
        
        # Принудительно обновляем размеры для корректного отображения
        self.content_label.updateGeometry()
        self.updateGeometry()
        
        # Таймер для отложенного обновления убран - вместо этого используем callback от chat_view
    
    def _delayed_resize(self):
        """Отложенное обновление размеров для исправления бага первого сообщения"""
        self.content_label.adjustSize()
        self.content_label.updateGeometry()
        self.updateGeometry()
    
    def force_resize_update(self):
        """Принудительное обновление размеров (публичный метод)"""
        self._delayed_resize()
    
    def showEvent(self, event):
        """Обработка события показа виджета"""
        super().showEvent(event)
        
        # При первом показе принудительно обновляем размеры
        if self.first_show:
            self.first_show = False
            QTimer.singleShot(10, self.force_resize_update)
    
    def _calculate_optimal_width(self, text: str) -> tuple[int, int]:
        """Вычисление оптимальной ширины пузыря сообщения как в Telegram"""
        # Базовые параметры
        min_width = 50   # Минимальная ширина
        max_width = 420   # Максимальная ширина
        padding = 30    # Отступы (18px * 2)
        
        # Получаем метрики шрифта
        font = QFont('Segoe UI', 16)
        font_metrics = QFontMetrics(font)
        
        # Проверяем на длинные слова без пробелов
        has_long_words = any(len(word) > 25 for word in text.split())
        
        if has_long_words:
            # Для длинных слов используем максимальную ширину
            return int(min_width), int(max_width)
        
        # Для обычного текста измеряем реальную ширину
        lines = text.split('\n')
        max_line_width = 0
        
        for line in lines:
            # Измеряем точную ширину строки
            line_width = font_metrics.horizontalAdvance(line)
            max_line_width = max(max_line_width, line_width)
        
        # Добавляем отступы
        needed_width = max_line_width + padding
        
        # Применяем логику размеров
        if needed_width <= min_width:
            # Очень короткий текст
            optimal_width = min_width
        elif needed_width <= max_width * 0.7:
            # Умеренный текст - используем точную ширину + небольшой запас
            optimal_width = needed_width - 10
        else:
            # Длинный текст - используем максимальную ширину
            optimal_width = needed_width - padding - padding - 10
        
        # Финальные ограничения
        optimal_width = max(min_width, min(optimal_width, max_width))
        
        return int(min_width), int(optimal_width)
    
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


class TypingIndicator(QWidget):
    """
    Индикатор печати (для отображения что ИИ отвечает)
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за индикацию печати
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        self.animation_step = 0
        
        self.init_ui()
    
    def init_ui(self):
        """Инициализация UI индикатора"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Контейнер как у сообщения ассистента
        self.indicator_container = QWidget()
        self.indicator_container.setStyleSheet("""
            QWidget {
                background-color: #2d2d2d;
                border-radius: 16px;
                padding: 12px 18px;
                border: 1px solid #404040;
                max-width: 100px;
            }
        """)
        
        indicator_layout = QHBoxLayout(self.indicator_container)
        indicator_layout.setContentsMargins(12, 8, 12, 8)
        
        # Точки для анимации
        self.dots = []
        for i in range(3):
            dot = QLabel("●")
            dot.setStyleSheet("color: #666666; font-size: 16px;")
            self.dots.append(dot)
            indicator_layout.addWidget(dot)
        
        layout.addWidget(self.indicator_container)
        layout.addStretch()
    
    def start_animation(self):
        """Запуск анимации"""
        self.animation_timer.start(500)  # Обновление каждые 500мс
    
    def stop_animation(self):
        """Остановка анимации"""
        self.animation_timer.stop()
        # Сброс всех точек
        for dot in self.dots:
            dot.setStyleSheet("color: #666666; font-size: 16px;")
    
    def _animate(self):
        """Анимация точек"""
        # Сброс всех точек
        for dot in self.dots:
            dot.setStyleSheet("color: #666666; font-size: 16px;")
        
        # Подсвечиваем текущую точку
        if self.animation_step < len(self.dots):
            self.dots[self.animation_step].setStyleSheet("color: #ffffff; font-size: 16px;")
        
        self.animation_step = (self.animation_step + 1) % (len(self.dots) + 1)

"""
Основное представление чата
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
    QLabel, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from typing import List, Optional

from ..models.chat_message import ChatMessage
from .message_widget import MessageWidget, TypingIndicator
from .input_widget import InputWidget


class ChatView(QWidget):
    """
    Основное представление чата
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за отображение чата
    - Open/Closed: может быть расширено новыми элементами UI
    - Interface Segregation: предоставляет только необходимые сигналы
    """
    
    # Сигналы
    send_message = pyqtSignal(str)
    copy_message = pyqtSignal(str)
    edit_message = pyqtSignal(str)
    delete_message = pyqtSignal(str)
    attach_file = pyqtSignal()
    change_model = pyqtSignal()
    change_mode = pyqtSignal()
    typing_started = pyqtSignal()
    typing_stopped = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Хранение виджетов сообщений
        self.message_widgets: List[MessageWidget] = []
        self.typing_indicator: Optional[TypingIndicator] = None
        
        self.init_ui()
        self.setup_connections()
        self.setup_style()
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создание области сообщений
        self.messages_area = self._create_messages_area()
        layout.addWidget(self.messages_area, stretch=1)
        
        # Создание области ввода
        self.input_area = self._create_input_area()
        layout.addWidget(self.input_area, stretch=0)
    
    def _create_messages_area(self) -> QWidget:
        """Создание области сообщений"""
        # Центрирующий контейнер
        messages_row = QWidget()
        messages_row_layout = QHBoxLayout(messages_row)
        messages_row_layout.setContentsMargins(0, 0, 0, 0)
        messages_row_layout.setSpacing(0)
        messages_row_layout.addStretch()
        
        # Контейнер для сообщений
        self.messages_container = QWidget()
        self.messages_container.setFixedWidth(600)
        
        container_layout = QVBoxLayout(self.messages_container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(0)
        
        # Заголовок чата
        title = QLabel("Чат с ИИ")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setObjectName("chatTitle")
        container_layout.addWidget(title)
        
        # Область прокрутки для сообщений
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Виджет для сообщений
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setContentsMargins(0, 0, 0, 0)
        self.messages_layout.setSpacing(16)
        # Убираем addStretch() чтобы не было лишней прокрутки вверх
        
        self.scroll_area.setWidget(self.messages_widget)
        container_layout.addWidget(self.scroll_area)
        
        messages_row_layout.addWidget(self.messages_container)
        messages_row_layout.addStretch()
        
        return messages_row
    
    def _create_input_area(self) -> QWidget:
        """Создание области ввода"""
        # Центрирующий контейнер
        input_row = QWidget()
        input_row_layout = QHBoxLayout(input_row)
        input_row_layout.setContentsMargins(0, 0, 0, 0)
        input_row_layout.setSpacing(0)
        input_row_layout.addStretch()
        
        # Виджет ввода
        self.input_widget = InputWidget()
        self.input_widget.setFixedWidth(600)
        
        input_row_layout.addWidget(self.input_widget)
        input_row_layout.addStretch()
        
        return input_row
    
    def setup_connections(self):
        """Настройка сигналов и слотов"""
        # Сигналы от области ввода
        self.input_widget.send_message.connect(self.send_message.emit)
        self.input_widget.attach_file.connect(self.attach_file.emit)
        self.input_widget.change_model.connect(self.change_model.emit)
        self.input_widget.change_mode.connect(self.change_mode.emit)
        self.input_widget.typing_started.connect(self.typing_started.emit)
        self.input_widget.typing_stopped.connect(self.typing_stopped.emit)
    
    def setup_style(self):
        """Настройка стилей"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
            }
            
            QLabel#chatTitle {
                font-size: 22px;
                font-weight: 600;
                color: #ffffff;
                padding: 24px 0;
                margin-bottom: 16px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
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
    
    def add_message(self, message: ChatMessage):
        """Добавление сообщения в чат"""
        # Удаляем индикатор печати если он есть
        self._remove_typing_indicator()
        
        # Создаем виджет сообщения
        message_widget = MessageWidget(message)
        
        # Подключаем сигналы
        message_widget.copy_requested.connect(self.copy_message.emit)
        message_widget.edit_requested.connect(self.edit_message.emit)
        message_widget.delete_requested.connect(self.delete_message.emit)
        
        # Добавляем виджет
        self.message_widgets.append(message_widget)
        self.messages_layout.addWidget(message_widget)
        
        # Прокручиваем к новому сообщению
        QTimer.singleShot(100, self._scroll_to_bottom)
    
    def show_typing_indicator(self):
        """Показать индикатор печати"""
        if self.typing_indicator is not None:
            return
        
        # Создаем и добавляем индикатор
        self.typing_indicator = TypingIndicator()
        self.messages_layout.addWidget(self.typing_indicator)
        
        # Запускаем анимацию
        self.typing_indicator.start_animation()
        
        # Прокручиваем вниз
        QTimer.singleShot(100, self._scroll_to_bottom)
    
    def hide_typing_indicator(self):
        """Скрыть индикатор печати"""
        self._remove_typing_indicator()
    
    def _remove_typing_indicator(self):
        """Удаление индикатора печати"""
        if self.typing_indicator is not None:
            self.typing_indicator.stop_animation()
            self.messages_layout.removeWidget(self.typing_indicator)
            self.typing_indicator.deleteLater()
            self.typing_indicator = None
    
    def clear_messages(self):
        """Очистка всех сообщений"""
        # Удаляем все виджеты сообщений
        for widget in self.message_widgets:
            self.messages_layout.removeWidget(widget)
            widget.deleteLater()
        
        self.message_widgets.clear()
        
        # Удаляем индикатор печати
        self._remove_typing_indicator()
    
    def get_message_count(self) -> int:
        """Получение количества сообщений"""
        return len(self.message_widgets)
    
    def find_message_widget(self, message_id: str) -> Optional[MessageWidget]:
        """Поиск виджета сообщения по ID"""
        for widget in self.message_widgets:
            if widget.get_message_id() == message_id:
                return widget
        return None
    
    def update_message(self, message: ChatMessage):
        """Обновление сообщения"""
        widget = self.find_message_widget(message.message_id)
        if widget:
            widget.update_message(message)
    
    def remove_message(self, message_id: str):
        """Удаление сообщения"""
        widget = self.find_message_widget(message_id)
        if widget:
            self.messages_layout.removeWidget(widget)
            self.message_widgets.remove(widget)
            widget.deleteLater()
    
    def highlight_message(self, message_id: str, highlighted: bool = True):
        """Подсветка сообщения"""
        widget = self.find_message_widget(message_id)
        if widget:
            widget.set_highlight(highlighted)
    
    def _scroll_to_bottom(self):
        """Прокрутка к последнему сообщению"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Принудительно обновляем размеры последнего сообщения для исправления бага
        if self.message_widgets:
            self.message_widgets[-1].force_resize_update()
    
    def set_input_enabled(self, enabled: bool):
        """Включение/отключение ввода"""
        self.input_widget.set_enabled(enabled)
    
    def clear_input(self):
        """Очистка поля ввода"""
        self.input_widget.clear_input()
    
    def get_input_text(self) -> str:
        """Получение текста из поля ввода"""
        return self.input_widget.get_input_text()
    
    def set_input_text(self, text: str):
        """Установка текста в поле ввода"""
        self.input_widget.set_input_text(text)
    
    def focus_input(self):
        """Установка фокуса на поле ввода"""
        self.input_widget.focus_input()
    
    def update_model_info(self, model_name: str):
        """Обновление информации о модели"""
        self.input_widget.update_model_info(model_name)
    
    def update_mode_info(self, mode_name: str):
        """Обновление информации о режиме"""
        self.input_widget.update_mode_info(mode_name)
    
    def show_welcome_message(self):
        """Показать приветственное сообщение"""
        # Можно добавить логику для отображения приветственного сообщения
        pass
    
    def show_error_message(self, error_text: str):
        """Показать сообщение об ошибке"""
        # Можно добавить специальный виджет для отображения ошибок
        pass

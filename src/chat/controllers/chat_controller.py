"""
Контроллер чата - координирует взаимодействие между моделями и представлениями
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt6.QtWidgets import QApplication

from ..models.chat_message import ChatMessage, MessageRole, MessageType
from ..models.conversation import Conversation
from ..models.ai_response import AIResponse, ResponseStatus
from ..services.ai_service import BaseAIService, AIServiceFactory
from ..services.cache_service import CacheService
from ..services.command_processor import CommandProcessor, FileCommandHandler, UICommandHandler
from ..utils.chat_logger import ChatLogger
from ..utils.message_formatter import MessageFormatter
from ..views.chat_view import ChatView


class AIResponseWorker(QThread):
    """
    Рабочий поток для обработки запросов к ИИ
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за выполнение запросов к ИИ в отдельном потоке
    """
    
    # Сигналы
    response_ready = pyqtSignal(object)  # AIResponse
    error_occurred = pyqtSignal(str)
    
    def __init__(self, ai_service: BaseAIService, conversation: Conversation):
        super().__init__()
        self.ai_service = ai_service
        self.conversation = conversation
    
    def run(self):
        """Выполнение запроса к ИИ"""
        try:
            # Создаем новый event loop для этого потока
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Выполняем запрос
            response = loop.run_until_complete(
                self.ai_service.generate_response(self.conversation)
            )
            
            self.response_ready.emit(response)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
        
        finally:
            loop.close()


class ChatController(QObject):
    """
    Основной контроллер чата
    
    Следует принципам SOLID:
    - Single Responsibility: координирует работу чата
    - Open/Closed: может быть расширен новой функциональностью
    - Liskov Substitution: может работать с любыми реализациями сервисов
    - Interface Segregation: зависит только от необходимых интерфейсов
    - Dependency Inversion: зависит от абстракций, а не от конкретных реализаций
    """
    
    # Сигналы для уведомления внешних компонентов
    conversation_changed = pyqtSignal(object)  # Conversation
    error_occurred = pyqtSignal(str, str)  # error_type, error_message
    status_changed = pyqtSignal(str)  # status_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Инициализация компонентов
        self.logger = logging.getLogger(__name__)
        self.chat_logger = ChatLogger()
        self.formatter = MessageFormatter()
        
        # Сервисы
        self.ai_service: Optional[BaseAIService] = None
        self.cache_service = CacheService()
        self.command_processor = CommandProcessor()
        
        # Текущее состояние
        self.current_conversation: Optional[Conversation] = None
        self.view: Optional[ChatView] = None
        self.is_processing = False
        
        # Рабочий поток для ИИ
        self.ai_worker: Optional[AIResponseWorker] = None
        
        # Таймер для автосохранения
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save_conversation)
        self.auto_save_interval = 30000  # 30 секунд
        
        self._initialize_services()
        self.logger.info("ChatController инициализирован")
    
    def set_view(self, view: ChatView):
        """Установка представления"""
        if self.view:
            self._disconnect_view_signals()
        
        self.view = view
        self._connect_view_signals()
        
        # Инициализируем представление
        if self.current_conversation:
            self._load_conversation_to_view()
        
        self.logger.debug("Представление подключено к контроллеру")
    
    def create_new_conversation(self) -> Conversation:
        """Создание нового разговора"""
        try:
            # Сохраняем текущий разговор
            if self.current_conversation:
                self._save_current_conversation()
            
            # Создаем новый разговор
            self.current_conversation = Conversation()
            
            # Очищаем представление
            if self.view:
                self.view.clear_messages()
                self.view.focus_input()
            
            # Запускаем автосохранение
            self._start_auto_save()
            
            # Логируем событие
            self.chat_logger.log_conversation_created(self.current_conversation)
            
            # Уведомляем о изменении
            self.conversation_changed.emit(self.current_conversation)
            self.status_changed.emit("Создан новый разговор")
            
            self.logger.info(f"Создан новый разговор: {self.current_conversation.conversation_id}")
            return self.current_conversation
            
        except Exception as e:
            error_msg = f"Ошибка при создании нового разговора: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit("conversation_creation", error_msg)
            raise
    
    def load_conversation(self, conversation_id: str) -> bool:
        """Загрузка разговора по ID"""
        try:
            # Сохраняем текущий разговор
            if self.current_conversation:
                self._save_current_conversation()
            
            # Загружаем разговор из кеша
            conversation = self.cache_service.load_conversation(conversation_id)
            if not conversation:
                error_msg = f"Разговор {conversation_id} не найден"
                self.error_occurred.emit("conversation_not_found", error_msg)
                return False
            
            self.current_conversation = conversation
            
            # Загружаем в представление
            if self.view:
                self._load_conversation_to_view()
            
            # Запускаем автосохранение
            self._start_auto_save()
            
            # Логируем событие
            self.chat_logger.log_conversation_loaded(conversation)
            
            # Уведомляем о изменении
            self.conversation_changed.emit(self.current_conversation)
            self.status_changed.emit(f"Загружен разговор: {conversation.title}")
            
            self.logger.info(f"Загружен разговор: {conversation_id}")
            return True
            
        except Exception as e:
            error_msg = f"Ошибка при загрузке разговора: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit("conversation_loading", error_msg)
            return False
    
    def send_message(self, content: str):
        """Отправка сообщения"""
        if self.is_processing:
            self.status_changed.emit("Дождитесь завершения предыдущего запроса")
            return
        
        if not content.strip():
            return
        
        try:
            # Создаем разговор если его нет
            if not self.current_conversation:
                self.create_new_conversation()
            
            # Создаем сообщение пользователя
            user_message = ChatMessage(
                content=content.strip(),
                role=MessageRole.USER,
                message_type=MessageType.TEXT
            )
            
            # Добавляем сообщение в разговор
            self.current_conversation.add_message(user_message)
            
            # Отображаем в UI
            if self.view:
                self.view.add_message(user_message)
                self.view.clear_input()
                self.view.set_input_enabled(False)
                self.view.show_typing_indicator()
            
            # Логируем отправку
            self.chat_logger.log_message_sent(
                user_message, 
                self.current_conversation.conversation_id
            )
            
            # Запускаем обработку ИИ
            self._process_ai_response()
            
            # Обновляем статус
            self.status_changed.emit("Отправка сообщения...")
            
            self.logger.debug(f"Отправлено сообщение: {user_message.message_id}")
            
        except Exception as e:
            error_msg = f"Ошибка при отправке сообщения: {str(e)}"
            self.logger.error(error_msg)
            self.logger.exception("Полная трассировка ошибки:")  # Для отладки
            self.error_occurred.emit("message_sending", error_msg)
            self._reset_ui_state()
    
    def _process_ai_response(self):
        """Обработка ответа ИИ в отдельном потоке"""
        if not self.ai_service or not self.current_conversation:
            self._handle_ai_error("Сервис ИИ не инициализирован")
            return
        
        self.is_processing = True
        
        # Создаем рабочий поток
        self.ai_worker = AIResponseWorker(self.ai_service, self.current_conversation)
        self.ai_worker.response_ready.connect(self._handle_ai_response)
        self.ai_worker.error_occurred.connect(self._handle_ai_error)
        self.ai_worker.finished.connect(self._cleanup_worker)
        
        # Запускаем поток
        self.ai_worker.start()
        
        self.status_changed.emit("Генерация ответа...")
    
    def _handle_ai_response(self, ai_response: AIResponse):
        """Обработка полученного ответа от ИИ"""
        try:
            # Логируем получение ответа
            self.chat_logger.log_message_received(
                ai_response,
                self.current_conversation.conversation_id
            )
            
            if ai_response.is_successful:
                # Создаем сообщение ассистента
                from ..models.chat_message import MessageType
                assistant_message = ChatMessage(
                    content=ai_response.content,
                    role=MessageRole.ASSISTANT,
                    message_type=MessageType.TEXT  # Используем правильный тип
                )
                
                # Добавляем метаданные
                assistant_message.add_metadata("processing_time", ai_response.processing_time)
                assistant_message.add_metadata("model_info", ai_response.model_info)
                
                # Добавляем в разговор
                self.current_conversation.add_message(assistant_message)
                
                # Отображаем в UI
                if self.view:
                    self.view.hide_typing_indicator()
                    self.view.add_message(assistant_message)
                
                # Обрабатываем команды если есть
                if ai_response.has_commands:
                    self._process_commands(ai_response)
                
                self.status_changed.emit(f"Ответ получен за {ai_response.formatted_processing_time}")
                
            else:
                # Обрабатываем ошибку
                self._handle_ai_error(ai_response.error_message or "Неизвестная ошибка ИИ")
            
            self._reset_ui_state()
            
        except Exception as e:
            error_msg = f"Ошибка при обработке ответа ИИ: {str(e)}"
            self.logger.error(error_msg)
            self._handle_ai_error(error_msg)
    
    def _handle_ai_error(self, error_message: str):
        """Обработка ошибки ИИ"""
        self.chat_logger.log_error("ai_response", error_message)
        
        # Создаем системное сообщение об ошибке
        error_msg = ChatMessage(
            content=f"Ошибка при генерации ответа: {error_message}",
            role=MessageRole.SYSTEM,
            message_type=MessageType.ERROR
        )
        
        if self.current_conversation:
            self.current_conversation.add_message(error_msg)
        
        # Отображаем в UI
        if self.view:
            self.view.hide_typing_indicator()
            self.view.add_message(error_msg)
        
        self.error_occurred.emit("ai_response", error_message)
        self.status_changed.emit("Ошибка при генерации ответа")
        
        self._reset_ui_state()
    
    def _process_commands(self, ai_response: AIResponse):
        """Обработка команд от ИИ"""
        try:
            # Запускаем обработку команд в отдельном потоке
            asyncio.create_task(self._execute_commands_async(ai_response))
            
        except Exception as e:
            self.logger.error(f"Ошибка при обработке команд: {e}")
    
    async def _execute_commands_async(self, ai_response: AIResponse):
        """Асинхронное выполнение команд"""
        try:
            results = await self.command_processor.process_response(ai_response)
            
            for result in results:
                self.chat_logger.log_command_executed(
                    result.message,
                    result.success,
                    result.message
                )
                
                if not result.success:
                    self.error_occurred.emit("command_execution", result.error or result.message)
            
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении команд: {e}")
    
    def _reset_ui_state(self):
        """Сброс состояния UI"""
        self.is_processing = False
        
        if self.view:
            self.view.set_input_enabled(True)
            self.view.focus_input()
    
    def _cleanup_worker(self):
        """Очистка рабочего потока"""
        if self.ai_worker:
            self.ai_worker.deleteLater()
            self.ai_worker = None
    
    def _connect_view_signals(self):
        """Подключение сигналов представления"""
        if not self.view:
            return
        
        self.view.send_message.connect(self.send_message)
        self.view.copy_message.connect(self._copy_message)
        self.view.edit_message.connect(self._edit_message)
        self.view.delete_message.connect(self._delete_message)
        self.view.change_model.connect(self._change_model)
        self.view.change_mode.connect(self._change_mode)
    
    def _disconnect_view_signals(self):
        """Отключение сигналов представления"""
        if not self.view:
            return
        
        self.view.send_message.disconnect()
        self.view.copy_message.disconnect()
        self.view.edit_message.disconnect()
        self.view.delete_message.disconnect()
        self.view.change_model.disconnect()
        self.view.change_mode.disconnect()
    
    def _load_conversation_to_view(self):
        """Загрузка разговора в представление"""
        if not self.view or not self.current_conversation:
            return
        
        self.view.clear_messages()
        
        for message in self.current_conversation.messages:
            self.view.add_message(message)
        
        self.view.focus_input()
    
    def _copy_message(self, content: str):
        """Копирование сообщения в буфер обмена"""
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        self.status_changed.emit("Сообщение скопировано")
    
    def _edit_message(self, message_id: str):
        """Редактирование сообщения"""
        # TODO: Реализовать редактирование сообщений
        self.status_changed.emit("Редактирование сообщений пока не реализовано")
    
    def _delete_message(self, message_id: str):
        """Удаление сообщения"""
        if self.current_conversation:
            if self.current_conversation.remove_message(message_id):
                if self.view:
                    self.view.remove_message(message_id)
                self.status_changed.emit("Сообщение удалено")
    
    def _change_model(self):
        """Смена модели ИИ"""
        # TODO: Реализовать смену модели
        self.status_changed.emit("Смена модели пока не реализована")
    
    def _change_mode(self):
        """Смена режима ИИ"""
        # TODO: Реализовать смену режима
        self.status_changed.emit("Смена режима пока не реализована")
    
    def _save_current_conversation(self):
        """Сохранение текущего разговора"""
        if self.current_conversation:
            self.cache_service.save_conversation(self.current_conversation)
    
    def _auto_save_conversation(self):
        """Автоматическое сохранение разговора"""
        self._save_current_conversation()
        self.logger.debug("Автосохранение разговора выполнено")
    
    def _start_auto_save(self):
        """Запуск автосохранения"""
        self.auto_save_timer.start(self.auto_save_interval)
    
    def _stop_auto_save(self):
        """Остановка автосохранения"""
        self.auto_save_timer.stop()
    
    def _initialize_services(self):
        """Инициализация сервисов"""
        try:
            # Инициализация ИИ сервиса
            self.ai_service = AIServiceFactory.create_service("mock")
            
            # Регистрация обработчиков команд
            file_handler = FileCommandHandler()
            ui_handler = UICommandHandler()
            
            self.command_processor.register_handler(file_handler)
            self.command_processor.register_handler(ui_handler)
            
            self.logger.info("Сервисы инициализированы")
            
        except Exception as e:
            error_msg = f"Ошибка при инициализации сервисов: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit("service_initialization", error_msg)
    
    def get_conversation_list(self, limit: int = 50):
        """Получение списка разговоров"""
        return self.cache_service.get_conversation_list(limit)
    
    def search_conversations(self, query: str, limit: int = 20):
        """Поиск разговоров"""
        return self.cache_service.search_conversations(query, limit)
    
    def export_conversation(self, format_type: str = "markdown") -> str:
        """Экспорт текущего разговора"""
        if not self.current_conversation:
            return ""
        
        return self.formatter.format_conversation_for_export(
            self.current_conversation.messages,
            format_type
        )
    
    def get_chat_statistics(self) -> Dict[str, Any]:
        """Получение статистики чата"""
        stats = self.chat_logger.get_session_stats()
        cache_stats = self.cache_service.get_cache_stats()
        
        return {
            "session": stats,
            "cache": cache_stats,
            "current_conversation": {
                "id": self.current_conversation.conversation_id if self.current_conversation else None,
                "message_count": self.current_conversation.get_message_count() if self.current_conversation else 0,
                "title": self.current_conversation.title if self.current_conversation else None
            }
        }
    
    def cleanup(self):
        """Очистка ресурсов при закрытии"""
        try:
            # Останавливаем автосохранение
            self._stop_auto_save()
            
            # Сохраняем текущий разговор
            self._save_current_conversation()
            
            # Сохраняем статистику сессии
            self.chat_logger.save_session_stats()
            
            # Завершаем рабочий поток если он активен
            if self.ai_worker and self.ai_worker.isRunning():
                self.ai_worker.terminate()
                self.ai_worker.wait()
            
            self.logger.info("ChatController очищен")
            
        except Exception as e:
            self.logger.error(f"Ошибка при очистке ChatController: {e}")

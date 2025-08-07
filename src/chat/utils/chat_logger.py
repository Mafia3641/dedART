"""
Специализированный логгер для чата
"""

import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from ..models.chat_message import ChatMessage
from ..models.conversation import Conversation
from ..models.ai_response import AIResponse


class ChatLogger:
    """
    Специализированный логгер для чата
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за логирование чата
    - Open/Closed: может быть расширен новыми типами логирования
    """
    
    def __init__(self, log_dir: str = "logs/chat"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Настройка основного логгера
        self.logger = logging.getLogger(f"{__name__}.ChatLogger")
        
        # Настройка специализированного логгера для чата
        self.chat_logger = self._setup_chat_logger()
        
        # Файл для детального логирования
        self.detailed_log_file = self.log_dir / f"chat_detailed_{datetime.now().strftime('%Y%m%d')}.log"
        
        # Файл для статистики
        self.stats_file = self.log_dir / "chat_stats.json"
        
        # Статистика в памяти
        self.session_stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'errors': 0,
            'session_start': datetime.now().isoformat(),
            'conversations_created': 0,
            'total_processing_time': 0.0
        }
    
    def log_message_sent(self, message: ChatMessage, conversation_id: str) -> None:
        """Логирование отправленного сообщения"""
        try:
            log_data = {
                'event': 'message_sent',
                'timestamp': datetime.now().isoformat(),
                'conversation_id': conversation_id,
                'message_id': message.message_id,
                'message_type': message.message_type.value,
                'content_length': len(message.content),
                'metadata': message.metadata
            }
            
            self.chat_logger.info(f"Сообщение отправлено: {message.message_id}")
            self._write_detailed_log(log_data)
            
            self.session_stats['messages_sent'] += 1
            
        except Exception as e:
            self.logger.error(f"Ошибка при логировании отправленного сообщения: {e}")
    
    def log_message_received(self, ai_response: AIResponse, conversation_id: str) -> None:
        """Логирование полученного ответа"""
        try:
            log_data = {
                'event': 'message_received',
                'timestamp': datetime.now().isoformat(),
                'conversation_id': conversation_id,
                'response_status': ai_response.status.value,
                'response_type': ai_response.response_type.value,
                'content_length': len(ai_response.content),
                'processing_time': ai_response.processing_time,
                'model_info': ai_response.model_info,
                'has_commands': ai_response.has_commands,
                'commands_count': len(ai_response.commands)
            }
            
            if ai_response.has_error:
                log_data['error_message'] = ai_response.error_message
                self.chat_logger.warning(f"Получен ответ с ошибкой: {ai_response.error_message}")
                self.session_stats['errors'] += 1
            else:
                self.chat_logger.info(f"Получен ответ, время обработки: {ai_response.formatted_processing_time}")
            
            self._write_detailed_log(log_data)
            
            self.session_stats['messages_received'] += 1
            self.session_stats['total_processing_time'] += ai_response.processing_time
            
        except Exception as e:
            self.logger.error(f"Ошибка при логировании полученного ответа: {e}")
    
    def log_conversation_created(self, conversation: Conversation) -> None:
        """Логирование создания нового разговора"""
        try:
            log_data = {
                'event': 'conversation_created',
                'timestamp': datetime.now().isoformat(),
                'conversation_id': conversation.conversation_id,
                'title': conversation.title
            }
            
            self.chat_logger.info(f"Создан новый разговор: {conversation.conversation_id}")
            self._write_detailed_log(log_data)
            
            self.session_stats['conversations_created'] += 1
            
        except Exception as e:
            self.logger.error(f"Ошибка при логировании создания разговора: {e}")
    
    def log_conversation_loaded(self, conversation: Conversation) -> None:
        """Логирование загрузки разговора"""
        try:
            log_data = {
                'event': 'conversation_loaded',
                'timestamp': datetime.now().isoformat(),
                'conversation_id': conversation.conversation_id,
                'title': conversation.title,
                'message_count': conversation.get_message_count(),
                'created_at': conversation.created_at.isoformat()
            }
            
            self.chat_logger.info(f"Загружен разговор: {conversation.conversation_id}")
            self._write_detailed_log(log_data)
            
        except Exception as e:
            self.logger.error(f"Ошибка при логировании загрузки разговора: {e}")
    
    def log_error(self, error_type: str, error_message: str, 
                  context: Optional[Dict[str, Any]] = None) -> None:
        """Логирование ошибки"""
        try:
            log_data = {
                'event': 'error',
                'timestamp': datetime.now().isoformat(),
                'error_type': error_type,
                'error_message': error_message,
                'context': context or {}
            }
            
            self.chat_logger.error(f"Ошибка {error_type}: {error_message}")
            self._write_detailed_log(log_data)
            
            self.session_stats['errors'] += 1
            
        except Exception as e:
            self.logger.error(f"Ошибка при логировании ошибки: {e}")
    
    def log_command_executed(self, command_type: str, success: bool, 
                           message: str, execution_time: float = 0.0) -> None:
        """Логирование выполнения команды"""
        try:
            log_data = {
                'event': 'command_executed',
                'timestamp': datetime.now().isoformat(),
                'command_type': command_type,
                'success': success,
                'message': message,
                'execution_time': execution_time
            }
            
            if success:
                self.chat_logger.info(f"Команда выполнена: {command_type} - {message}")
            else:
                self.chat_logger.warning(f"Команда не выполнена: {command_type} - {message}")
            
            self._write_detailed_log(log_data)
            
        except Exception as e:
            self.logger.error(f"Ошибка при логировании выполнения команды: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Получение статистики текущей сессии"""
        current_time = datetime.now()
        session_duration = (current_time - datetime.fromisoformat(self.session_stats['session_start'])).total_seconds()
        
        stats = self.session_stats.copy()
        stats['session_duration_seconds'] = session_duration
        stats['average_processing_time'] = (
            self.session_stats['total_processing_time'] / max(self.session_stats['messages_received'], 1)
        )
        
        return stats
    
    def save_session_stats(self) -> None:
        """Сохранение статистики сессии"""
        try:
            stats = self.get_session_stats()
            
            # Загружаем существующие статистики
            all_stats = []
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    all_stats = json.load(f)
            
            # Добавляем статистику текущей сессии
            all_stats.append(stats)
            
            # Сохраняем обновленные статистики
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(all_stats, f, ensure_ascii=False, indent=2)
            
            self.logger.info("Статистика сессии сохранена")
            
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении статистики: {e}")
    
    def load_historical_stats(self) -> List[Dict[str, Any]]:
        """Загрузка исторических статистик"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке статистики: {e}")
            return []
    
    def _setup_chat_logger(self) -> logging.Logger:
        """Настройка специализированного логгера для чата"""
        chat_logger = logging.getLogger(f"{__name__}.Chat")
        chat_logger.setLevel(logging.DEBUG)
        
        # Файловый обработчик для чата
        chat_log_file = self.log_dir / f"chat_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(chat_log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Форматтер для чата
        formatter = logging.Formatter(
            "%(asctime)s - CHAT - %(levelname)s - %(message)s",
            datefmt="%H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        
        chat_logger.addHandler(file_handler)
        
        return chat_logger
    
    def _write_detailed_log(self, log_data: Dict[str, Any]) -> None:
        """Запись детального лога в JSON формате"""
        try:
            with open(self.detailed_log_file, 'a', encoding='utf-8') as f:
                json_line = json.dumps(log_data, ensure_ascii=False)
                f.write(json_line + '\n')
                
        except Exception as e:
            self.logger.error(f"Ошибка при записи детального лога: {e}")
    
    def cleanup_old_logs(self, days_to_keep: int = 30) -> int:
        """Очистка старых логов"""
        deleted_count = 0
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        try:
            for log_file in self.log_dir.glob("*.log"):
                file_date = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_count += 1
            
            self.logger.info(f"Удалено {deleted_count} старых лог-файлов")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Ошибка при очистке старых логов: {e}")
            return 0

"""
Модель разговора (диалога)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Iterator
import uuid
import json
from pathlib import Path

from .chat_message import ChatMessage, MessageRole


@dataclass
class Conversation:
    """
    Модель разговора/диалога
    
    Следует принципам SOLID:
    - Single Responsibility: управляет коллекцией сообщений
    - Open/Closed: может быть расширена новыми методами
    - Liskov Substitution: может быть заменена наследниками
    - Dependency Inversion: зависит от абстракций (ChatMessage)
    """
    
    conversation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "Новый разговор"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    messages: List[ChatMessage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, message: ChatMessage) -> None:
        """Добавление сообщения в разговор"""
        if not isinstance(message, ChatMessage):
            raise TypeError("message должен быть экземпляром ChatMessage")
        
        self.messages.append(message)
        self.updated_at = datetime.now()
        
        # Автоматически обновляем заголовок если это первое пользовательское сообщение
        if (self.title == "Новый разговор" and 
            message.is_user_message and 
            len(self.get_user_messages()) == 1):
            self.title = self._generate_title_from_message(message.content)
    
    def get_messages_by_role(self, role: MessageRole) -> List[ChatMessage]:
        """Получение сообщений по роли"""
        return [msg for msg in self.messages if msg.role == role]
    
    def get_user_messages(self) -> List[ChatMessage]:
        """Получение сообщений пользователя"""
        return self.get_messages_by_role(MessageRole.USER)
    
    def get_assistant_messages(self) -> List[ChatMessage]:
        """Получение сообщений ассистента"""
        return self.get_messages_by_role(MessageRole.ASSISTANT)
    
    def get_system_messages(self) -> List[ChatMessage]:
        """Получение системных сообщений"""
        return self.get_messages_by_role(MessageRole.SYSTEM)
    
    def get_last_message(self) -> Optional[ChatMessage]:
        """Получение последнего сообщения"""
        return self.messages[-1] if self.messages else None
    
    def get_last_user_message(self) -> Optional[ChatMessage]:
        """Получение последнего сообщения пользователя"""
        user_messages = self.get_user_messages()
        return user_messages[-1] if user_messages else None
    
    def get_last_assistant_message(self) -> Optional[ChatMessage]:
        """Получение последнего сообщения ассистента"""
        assistant_messages = self.get_assistant_messages()
        return assistant_messages[-1] if assistant_messages else None
    
    def get_message_count(self) -> int:
        """Получение количества сообщений"""
        return len(self.messages)
    
    def get_context_messages(self, limit: int = 10) -> List[ChatMessage]:
        """Получение последних сообщений для контекста"""
        return self.messages[-limit:] if limit > 0 else self.messages
    
    def clear_messages(self) -> None:
        """Очистка всех сообщений"""
        self.messages.clear()
        self.updated_at = datetime.now()
    
    def remove_message(self, message_id: str) -> bool:
        """Удаление сообщения по ID"""
        for i, message in enumerate(self.messages):
            if message.message_id == message_id:
                del self.messages[i]
                self.updated_at = datetime.now()
                return True
        return False
    
    def find_message(self, message_id: str) -> Optional[ChatMessage]:
        """Поиск сообщения по ID"""
        for message in self.messages:
            if message.message_id == message_id:
                return message
        return None
    
    def __iter__(self) -> Iterator[ChatMessage]:
        """Итерация по сообщениям"""
        return iter(self.messages)
    
    def __len__(self) -> int:
        """Длина разговора (количество сообщений)"""
        return len(self.messages)
    
    def __bool__(self) -> bool:
        """Проверка на пустоту"""
        return len(self.messages) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для сериализации"""
        return {
            'conversation_id': self.conversation_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'messages': [msg.to_dict() for msg in self.messages],
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Создание объекта из словаря"""
        conversation = cls(
            conversation_id=data['conversation_id'],
            title=data['title'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            metadata=data.get('metadata', {})
        )
        
        for msg_data in data['messages']:
            conversation.messages.append(ChatMessage.from_dict(msg_data))
        
        return conversation
    
    def save_to_file(self, file_path: Path) -> None:
        """Сохранение разговора в файл"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise IOError(f"Ошибка при сохранении разговора: {e}")
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> 'Conversation':
        """Загрузка разговора из файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            raise IOError(f"Ошибка при загрузке разговора: {e}")
    
    def _generate_title_from_message(self, content: str) -> str:
        """Генерация заголовка из первого сообщения"""
        # Ограничиваем длину заголовка
        max_length = 50
        if len(content) <= max_length:
            return content
        
        # Обрезаем по словам
        words = content.split()
        title = ""
        for word in words:
            if len(title + word + " ") <= max_length - 3:
                title += word + " "
            else:
                break
        
        return title.strip() + "..." if title else content[:max_length-3] + "..."

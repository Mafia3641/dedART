"""
Модель сообщения чата
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
import uuid


class MessageRole(Enum):
    """Роль отправителя сообщения"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageType(Enum):
    """Тип сообщения"""
    TEXT = "text"
    CODE = "code"
    IMAGE = "image"
    COMMAND = "command"
    ERROR = "error"


@dataclass
class ChatMessage:
    """
    Модель сообщения чата
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за хранение данных сообщения
    - Open/Closed: может быть расширена через наследование
    - Interface Segregation: содержит только необходимые поля
    """
    
    content: str
    role: MessageRole
    message_type: MessageType = MessageType.TEXT
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Валидация после создания объекта"""
        if not self.content.strip():
            raise ValueError("Содержимое сообщения не может быть пустым")
        
        if not isinstance(self.role, MessageRole):
            raise TypeError("role должен быть экземпляром MessageRole")
            
        if not isinstance(self.message_type, MessageType):
            raise TypeError("message_type должен быть экземпляром MessageType")
    
    @property
    def is_user_message(self) -> bool:
        """Проверка, является ли сообщение пользовательским"""
        return self.role == MessageRole.USER
    
    @property
    def is_assistant_message(self) -> bool:
        """Проверка, является ли сообщение от ассистента"""
        return self.role == MessageRole.ASSISTANT
    
    @property
    def is_system_message(self) -> bool:
        """Проверка, является ли сообщение системным"""
        return self.role == MessageRole.SYSTEM
    
    @property
    def formatted_timestamp(self) -> str:
        """Форматированная метка времени"""
        return self.timestamp.strftime("%H:%M:%S")
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для сериализации"""
        return {
            'message_id': self.message_id,
            'content': self.content,
            'role': self.role.value,
            'message_type': self.message_type.value,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Создание объекта из словаря"""
        return cls(
            message_id=data['message_id'],
            content=data['content'],
            role=MessageRole(data['role']),
            message_type=MessageType(data['message_type']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Добавление метаданных к сообщению"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Получение метаданных сообщения"""
        return self.metadata.get(key, default)

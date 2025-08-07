"""
Модель ответа от ИИ
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum


class ResponseStatus(Enum):
    """Статус ответа ИИ"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ResponseType(Enum):
    """Тип ответа ИИ"""
    TEXT = "text"
    CODE = "code"
    COMMAND = "command"
    IMAGE_GENERATION = "image_generation"
    FILE_MODIFICATION = "file_modification"


@dataclass
class AIResponse:
    """
    Модель ответа от ИИ
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за хранение данных ответа ИИ
    - Open/Closed: может быть расширена новыми типами ответов
    """
    
    content: str
    status: ResponseStatus
    response_type: ResponseType = ResponseType.TEXT
    timestamp: datetime = field(default_factory=datetime.now)
    processing_time: float = 0.0  # время обработки в секундах
    model_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    commands: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    
    def __post_init__(self):
        """Валидация после создания объекта"""
        if not isinstance(self.status, ResponseStatus):
            raise TypeError("status должен быть экземпляром ResponseStatus")
            
        if not isinstance(self.response_type, ResponseType):
            raise TypeError("response_type должен быть экземпляром ResponseType")
    
    @property
    def is_successful(self) -> bool:
        """Проверка успешности ответа"""
        return self.status == ResponseStatus.SUCCESS
    
    @property
    def has_error(self) -> bool:
        """Проверка наличия ошибки"""
        return self.status == ResponseStatus.ERROR
    
    @property
    def has_commands(self) -> bool:
        """Проверка наличия команд в ответе"""
        return len(self.commands) > 0
    
    @property
    def formatted_processing_time(self) -> str:
        """Форматированное время обработки"""
        if self.processing_time < 1:
            return f"{self.processing_time * 1000:.0f}мс"
        else:
            return f"{self.processing_time:.2f}с"
    
    def add_command(self, command_type: str, parameters: Dict[str, Any]) -> None:
        """Добавление команды к ответу"""
        command = {
            'type': command_type,
            'parameters': parameters,
            'timestamp': datetime.now().isoformat()
        }
        self.commands.append(command)
    
    def get_commands_by_type(self, command_type: str) -> List[Dict[str, Any]]:
        """Получение команд определенного типа"""
        return [cmd for cmd in self.commands if cmd.get('type') == command_type]
    
    def set_error(self, error_message: str) -> None:
        """Установка ошибки"""
        self.status = ResponseStatus.ERROR
        self.error_message = error_message
    
    def set_model_info(self, model_name: str, model_version: str = "", 
                      provider: str = "") -> None:
        """Установка информации о модели"""
        self.model_info = {
            'name': model_name,
            'version': model_version,
            'provider': provider
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертация в словарь для сериализации"""
        return {
            'content': self.content,
            'status': self.status.value,
            'response_type': self.response_type.value,
            'timestamp': self.timestamp.isoformat(),
            'processing_time': self.processing_time,
            'model_info': self.model_info,
            'metadata': self.metadata,
            'commands': self.commands,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIResponse':
        """Создание объекта из словаря"""
        return cls(
            content=data['content'],
            status=ResponseStatus(data['status']),
            response_type=ResponseType(data['response_type']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            processing_time=data['processing_time'],
            model_info=data.get('model_info', {}),
            metadata=data.get('metadata', {}),
            commands=data.get('commands', []),
            error_message=data.get('error_message')
        )
    
    @classmethod
    def create_error_response(cls, error_message: str, 
                            response_type: ResponseType = ResponseType.TEXT) -> 'AIResponse':
        """Создание ответа с ошибкой"""
        return cls(
            content="",
            status=ResponseStatus.ERROR,
            response_type=response_type,
            error_message=error_message
        )
    
    @classmethod
    def create_success_response(cls, content: str, 
                              response_type: ResponseType = ResponseType.TEXT,
                              processing_time: float = 0.0) -> 'AIResponse':
        """Создание успешного ответа"""
        return cls(
            content=content,
            status=ResponseStatus.SUCCESS,
            response_type=response_type,
            processing_time=processing_time
        )

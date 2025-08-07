"""
Сервис для работы с ИИ
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import logging

from ..models.chat_message import ChatMessage, MessageRole
from ..models.ai_response import AIResponse, ResponseStatus, ResponseType
from ..models.conversation import Conversation


class BaseAIService(ABC):
    """
    Базовый абстрактный класс для сервиса ИИ
    
    Следует принципам SOLID:
    - Interface Segregation: определяет только необходимые методы
    - Dependency Inversion: другие классы зависят от этой абстракции
    """
    
    @abstractmethod
    async def generate_response(self, conversation: Conversation) -> AIResponse:
        """Генерация ответа на основе разговора"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Проверка доступности сервиса"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Получение информации о модели"""
        pass


class MockAIService(BaseAIService):
    """
    Mock-реализация сервиса ИИ для демонстрации
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за имитацию ответов ИИ
    - Open/Closed: может быть заменена реальной реализацией
    - Liskov Substitution: полностью заменяет базовый класс
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.response_templates = [
            "Это демо-ответ от ИИ. Функция чата в разработке...",
            "Я понимаю ваш запрос. В данный момент это демо-версия чата.",
            "Спасибо за сообщение! Это тестовый ответ от ИИ.",
            "Ваш запрос обработан. Это демонстрационный ответ.",
            "Интересный вопрос! Пока что я отвечаю в демо-режиме."
        ]
        self.response_counter = 0
    
    async def generate_response(self, conversation: Conversation) -> AIResponse:
        """Генерация демо-ответа"""
        start_time = time.time()
        
        try:
            # Имитируем задержку обработки
            await asyncio.sleep(0.5 + (self.response_counter % 3) * 0.5)
            
            last_message = conversation.get_last_user_message()
            if not last_message:
                return AIResponse.create_error_response("Нет сообщений для обработки")
            
            # Генерируем демо-ответ на основе содержимого сообщения
            response_content = self._generate_demo_response(last_message.content)
            
            processing_time = time.time() - start_time
            
            response = AIResponse.create_success_response(
                content=response_content,
                response_type=ResponseType.TEXT,
                processing_time=processing_time
            )
            
            response.set_model_info("Demo AI", "1.0", "Mock Provider")
            response.metadata['message_count'] = conversation.get_message_count()
            
            self.logger.info(f"Сгенерирован демо-ответ за {response.formatted_processing_time}")
            
            return response
            
        except Exception as e:
            self.logger.error(f"Ошибка при генерации ответа: {e}")
            return AIResponse.create_error_response(f"Ошибка обработки: {str(e)}")
    
    def is_available(self) -> bool:
        """Демо-сервис всегда доступен"""
        return True
    
    def get_model_info(self) -> Dict[str, Any]:
        """Информация о демо-модели"""
        return {
            'name': 'Demo AI',
            'version': '1.0',
            'provider': 'Mock Provider',
            'type': 'demonstration',
            'capabilities': ['text_generation', 'conversation']
        }
    
    def _generate_demo_response(self, user_message: str) -> str:
        """Генерация демо-ответа на основе пользовательского сообщения"""
        # Анализируем содержимое сообщения для более релевантного ответа
        user_message_lower = user_message.lower()
        
        if any(word in user_message_lower for word in ['код', 'code', 'программ', 'скрипт']):
            return "Я понимаю, что вы спрашиваете о коде. В полной версии я смогу помочь с программированием и анализом кода."
        
        elif any(word in user_message_lower for word in ['рисунок', 'изображение', 'картинка', 'draw']):
            return "Вы интересуетесь работой с изображениями. В будущем я смогу помочь с генерацией и редактированием изображений."
        
        elif any(word in user_message_lower for word in ['файл', 'сохранить', 'открыть', 'file']):
            return "Понимаю, что вас интересуют операции с файлами. Я смогу помочь с этим, когда будет реализован полный функционал."
        
        elif '?' in user_message:
            return f"Интересный вопрос! В полной версии я смогу дать подробный ответ на: '{user_message[:50]}...'"
        
        else:
            # Используем циклический ответ из шаблонов
            response = self.response_templates[self.response_counter % len(self.response_templates)]
            self.response_counter += 1
            return response


class OpenAIService(BaseAIService):
    """
    Реализация сервиса для работы с OpenAI API
    (Заготовка для будущей реализации)
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(__name__)
    
    async def generate_response(self, conversation: Conversation) -> AIResponse:
        """Генерация ответа через OpenAI API"""
        # TODO: Реализовать интеграцию с OpenAI API
        return AIResponse.create_error_response("OpenAI интеграция пока не реализована")
    
    def is_available(self) -> bool:
        """Проверка доступности OpenAI API"""
        # TODO: Реализовать проверку доступности API
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Информация о модели OpenAI"""
        return {
            'name': self.model,
            'provider': 'OpenAI',
            'type': 'production'
        }


class AIServiceFactory:
    """
    Фабрика для создания сервисов ИИ
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за создание сервисов
    - Open/Closed: может быть расширена новыми типами сервисов
    - Dependency Inversion: возвращает абстракцию BaseAIService
    """
    
    @staticmethod
    def create_service(service_type: str = "mock", **kwargs) -> BaseAIService:
        """Создание сервиса ИИ"""
        if service_type == "mock":
            return MockAIService()
        elif service_type == "openai":
            api_key = kwargs.get('api_key')
            if not api_key:
                raise ValueError("Для OpenAI сервиса требуется api_key")
            return OpenAIService(api_key, kwargs.get('model', 'gpt-3.5-turbo'))
        else:
            raise ValueError(f"Неизвестный тип сервиса: {service_type}")
    
    @staticmethod
    def get_available_services() -> List[str]:
        """Получение списка доступных сервисов"""
        return ["mock", "openai"]

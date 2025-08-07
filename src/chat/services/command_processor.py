"""
Обработчик команд от ИИ
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from ..models.ai_response import AIResponse


class CommandType(Enum):
    """Типы команд"""
    CREATE_FILE = "create_file"
    MODIFY_FILE = "modify_file"
    DELETE_FILE = "delete_file"
    GENERATE_IMAGE = "generate_image"
    RUN_CODE = "run_code"
    OPEN_EDITOR = "open_editor"
    SWITCH_TAB = "switch_tab"
    CUSTOM = "custom"


@dataclass
class CommandResult:
    """Результат выполнения команды"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class BaseCommandHandler(ABC):
    """
    Базовый обработчик команд
    
    Следует принципам SOLID:
    - Single Responsibility: каждый обработчик отвечает за один тип команд
    - Open/Closed: можно добавлять новые обработчики без изменения существующих
    """
    
    @abstractmethod
    def can_handle(self, command_type: CommandType) -> bool:
        """Проверка возможности обработки команды"""
        pass
    
    @abstractmethod
    async def execute(self, command_type: CommandType, 
                     parameters: Dict[str, Any]) -> CommandResult:
        """Выполнение команды"""
        pass


class FileCommandHandler(BaseCommandHandler):
    """Обработчик команд для работы с файлами"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_commands = {
            CommandType.CREATE_FILE,
            CommandType.MODIFY_FILE,
            CommandType.DELETE_FILE
        }
    
    def can_handle(self, command_type: CommandType) -> bool:
        """Проверка поддержки команды"""
        return command_type in self.supported_commands
    
    async def execute(self, command_type: CommandType, 
                     parameters: Dict[str, Any]) -> CommandResult:
        """Выполнение файловой команды"""
        try:
            if command_type == CommandType.CREATE_FILE:
                return await self._create_file(parameters)
            elif command_type == CommandType.MODIFY_FILE:
                return await self._modify_file(parameters)
            elif command_type == CommandType.DELETE_FILE:
                return await self._delete_file(parameters)
            else:
                return CommandResult(
                    success=False,
                    message=f"Неподдерживаемая команда: {command_type}",
                    error="Unsupported command"
                )
                
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении команды {command_type}: {e}")
            return CommandResult(
                success=False,
                message=f"Ошибка выполнения команды: {str(e)}",
                error=str(e)
            )
    
    async def _create_file(self, parameters: Dict[str, Any]) -> CommandResult:
        """Создание файла"""
        # TODO: Реализовать создание файла
        file_path = parameters.get('path', '')
        content = parameters.get('content', '')
        
        return CommandResult(
            success=False,
            message=f"Создание файла {file_path} пока не реализовано",
            data={'path': file_path, 'content_length': len(content)}
        )
    
    async def _modify_file(self, parameters: Dict[str, Any]) -> CommandResult:
        """Модификация файла"""
        # TODO: Реализовать модификацию файла
        file_path = parameters.get('path', '')
        
        return CommandResult(
            success=False,
            message=f"Модификация файла {file_path} пока не реализована"
        )
    
    async def _delete_file(self, parameters: Dict[str, Any]) -> CommandResult:
        """Удаление файла"""
        # TODO: Реализовать удаление файла
        file_path = parameters.get('path', '')
        
        return CommandResult(
            success=False,
            message=f"Удаление файла {file_path} пока не реализовано"
        )


class UICommandHandler(BaseCommandHandler):
    """Обработчик команд пользовательского интерфейса"""
    
    def __init__(self, ui_callbacks: Optional[Dict[str, Callable]] = None):
        self.logger = logging.getLogger(__name__)
        self.ui_callbacks = ui_callbacks or {}
        self.supported_commands = {
            CommandType.OPEN_EDITOR,
            CommandType.SWITCH_TAB
        }
    
    def can_handle(self, command_type: CommandType) -> bool:
        """Проверка поддержки команды"""
        return command_type in self.supported_commands
    
    async def execute(self, command_type: CommandType, 
                     parameters: Dict[str, Any]) -> CommandResult:
        """Выполнение UI команды"""
        try:
            if command_type == CommandType.OPEN_EDITOR:
                return await self._open_editor(parameters)
            elif command_type == CommandType.SWITCH_TAB:
                return await self._switch_tab(parameters)
            else:
                return CommandResult(
                    success=False,
                    message=f"Неподдерживаемая UI команда: {command_type}",
                    error="Unsupported UI command"
                )
                
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении UI команды {command_type}: {e}")
            return CommandResult(
                success=False,
                message=f"Ошибка выполнения UI команды: {str(e)}",
                error=str(e)
            )
    
    async def _open_editor(self, parameters: Dict[str, Any]) -> CommandResult:
        """Открытие редактора"""
        callback = self.ui_callbacks.get('open_editor')
        if callback:
            try:
                callback(parameters)
                return CommandResult(
                    success=True,
                    message="Редактор открыт"
                )
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"Ошибка при открытии редактора: {str(e)}",
                    error=str(e)
                )
        
        return CommandResult(
            success=False,
            message="Callback для открытия редактора не настроен"
        )
    
    async def _switch_tab(self, parameters: Dict[str, Any]) -> CommandResult:
        """Переключение вкладки"""
        tab_name = parameters.get('tab', '')
        callback = self.ui_callbacks.get('switch_tab')
        
        if callback:
            try:
                callback(tab_name)
                return CommandResult(
                    success=True,
                    message=f"Переключено на вкладку: {tab_name}"
                )
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"Ошибка при переключении вкладки: {str(e)}",
                    error=str(e)
                )
        
        return CommandResult(
            success=False,
            message="Callback для переключения вкладки не настроен"
        )


class CommandProcessor:
    """
    Главный процессор команд
    
    Следует принципам SOLID:
    - Single Responsibility: координирует выполнение команд
    - Open/Closed: можно добавлять новые обработчики
    - Dependency Inversion: зависит от абстракции BaseCommandHandler
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.handlers: List[BaseCommandHandler] = []
        self.command_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
    
    def register_handler(self, handler: BaseCommandHandler) -> None:
        """Регистрация обработчика команд"""
        if not isinstance(handler, BaseCommandHandler):
            raise TypeError("Handler должен наследоваться от BaseCommandHandler")
        
        self.handlers.append(handler)
        self.logger.debug(f"Зарегистрирован обработчик: {type(handler).__name__}")
    
    def unregister_handler(self, handler: BaseCommandHandler) -> bool:
        """Отмена регистрации обработчика"""
        try:
            self.handlers.remove(handler)
            return True
        except ValueError:
            return False
    
    async def process_response(self, ai_response: AIResponse) -> List[CommandResult]:
        """Обработка команд из ответа ИИ"""
        if not ai_response.has_commands:
            return []
        
        results = []
        
        for command_data in ai_response.commands:
            try:
                command_type_str = command_data.get('type', '')
                command_type = CommandType(command_type_str)
                parameters = command_data.get('parameters', {})
                
                result = await self.execute_command(command_type, parameters)
                results.append(result)
                
                # Добавляем в историю
                self._add_to_history(command_type, parameters, result)
                
            except ValueError as e:
                error_result = CommandResult(
                    success=False,
                    message=f"Неизвестный тип команды: {command_type_str}",
                    error=str(e)
                )
                results.append(error_result)
                self.logger.error(f"Неизвестный тип команды: {command_type_str}")
            
            except Exception as e:
                error_result = CommandResult(
                    success=False,
                    message=f"Ошибка при обработке команды: {str(e)}",
                    error=str(e)
                )
                results.append(error_result)
                self.logger.error(f"Ошибка при обработке команды: {e}")
        
        return results
    
    async def execute_command(self, command_type: CommandType, 
                            parameters: Dict[str, Any]) -> CommandResult:
        """Выполнение отдельной команды"""
        # Находим подходящий обработчик
        for handler in self.handlers:
            if handler.can_handle(command_type):
                self.logger.debug(f"Выполнение команды {command_type} через {type(handler).__name__}")
                return await handler.execute(command_type, parameters)
        
        # Если обработчик не найден
        return CommandResult(
            success=False,
            message=f"Не найден обработчик для команды: {command_type}",
            error="No handler found"
        )
    
    def get_command_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Получение истории команд"""
        return self.command_history[-limit:] if limit > 0 else self.command_history
    
    def clear_history(self) -> None:
        """Очистка истории команд"""
        self.command_history.clear()
        self.logger.debug("История команд очищена")
    
    def get_supported_commands(self) -> List[CommandType]:
        """Получение списка поддерживаемых команд"""
        supported = set()
        for handler in self.handlers:
            for command_type in CommandType:
                if handler.can_handle(command_type):
                    supported.add(command_type)
        return list(supported)
    
    def _add_to_history(self, command_type: CommandType, 
                       parameters: Dict[str, Any], result: CommandResult) -> None:
        """Добавление команды в историю"""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'command_type': command_type.value,
            'parameters': parameters,
            'success': result.success,
            'message': result.message,
            'error': result.error
        }
        
        self.command_history.append(history_entry)
        
        # Ограничиваем размер истории
        if len(self.command_history) > self.max_history_size:
            self.command_history = self.command_history[-self.max_history_size:]

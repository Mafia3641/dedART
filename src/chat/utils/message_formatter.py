"""
Форматирование сообщений чата
"""

import re
import html
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.chat_message import ChatMessage, MessageRole, MessageType


class MessageFormatter:
    """
    Форматировщик сообщений чата
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за форматирование сообщений
    - Open/Closed: может быть расширен новыми форматами
    """
    
    def __init__(self):
        # Регулярные выражения для различных элементов
        self.code_block_pattern = re.compile(r'```(\w+)?\n(.*?)\n```', re.DOTALL)
        self.inline_code_pattern = re.compile(r'`([^`]+)`')
        self.bold_pattern = re.compile(r'\*\*(.*?)\*\*')
        self.italic_pattern = re.compile(r'\*(.*?)\*')
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
    def format_message_for_display(self, message: ChatMessage) -> Dict[str, Any]:
        """Форматирование сообщения для отображения в UI"""
        formatted_content = self._format_content(message.content, message.message_type)
        
        return {
            'id': message.message_id,
            'content': formatted_content,
            'html_content': self._to_html(formatted_content, message.message_type),
            'role': message.role.value,
            'message_type': message.message_type.value,
            'timestamp': message.formatted_timestamp,
            'is_user': message.is_user_message,
            'is_assistant': message.is_assistant_message,
            'is_system': message.is_system_message,
            'metadata': message.metadata
        }
    
    def format_conversation_for_export(self, messages: List[ChatMessage], 
                                     format_type: str = "markdown") -> str:
        """Форматирование разговора для экспорта"""
        if format_type == "markdown":
            return self._to_markdown(messages)
        elif format_type == "text":
            return self._to_plain_text(messages)
        elif format_type == "html":
            return self._to_html_document(messages)
        else:
            raise ValueError(f"Неподдерживаемый формат: {format_type}")
    
    def extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Извлечение блоков кода из сообщения"""
        code_blocks = []
        matches = self.code_block_pattern.findall(content)
        
        for language, code in matches:
            code_blocks.append({
                'language': language or 'text',
                'code': code.strip()
            })
        
        return code_blocks
    
    def extract_commands(self, content: str) -> List[str]:
        """Извлечение команд из сообщения"""
        # Простая реализация для извлечения команд
        # Команды начинаются с / или @
        command_pattern = re.compile(r'[/@](\w+)')
        commands = command_pattern.findall(content)
        return commands
    
    def _format_content(self, content: str, message_type: MessageType) -> str:
        """Базовое форматирование содержимого"""
        if message_type == MessageType.CODE:
            return self._format_code_content(content)
        elif message_type == MessageType.ERROR:
            return self._format_error_content(content)
        else:
            return self._format_text_content(content)
    
    def _format_text_content(self, content: str) -> str:
        """Форматирование текстового содержимого"""
        # Базовая обработка markdown-подобного синтаксиса
        formatted = content
        
        # Экранируем HTML
        formatted = html.escape(formatted)
        
        # Применяем форматирование
        formatted = self.bold_pattern.sub(r'<strong>\1</strong>', formatted)
        formatted = self.italic_pattern.sub(r'<em>\1</em>', formatted)
        formatted = self.inline_code_pattern.sub(r'<code>\1</code>', formatted)
        formatted = self.link_pattern.sub(r'<a href="\2" target="_blank">\1</a>', formatted)
        
        # Обрабатываем блоки кода
        formatted = self.code_block_pattern.sub(
            lambda m: f'<pre><code class="language-{m.group(1) or "text"}">{html.escape(m.group(2))}</code></pre>',
            formatted
        )
        
        # Конвертируем переносы строк
        formatted = formatted.replace('\n', '<br>')
        
        return formatted
    
    def _format_code_content(self, content: str) -> str:
        """Форматирование кода"""
        escaped_content = html.escape(content)
        return f'<pre><code>{escaped_content}</code></pre>'
    
    def _format_error_content(self, content: str) -> str:
        """Форматирование сообщения об ошибке"""
        escaped_content = html.escape(content)
        return f'<div class="error-message">{escaped_content}</div>'
    
    def _to_html(self, content: str, message_type: MessageType) -> str:
        """Конвертация в HTML"""
        css_class = self._get_css_class_for_message_type(message_type)
        return f'<div class="{css_class}">{content}</div>'
    
    def _to_markdown(self, messages: List[ChatMessage]) -> str:
        """Конвертация в Markdown"""
        lines = []
        lines.append(f"# Экспорт разговора")
        lines.append(f"Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        for message in messages:
            role_name = self._get_role_display_name(message.role)
            timestamp = message.formatted_timestamp
            
            lines.append(f"## {role_name} ({timestamp})")
            lines.append("")
            
            if message.message_type == MessageType.CODE:
                lines.append("```")
                lines.append(message.content)
                lines.append("```")
            else:
                lines.append(message.content)
            
            lines.append("")
        
        return "\n".join(lines)
    
    def _to_plain_text(self, messages: List[ChatMessage]) -> str:
        """Конвертация в простой текст"""
        lines = []
        lines.append(f"Экспорт разговора - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 50)
        lines.append("")
        
        for message in messages:
            role_name = self._get_role_display_name(message.role)
            timestamp = message.formatted_timestamp
            
            lines.append(f"[{timestamp}] {role_name}:")
            lines.append("-" * 30)
            lines.append(message.content)
            lines.append("")
        
        return "\n".join(lines)
    
    def _to_html_document(self, messages: List[ChatMessage]) -> str:
        """Конвертация в полный HTML документ"""
        html_parts = []
        html_parts.append("""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Экспорт разговора</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .message { margin: 20px 0; padding: 15px; border-radius: 8px; }
        .user-message { background-color: #e3f2fd; text-align: right; }
        .assistant-message { background-color: #f5f5f5; }
        .system-message { background-color: #fff3e0; font-style: italic; }
        .timestamp { font-size: 0.8em; color: #666; }
        .role { font-weight: bold; margin-bottom: 5px; }
        pre { background-color: #f8f8f8; padding: 10px; border-radius: 4px; overflow-x: auto; }
        code { background-color: #f0f0f0; padding: 2px 4px; border-radius: 2px; }
    </style>
</head>
<body>
        """)
        
        html_parts.append(f"<h1>Экспорт разговора</h1>")
        html_parts.append(f"<p>Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        
        for message in messages:
            css_class = f"{message.role.value}-message"
            role_name = self._get_role_display_name(message.role)
            formatted_content = self._format_content(message.content, message.message_type)
            
            html_parts.append(f'<div class="message {css_class}">')
            html_parts.append(f'<div class="role">{role_name}</div>')
            html_parts.append(f'<div class="timestamp">{message.formatted_timestamp}</div>')
            html_parts.append(f'<div class="content">{formatted_content}</div>')
            html_parts.append('</div>')
        
        html_parts.append("</body></html>")
        
        return "\n".join(html_parts)
    
    def _get_role_display_name(self, role: MessageRole) -> str:
        """Получение отображаемого имени роли"""
        role_names = {
            MessageRole.USER: "Пользователь",
            MessageRole.ASSISTANT: "Ассистент",
            MessageRole.SYSTEM: "Система"
        }
        return role_names.get(role, str(role.value))
    
    def _get_css_class_for_message_type(self, message_type: MessageType) -> str:
        """Получение CSS класса для типа сообщения"""
        type_classes = {
            MessageType.TEXT: "message-text",
            MessageType.CODE: "message-code",
            MessageType.IMAGE: "message-image",
            MessageType.COMMAND: "message-command",
            MessageType.ERROR: "message-error"
        }
        return type_classes.get(message_type, "message-text")
    
    def highlight_search_terms(self, content: str, search_terms: List[str]) -> str:
        """Подсветка поисковых терминов в тексте"""
        if not search_terms:
            return content
        
        highlighted = content
        for term in search_terms:
            if term.strip():
                # Создаем регулярное выражение для поиска термина (без учета регистра)
                pattern = re.compile(re.escape(term), re.IGNORECASE)
                highlighted = pattern.sub(
                    lambda m: f'<mark>{m.group(0)}</mark>',
                    highlighted
                )
        
        return highlighted
    
    def truncate_content(self, content: str, max_length: int = 100, 
                        add_ellipsis: bool = True) -> str:
        """Обрезка содержимого до определенной длины"""
        if len(content) <= max_length:
            return content
        
        truncated = content[:max_length]
        
        # Пытаемся обрезать по словам
        if ' ' in truncated:
            truncated = truncated.rsplit(' ', 1)[0]
        
        if add_ellipsis:
            truncated += "..."
        
        return truncated
    
    def format_message_for_display_custom(self, text: str) -> str:
        """Простое форматирование текста без сложной обработки"""
        # Экранируем HTML
        import html
        escaped_text = html.escape(text)
        
        # Конвертируем переносы строк
        formatted_text = escaped_text.replace('\n', '<br>')
        
        return formatted_text

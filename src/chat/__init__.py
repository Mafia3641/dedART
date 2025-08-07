"""
Модуль чата с архитектурой MVC
"""

from .controllers.chat_controller import ChatController
from .models.chat_message import ChatMessage
from .models.conversation import Conversation
from .views.chat_view import ChatView

__all__ = [
    'ChatController',
    'ChatMessage', 
    'Conversation',
    'ChatView'
]

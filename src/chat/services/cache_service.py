"""
Сервис кеширования разговоров
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from ..models.conversation import Conversation


class CacheService:
    """
    Сервис для кеширования и управления разговорами
    
    Следует принципам SOLID:
    - Single Responsibility: отвечает только за кеширование данных
    - Open/Closed: может быть расширен новыми методами кеширования
    - Interface Segregation: предоставляет только необходимые методы
    """
    
    def __init__(self, cache_dir: str = "cache/conversations"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Кеш в памяти для быстрого доступа
        self._memory_cache: Dict[str, Conversation] = {}
        self._cache_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Настройки кеширования
        self.max_memory_cache_size = 50  # Максимальное количество разговоров в памяти
        self.cache_expiry_days = 30  # Срок хранения кеша на диске
        
        self._load_cache_metadata()
    
    def save_conversation(self, conversation: Conversation) -> bool:
        """Сохранение разговора в кеш"""
        try:
            # Сохраняем в память
            self._memory_cache[conversation.conversation_id] = conversation
            
            # Обновляем метаданные
            self._cache_metadata[conversation.conversation_id] = {
                'title': conversation.title,
                'created_at': conversation.created_at.isoformat(),
                'updated_at': conversation.updated_at.isoformat(),
                'message_count': conversation.get_message_count(),
                'last_access': datetime.now().isoformat()
            }
            
            # Сохраняем на диск
            file_path = self._get_conversation_file_path(conversation.conversation_id)
            conversation.save_to_file(file_path)
            
            # Управляем размером кеша в памяти
            self._manage_memory_cache()
            
            # Сохраняем метаданные
            self._save_cache_metadata()
            
            self.logger.debug(f"Разговор {conversation.conversation_id} сохранен в кеш")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении разговора в кеш: {e}")
            return False
    
    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Загрузка разговора из кеша"""
        try:
            # Сначала проверяем кеш в памяти
            if conversation_id in self._memory_cache:
                self._update_last_access(conversation_id)
                return self._memory_cache[conversation_id]
            
            # Загружаем с диска
            file_path = self._get_conversation_file_path(conversation_id)
            if file_path.exists():
                conversation = Conversation.load_from_file(file_path)
                
                # Добавляем в кеш памяти
                self._memory_cache[conversation_id] = conversation
                self._update_last_access(conversation_id)
                
                self.logger.debug(f"Разговор {conversation_id} загружен из кеша")
                return conversation
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке разговора из кеша: {e}")
            return None
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Удаление разговора из кеша"""
        try:
            # Удаляем из памяти
            if conversation_id in self._memory_cache:
                del self._memory_cache[conversation_id]
            
            # Удаляем с диска
            file_path = self._get_conversation_file_path(conversation_id)
            if file_path.exists():
                file_path.unlink()
            
            # Удаляем метаданные
            if conversation_id in self._cache_metadata:
                del self._cache_metadata[conversation_id]
            
            self._save_cache_metadata()
            
            self.logger.debug(f"Разговор {conversation_id} удален из кеша")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при удалении разговора из кеша: {e}")
            return False
    
    def get_conversation_list(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение списка разговоров"""
        try:
            # Сортируем по времени последнего обновления
            sorted_conversations = sorted(
                self._cache_metadata.items(),
                key=lambda x: x[1]['updated_at'],
                reverse=True
            )
            
            return [
                {
                    'conversation_id': conv_id,
                    **metadata
                }
                for conv_id, metadata in sorted_conversations[:limit]
            ]
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка разговоров: {e}")
            return []
    
    def search_conversations(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Поиск разговоров по названию"""
        try:
            query_lower = query.lower()
            matching_conversations = []
            
            for conv_id, metadata in self._cache_metadata.items():
                if query_lower in metadata['title'].lower():
                    matching_conversations.append({
                        'conversation_id': conv_id,
                        **metadata
                    })
            
            # Сортируем по релевантности и времени
            matching_conversations.sort(
                key=lambda x: (
                    x['title'].lower().index(query_lower),  # Релевантность
                    -datetime.fromisoformat(x['updated_at']).timestamp()  # Время
                )
            )
            
            return matching_conversations[:limit]
            
        except Exception as e:
            self.logger.error(f"Ошибка при поиске разговоров: {e}")
            return []
    
    def clear_cache(self, max_age_days: Optional[int] = None) -> int:
        """Очистка старого кеша"""
        if max_age_days is None:
            max_age_days = self.cache_expiry_days
        
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0
        
        try:
            conversations_to_delete = []
            
            for conv_id, metadata in self._cache_metadata.items():
                updated_at = datetime.fromisoformat(metadata['updated_at'])
                if updated_at < cutoff_date:
                    conversations_to_delete.append(conv_id)
            
            for conv_id in conversations_to_delete:
                if self.delete_conversation(conv_id):
                    deleted_count += 1
            
            self.logger.info(f"Удалено {deleted_count} старых разговоров")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Ошибка при очистке кеша: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кеша"""
        try:
            total_conversations = len(self._cache_metadata)
            memory_cached = len(self._memory_cache)
            
            total_messages = sum(
                metadata.get('message_count', 0) 
                for metadata in self._cache_metadata.values()
            )
            
            cache_size_mb = sum(
                file.stat().st_size 
                for file in self.cache_dir.glob("*.json")
            ) / (1024 * 1024)
            
            return {
                'total_conversations': total_conversations,
                'memory_cached': memory_cached,
                'total_messages': total_messages,
                'cache_size_mb': round(cache_size_mb, 2),
                'cache_directory': str(self.cache_dir)
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении статистики кеша: {e}")
            return {}
    
    def _get_conversation_file_path(self, conversation_id: str) -> Path:
        """Получение пути к файлу разговора"""
        return self.cache_dir / f"{conversation_id}.json"
    
    def _manage_memory_cache(self):
        """Управление размером кеша в памяти"""
        if len(self._memory_cache) <= self.max_memory_cache_size:
            return
        
        # Удаляем наименее используемые разговоры
        conversations_by_access = sorted(
            self._cache_metadata.items(),
            key=lambda x: x[1].get('last_access', '1970-01-01T00:00:00')
        )
        
        # Удаляем старые разговоры из памяти
        conversations_to_remove = len(self._memory_cache) - self.max_memory_cache_size
        
        for i in range(conversations_to_remove):
            conv_id = conversations_by_access[i][0]
            if conv_id in self._memory_cache:
                del self._memory_cache[conv_id]
    
    def _update_last_access(self, conversation_id: str):
        """Обновление времени последнего доступа"""
        if conversation_id in self._cache_metadata:
            self._cache_metadata[conversation_id]['last_access'] = datetime.now().isoformat()
    
    def _load_cache_metadata(self):
        """Загрузка метаданных кеша"""
        metadata_file = self.cache_dir / "metadata.json"
        
        try:
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    self._cache_metadata = json.load(f)
            else:
                self._cache_metadata = {}
                
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке метаданных кеша: {e}")
            self._cache_metadata = {}
    
    def _save_cache_metadata(self):
        """Сохранение метаданных кеша"""
        metadata_file = self.cache_dir / "metadata.json"
        
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache_metadata, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении метаданных кеша: {e}")

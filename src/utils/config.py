"""
Работа с конфигурацией приложения
"""

import configparser
from pathlib import Path
from typing import Any, Dict, Optional


class Config:
    """Класс для работы с конфигурацией приложения"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = Path(config_file)
        self.config = configparser.ConfigParser()
        self.load_config()
    
    def load_config(self):
        """Загрузка конфигурации из файла"""
        if self.config_file.exists():
            try:
                self.config.read(self.config_file, encoding='utf-8')
            except Exception as e:
                print(f"Ошибка при загрузке конфигурации: {e}")
                self.create_default_config()
        else:
            self.create_default_config()
    
    def create_default_config(self):
        """Создание конфигурации по умолчанию"""
        # Основные настройки
        self.config['General'] = {
            'theme': 'dark',
            'language': 'ru',
            'auto_save': 'true',
            'auto_save_interval': '300'
        }
        
        # Настройки редактора
        self.config['Editor'] = {
            'font_family': 'Consolas',
            'font_size': '12',
            'tab_size': '4',
            'line_numbers': 'true',
            'word_wrap': 'false',
            'auto_indent': 'true'
        }
        
        # Настройки интерфейса
        self.config['Interface'] = {
            'toolbar_visible': 'true',
            'statusbar_visible': 'true',
            'menubar_visible': 'true',
            'window_width': '1200',
            'window_height': '800'
        }
        
        # Настройки файлов
        self.config['Files'] = {
            'default_encoding': 'utf-8',
            'remember_open_files': 'true',
            'max_recent_files': '10'
        }
        
        self.save_config()
    
    def save_config(self):
        """Сохранение конфигурации в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                self.config.write(configfile)
        except Exception as e:
            print(f"Ошибка при сохранении конфигурации: {e}")
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Получение значения из конфигурации"""
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
    
    def getint(self, section: str, key: str, default: int = 0) -> int:
        """Получение целочисленного значения из конфигурации"""
        try:
            return self.config.getint(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def getboolean(self, section: str, key: str, default: bool = False) -> bool:
        """Получение булевого значения из конфигурации"""
        try:
            return self.config.getboolean(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            return default
    
    def set(self, section: str, key: str, value: Any):
        """Установка значения в конфигурации"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        
        self.config.set(section, key, str(value))
        self.save_config()
    
    def get_editor_font_family(self) -> str:
        """Получение семейства шрифта редактора"""
        return self.get('Editor', 'font_family', 'Consolas')
    
    def get_editor_font_size(self) -> int:
        """Получение размера шрифта редактора"""
        return self.getint('Editor', 'font_size', 12)
    
    def get_editor_tab_size(self) -> int:
        """Получение размера табуляции"""
        return self.getint('Editor', 'tab_size', 4)
    
    def is_line_numbers_enabled(self) -> bool:
        """Проверка включения номеров строк"""
        return self.getboolean('Editor', 'line_numbers', True)
    
    def is_word_wrap_enabled(self) -> bool:
        """Проверка включения переноса слов"""
        return self.getboolean('Editor', 'word_wrap', False)
    
    def is_auto_indent_enabled(self) -> bool:
        """Проверка включения автоотступов"""
        return self.getboolean('Editor', 'auto_indent', True)
    
    def get_theme(self) -> str:
        """Получение текущей темы"""
        return self.get('General', 'theme', 'dark')
    
    def get_language(self) -> str:
        """Получение языка интерфейса"""
        return self.get('General', 'language', 'ru')
    
    def is_auto_save_enabled(self) -> bool:
        """Проверка включения автосохранения"""
        return self.getboolean('General', 'auto_save', True)
    
    def get_auto_save_interval(self) -> int:
        """Получение интервала автосохранения в секундах"""
        return self.getint('General', 'auto_save_interval', 300)
    
    def get_default_encoding(self) -> str:
        """Получение кодировки по умолчанию"""
        return self.get('Files', 'default_encoding', 'utf-8')
    
    def get_window_size(self) -> tuple:
        """Получение размера окна"""
        width = self.getint('Interface', 'window_width', 1200)
        height = self.getint('Interface', 'window_height', 800)
        return (width, height)
    
    def set_window_size(self, width: int, height: int):
        """Установка размера окна"""
        self.set('Interface', 'window_width', width)
        self.set('Interface', 'window_height', height)
    
    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """Получение всех настроек"""
        settings = {}
        for section in self.config.sections():
            settings[section] = dict(self.config[section])
        return settings 
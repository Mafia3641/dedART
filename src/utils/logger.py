"""
Настройка логирования
"""

import logging
import colorlog
from pathlib import Path
from datetime import datetime


def setup_logging():
    """Настройка системы логирования"""
    # Создание директории для логов
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Настройка форматирования
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Очистка существующих обработчиков
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Файловый обработчик
    log_file = log_dir / f"dedart_editor_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Логирование запуска
    logger = logging.getLogger(__name__)
    logger.info("Система логирования инициализирована")
    logger.info(f"Логи сохраняются в: {log_dir}") 
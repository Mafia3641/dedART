#!/usr/bin/env python3
"""
Основной файл проекта dedART - Редактор на PyQt6
"""

import sys
import logging

from PyQt6.QtWidgets import QApplication

from src.app import EditorApp
from src.utils.logger import setup_logging


def main():
    """Главная функция приложения"""
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Запуск приложения dedART Editor")
    
    # Создание QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("dedART Editor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("dedART")
    
    # Настройка стилей
    app.setStyle('Fusion')
    
    # Создание и запуск главного окна
    editor = EditorApp()
    editor.show()
    
    logger.info("Приложение запущено успешно")
    
    # Запуск главного цикла приложения
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 
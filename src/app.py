"""
Главное приложение редактора
"""

import logging
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QSettings, QEvent
# from PyQt6.QtGui import QFont  # Не используется

from .ui.menu_bar import MenuBar
from .ui.status_bar import StatusBar
from .ui.custom_tab_widget import CustomTabWidget
# from .utils.config import Config  # Временно отключен


class EditorApp(QMainWindow):
    """Главное окно приложения редактора"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
# Конфигурация временно отключена - не используется
        self.current_file: Optional[Path] = None
        
        self.init_ui()
        self.setup_connections()
        self.load_settings()
        
        # Гарантируем полноэкранный режим после инициализации
        self.showMaximized()
        
        self.logger.info("Главное окно приложения инициализировано")
    
    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("dedART Editor")
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Создание компонентов UI
        self.menu_bar = MenuBar(self)
        self.status_bar = StatusBar(self)
        self.tab_widget = CustomTabWidget(self)
        
        # Добавление компонентов в layout
        main_layout.addWidget(self.tab_widget)
        
        # Установка меню и статусной панели
        self.setMenuBar(self.menu_bar)
        self.setStatusBar(self.status_bar)
    
    def setup_connections(self):
        """Настройка сигналов и слотов"""
        # Подключение сигналов меню
        self.menu_bar.file_new.triggered.connect(self.new_file)
        self.menu_bar.file_open.triggered.connect(self.open_file)
        self.menu_bar.file_save.triggered.connect(self.save_file)
        self.menu_bar.file_save_as.triggered.connect(self.save_file_as)
        self.menu_bar.file_exit.triggered.connect(self.close)
        
        # Подключение сигналов редактора через tab_widget
        self.tab_widget.text_changed.connect(self.on_text_changed)
        self.tab_widget.cursor_position_changed.connect(self.on_cursor_changed)
    
    def new_file(self):
        """Создание нового файла"""
        if self.check_save_changes():
            self.tab_widget.new_file()
            self.current_file = None
            self.update_title()
            self.status_bar.set_message("Новый файл создан")
            self.logger.info("Создан новый файл")
    
    def open_file(self):
        """Открытие файла"""
        if self.check_save_changes():
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Открыть файл",
                str(Path.home()),
                "Все файлы (*);;Текстовые файлы (*.txt);;Python файлы (*.py)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        self.tab_widget.set_content(content)
                    
                    self.current_file = Path(file_path)
                    self.update_title()
                    self.status_bar.set_message(f"Файл открыт: {self.current_file.name}")
                    self.logger.info(f"Открыт файл: {file_path}")
                    
                except Exception as e:
                    QMessageBox.critical(self, "Ошибка", f"Не удалось открыть файл: {e}")
                    self.logger.error(f"Ошибка при открытии файла: {e}")
    
    def save_file(self):
        """Сохранение файла"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Сохранение файла как"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл",
            str(Path.home()),
            "Все файлы (*);;Текстовые файлы (*.txt);;Python файлы (*.py)"
        )
        
        if file_path:
            self._save_to_file(Path(file_path))
    
    def _save_to_file(self, file_path: Path):
        """Сохранение содержимого в файл"""
        try:
            content = self.tab_widget.get_content()
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            
            self.current_file = file_path
            self.update_title()
            self.status_bar.set_message(f"Файл сохранен: {file_path.name}")
            self.logger.info(f"Файл сохранен: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")
            self.logger.error(f"Ошибка при сохранении файла: {e}")
    
    def check_save_changes(self) -> bool:
        """Проверка необходимости сохранения изменений"""
        if self.tab_widget.is_modified():
            reply = QMessageBox.question(
                self,
                "Сохранение",
                "Документ был изменен. Сохранить изменения?",
                QMessageBox.StandardButton.Save | 
                QMessageBox.StandardButton.Discard | 
                QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Save:
                return self.save_file()
            elif reply == QMessageBox.StandardButton.Cancel:
                return False
        
        return True
    
    def update_title(self):
        """Обновление заголовка окна"""
        if self.current_file:
            title = f"{self.current_file.name} - dedART Editor"
        else:
            title = "dedART Editor"
        
        if self.tab_widget.is_modified():
            title = f"*{title}"
        
        self.setWindowTitle(title)
    
    def on_text_changed(self):
        """Обработчик изменения текста"""
        self.update_title()
        self.status_bar.update_line_count(self.tab_widget.get_line_count())
    
    def on_cursor_changed(self, line: int, column: int):
        """Обработчик изменения позиции курсора"""
        self.status_bar.update_cursor_position(line, column)
    
    def load_settings(self):
        """Загрузка настроек приложения"""
        settings = QSettings()
        
        # Принудительно запускаем в полноэкранном режиме
        self.showMaximized()
        
        # Загрузка настроек редактора
        font_family = settings.value("editor/font_family", "Consolas")
        font_size = settings.value("editor/font_size", 12)
        self.tab_widget.set_font(font_family, font_size)
    
    def save_settings(self):
        """Сохранение настроек приложения"""
        settings = QSettings()
        
        # Сохраняем только настройки редактора, не геометрию окна
        # чтобы приложение всегда запускалось в полноэкранном режиме
        font_family, font_size = self.tab_widget.get_font()
        settings.setValue("editor/font_family", font_family)
        settings.setValue("editor/font_size", font_size)
    
    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.check_save_changes():
            self.save_settings()
            
            # Очищаем ресурсы чата
            if hasattr(self.tab_widget, 'cleanup'):
                self.tab_widget.cleanup()
            
            self.logger.info("Приложение закрыто")
            event.accept()
        else:
            event.ignore()
    
    def changeEvent(self, event):
        """Обработчик изменения состояния окна"""
        if event.type() == QEvent.Type.WindowStateChange:
            # Если окно было развернуто не в полноэкранный режим, возвращаем его
            if not self.isMaximized():
                self.showMaximized()
        super().changeEvent(event) 
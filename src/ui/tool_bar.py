"""
Панель инструментов
"""

from PyQt6.QtWidgets import QToolBar
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt


class ToolBar(QToolBar):
    """Панель инструментов приложения"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Панель инструментов")
        self.setMovable(True)
        self.init_actions()
    
    def init_actions(self):
        """Инициализация действий панели инструментов"""
        # Действие "Новый файл"
        self.new_action = QAction("Новый", self)
        self.new_action.setStatusTip("Создать новый файл")
        self.new_action.setToolTip("Новый файл")
        self.addAction(self.new_action)
        
        # Действие "Открыть файл"
        self.open_action = QAction("Открыть", self)
        self.open_action.setStatusTip("Открыть файл")
        self.open_action.setToolTip("Открыть файл")
        self.addAction(self.open_action)
        
        # Действие "Сохранить"
        self.save_action = QAction("Сохранить", self)
        self.save_action.setStatusTip("Сохранить файл")
        self.save_action.setToolTip("Сохранить файл")
        self.addAction(self.save_action)
        
        self.addSeparator()
        
        # Действие "Отменить"
        self.undo_action = QAction("Отменить", self)
        self.undo_action.setStatusTip("Отменить последнее действие")
        self.undo_action.setToolTip("Отменить")
        self.addAction(self.undo_action)
        
        # Действие "Повторить"
        self.redo_action = QAction("Повторить", self)
        self.redo_action.setStatusTip("Повторить отмененное действие")
        self.redo_action.setToolTip("Повторить")
        self.addAction(self.redo_action)
        
        self.addSeparator()
        
        # Действие "Вырезать"
        self.cut_action = QAction("Вырезать", self)
        self.cut_action.setStatusTip("Вырезать выделенный текст")
        self.cut_action.setToolTip("Вырезать")
        self.addAction(self.cut_action)
        
        # Действие "Копировать"
        self.copy_action = QAction("Копировать", self)
        self.copy_action.setStatusTip("Копировать выделенный текст")
        self.copy_action.setToolTip("Копировать")
        self.addAction(self.copy_action)
        
        # Действие "Вставить"
        self.paste_action = QAction("Вставить", self)
        self.paste_action.setStatusTip("Вставить текст из буфера обмена")
        self.paste_action.setToolTip("Вставить")
        self.addAction(self.paste_action) 
"""
Меню приложения
"""

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QKeySequence


class MenuBar(QMenuBar):
    """Меню приложения"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_menus()
    
    def init_menus(self):
        """Инициализация меню"""
        # Меню Файл
        self.file_menu = QMenu("&Файл", self)
        self.addMenu(self.file_menu)
        
        # Действия меню Файл
        self.file_new = QAction("&Новый", self)
        self.file_new.setShortcut(QKeySequence.StandardKey.New)
        self.file_new.setStatusTip("Создать новый файл")
        self.file_menu.addAction(self.file_new)
        
        self.file_open = QAction("&Открыть...", self)
        self.file_open.setShortcut(QKeySequence.StandardKey.Open)
        self.file_open.setStatusTip("Открыть файл")
        self.file_menu.addAction(self.file_open)
        
        self.file_menu.addSeparator()
        
        self.file_save = QAction("&Сохранить", self)
        self.file_save.setShortcut(QKeySequence.StandardKey.Save)
        self.file_save.setStatusTip("Сохранить файл")
        self.file_menu.addAction(self.file_save)
        
        self.file_save_as = QAction("Сохранить &как...", self)
        self.file_save_as.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.file_save_as.setStatusTip("Сохранить файл как")
        self.file_menu.addAction(self.file_save_as)
        
        self.file_menu.addSeparator()
        
        self.file_exit = QAction("&Выход", self)
        self.file_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self.file_exit.setStatusTip("Выйти из приложения")
        self.file_menu.addAction(self.file_exit)
        
        # Удалены неиспользуемые меню: Правка, Вид, Справка
        # Они не подключены к обработчикам в приложении 
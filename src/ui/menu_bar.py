"""
Меню приложения
"""

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QKeySequence


class MenuBar(QMenuBar):
    """Меню приложения"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
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
        
        # Меню Правка
        self.edit_menu = QMenu("&Правка", self)
        self.addMenu(self.edit_menu)
        
        # Действия меню Правка
        self.edit_undo = QAction("&Отменить", self)
        self.edit_undo.setShortcut(QKeySequence.StandardKey.Undo)
        self.edit_undo.setStatusTip("Отменить последнее действие")
        self.edit_menu.addAction(self.edit_undo)
        
        self.edit_redo = QAction("&Повторить", self)
        self.edit_redo.setShortcut(QKeySequence.StandardKey.Redo)
        self.edit_redo.setStatusTip("Повторить отмененное действие")
        self.edit_menu.addAction(self.edit_redo)
        
        self.edit_menu.addSeparator()
        
        self.edit_cut = QAction("&Вырезать", self)
        self.edit_cut.setShortcut(QKeySequence.StandardKey.Cut)
        self.edit_cut.setStatusTip("Вырезать выделенный текст")
        self.edit_menu.addAction(self.edit_cut)
        
        self.edit_copy = QAction("&Копировать", self)
        self.edit_copy.setShortcut(QKeySequence.StandardKey.Copy)
        self.edit_copy.setStatusTip("Копировать выделенный текст")
        self.edit_menu.addAction(self.edit_copy)
        
        self.edit_paste = QAction("&Вставить", self)
        self.edit_paste.setShortcut(QKeySequence.StandardKey.Paste)
        self.edit_paste.setStatusTip("Вставить текст из буфера обмена")
        self.edit_menu.addAction(self.edit_paste)
        
        # Меню Вид
        self.view_menu = QMenu("&Вид", self)
        self.addMenu(self.view_menu)
        
        # Действия меню Вид
        self.view_zoom_in = QAction("&Увеличить", self)
        self.view_zoom_in.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.view_zoom_in.setStatusTip("Увеличить масштаб")
        self.view_menu.addAction(self.view_zoom_in)
        
        self.view_zoom_out = QAction("&Уменьшить", self)
        self.view_zoom_out.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.view_zoom_out.setStatusTip("Уменьшить масштаб")
        self.view_menu.addAction(self.view_zoom_out)
        
        self.view_menu.addSeparator()
        
        self.view_line_numbers = QAction("&Номера строк", self)
        self.view_line_numbers.setCheckable(True)
        self.view_line_numbers.setChecked(True)
        self.view_line_numbers.setStatusTip("Показать/скрыть номера строк")
        self.view_menu.addAction(self.view_line_numbers)
        
        # Меню Справка
        self.help_menu = QMenu("&Справка", self)
        self.addMenu(self.help_menu)
        
        # Действия меню Справка
        self.help_about = QAction("&О программе", self)
        self.help_about.setStatusTip("Информация о программе")
        self.help_menu.addAction(self.help_about) 
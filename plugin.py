import os
from qgis.PyQt.QtWidgets import QAction, QMenu
from qgis.PyQt.QtGui import QIcon
from .dialog import DEMDialog

class DEMResamplePlugin:

    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.menu_name = "Ineffable Tools"

    def initGui(self):
        # 1. Setup icon and action
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.action = QAction(
            QIcon(icon_path), 
            "DEM Resample Interpolator", 
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)

        # 2. Add to "Ineffable Tools" menu
        main_menu = self.iface.mainWindow().menuBar()
        found_menu = None
        
        # Find existing "Ineffable Tools" menu
        for action in main_menu.actions():
            if action.text() == self.menu_name:
                found_menu = action.menu()
                break
        
        # Create it if it doesn't exist
        if not found_menu:
            found_menu = QMenu(self.menu_name, self.iface.mainWindow())
            main_menu.addMenu(found_menu)
            
        found_menu.addAction(self.action)

    def unload(self):
        # Remove action from menu
        main_menu = self.iface.mainWindow().menuBar()
        for action in main_menu.actions():
            if action.text() == self.menu_name:
                menu = action.menu()
                if menu:
                    menu.removeAction(self.action)
                break

    def run(self):
        dlg = DEMDialog(self.iface)
        dlg.exec_()


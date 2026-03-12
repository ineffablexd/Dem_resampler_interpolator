import os
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from .dialog import DEMDialog

class DEMResamplePlugin:

    def __init__(self, iface):
        self.iface = iface
        self.action = None

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        self.action = QAction(
            QIcon(icon_path),
            "DEM Resample Interpolator",
            self.iface.mainWindow()
        )
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("Ineffable Tools", self.action)

    def unload(self):
        self.iface.removePluginMenu("Ineffable Tools", self.action)

    def run(self):
        dlg = DEMDialog(self.iface)
        dlg.exec_()

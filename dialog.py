from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QDoubleSpinBox, QProgressBar, QFrame
)
from qgis.PyQt.QtCore import Qt, QCoreApplication
from qgis.core import QgsProject, QgsProcessingFeedback
import processing


class DEMDialog(QDialog):

    def __init__(self, iface):
        super().__init__()

        self.iface = iface
        self.setWindowTitle("DEM Resample Interpolator")

        layout = QVBoxLayout()

        # DEM selection
        layout.addWidget(QLabel("Select DEM Layer"))

        self.dem_combo = QComboBox()
        self.layers = []

        for layer in QgsProject.instance().mapLayers().values():
            if layer.type() == layer.RasterLayer:
                self.layers.append(layer)
                self.dem_combo.addItem(layer.name())

        layout.addWidget(self.dem_combo)

        # Interpolation method
        layout.addWidget(QLabel("Interpolation Method"))

        self.method = QComboBox()
        self.method.addItems(["Bilinear", "Bicubic", "Lanczos", "Nearest Neighbor"])

        layout.addWidget(self.method)

        # Output resolution
        layout.addWidget(QLabel("Output Resolution (meters, supports 0.1m)"))

        self.resolution = QDoubleSpinBox()
        self.resolution.setDecimals(2)
        self.resolution.setMinimum(0.1)
        self.resolution.setValue(0.2)  # Default to 0.2m as user requested before

        layout.addWidget(self.resolution)

        # Method Description (Logic Info)
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_layout = QVBoxLayout(info_frame)
        
        layout.addWidget(QLabel("Method Info & Logic:"))
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setMinimumHeight(60)
        self.info_label.setStyleSheet("color: #444; font-style: italic; background-color: #f0f0f0; padding: 10px; border: 1px solid #ddd; border-radius: 4px;")
        info_layout.addWidget(self.info_label)
        layout.addWidget(info_frame)

        # Run button
        self.run_btn = QPushButton("Generate Enhanced DEM")
        self.run_btn.setStyleSheet("font-weight: bold; height: 35px;")
        self.run_btn.clicked.connect(self.run_process)
        layout.addWidget(self.run_btn)

        # Progress Bar (at the very bottom, thinner)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumHeight(10)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #ddd; border-radius: 5px; background-color: #eee; } QProgressBar::chunk { background-color: #3498db; }")
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        # Descriptions mapping
        self.descriptions = {
            "Bilinear": "Linear interpolation in 2D. Uses 4 pixels. Good for continuous data like DEMs, providing smooth gradients.",
            "Bicubic": "Higher-order interpolation using 16 pixels. Produces smoother results than Bilinear, ideal for high-quality DEM upsampling.",
            "Lanczos": "Sinc-based interpolation using 36 pixels. Provides the sharpest results and best quality for significant resolution increases.",
            "Nearest Neighbor": "Fastest. Pixel value is taken from the closest source pixel. Use this only if you must preserve original exact values (e.g., categories)."
        }
        self.method.currentTextChanged.connect(self.update_info)
        self.update_info(self.method.currentText())

    def update_info(self, text):
        self.info_label.setText(self.descriptions.get(text, ""))

    # ------------------------------------------------
    # DEM RESAMPLING FUNCTION
    # ------------------------------------------------
    def run_process(self):
        if self.dem_combo.currentIndex() < 0:
            from qgis.PyQt.QtWidgets import QMessageBox
            QMessageBox.warning(self, "No Layer", "Please select a raster layer first.")
            return

        raster = self.layers[self.dem_combo.currentIndex()]
        res = self.resolution.value()

        method = self.method.currentText()

        resample_map = {
            "Bilinear": 1,
            "Bicubic": 2,
            "Lanczos": 4,
            "Nearest Neighbor": 0
        }

        resample = resample_map[method]

        # Reset Progress
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.run_btn.setEnabled(False)
        QCoreApplication.processEvents()

        feedback = QgsProcessingFeedback()
        feedback.progressChanged.connect(lambda p: self.progress_bar.setValue(int(round(p))))

        params = {
            'INPUT': raster.source(),
            'SOURCE_CRS': raster.crs().authid(),
            'TARGET_CRS': raster.crs().authid(),
            'RESAMPLING': resample,
            'TARGET_RESOLUTION': res,
            'OUTPUT': 'TEMPORARY_OUTPUT'
        }

        try:
            result = processing.run("gdal:warpreproject", params, feedback=feedback)
            self.iface.addRasterLayer(result['OUTPUT'], f"Resampled_{method}_{res}m")
            self.progress_bar.setValue(100)
            from qgis.PyQt.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", f"DEM successfully resampled to {res}m using {method} interpolation.")
        except Exception as e:
            from qgis.PyQt.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Processing Error", f"Resampling failed: {str(e)}")
        finally:
            self.run_btn.setEnabled(True)
            self.progress_bar.setVisible(False)  # Hide it when done
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
        self.setMinimumWidth(380)

        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

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
        self.resolution.setValue(1.0) 

        layout.addWidget(self.resolution)

        # Method Description (Logic Info)
        layout.addWidget(QLabel("Method Info & Logic:"))
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setFixedHeight(90)
        self.info_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.info_label.setStyleSheet(
            "color: #444; font-style: italic; background-color: #f0f0f0;"
            "padding: 10px; border: 1px solid #ddd; border-radius: 4px;"
        )
        layout.addWidget(self.info_label)

        # Progress indicator (above the run button, hidden by default)
        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #2980b9; font-size: 11px;")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(18)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #aaa; border-radius: 5px; background-color: #eee; text-align: center; font-weight: bold; }"
            "QProgressBar::chunk { background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980b9, stop:1 #27ae60); border-radius: 4px; }"
        )
        layout.addWidget(self.progress_bar)

        # Run button
        self.run_btn = QPushButton("Generate Enhanced DEM")
        self.run_btn.setStyleSheet("font-weight: bold; height: 35px;")
        self.run_btn.clicked.connect(self.run_process)
        layout.addWidget(self.run_btn)

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
        self.progress_label.setText("⏳ Processing, please wait...")
        self.progress_label.setVisible(True)
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
            self.progress_label.setText("✅ Done!")
            from qgis.PyQt.QtWidgets import QMessageBox
            QMessageBox.information(self, "Success", f"DEM resampled to {res}m using {method}.")
        except Exception as e:
            from qgis.PyQt.QtWidgets import QMessageBox
            self.progress_label.setText("❌ Failed.")
            QMessageBox.critical(self, "Processing Error", f"Resampling failed: {str(e)}")
        finally:
            self.run_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.progress_label.setVisible(False)
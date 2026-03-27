# 📋 DEM Resample Interpolator 🏔️

[![QGIS Version](https://img.shields.io/badge/QGIS-3.0+-green.svg)](https://qgis.org)
[![Version](https://img.shields.io/badge/Version-1.0-blue.svg)](https://github.com/ineffablexd/Dem_resampler_interpolator)
[![License](https://img.shields.io/badge/License-GPL--2.0--or--later-orange.svg)](LICENSE)

**DEM Resample Interpolator** is a terrain analysis tool designed for high-resolution Digital Elevation Model (DEM) processing. Part of the **Ineffable Tools** suite, it provides a streamlined interface for upsampling or downsampling rasters using interpolation algorithms to ensure data integrity and visual smoothness.

---

## 🖼️ Visual Workflow

<p align="center">
  <img src="assets/ui_main.png" alt="DEM Resample Interpolator Main UI" width="600">
  <br>
  <em>Main interface showcasing the clean layout and method information panel.</em>
</p>

<p align="center">
  <img src="assets/ui_dropdown.png" alt="Interpolation Methods" width="600">
  <br>
  <em>Support for multiple interpolation methods with live descriptions.</em>
</p>

---

## ⚡ Key Features

- **🏔️ Precision Resampling**: Effortlessly upsample or downsample DEMs to any target resolution (supports up to 0.1m).
- **🛠️ Sophisticated Algorithms**: Choose from Bilinear, Bicubic, Lanczos, and Nearest Neighbor methods.
- **📖 Integrated Logic Panel**: Real-time descriptions for each method so you always know which algorithm fits your data.
- **📊 Live Progress Tracking**: Integrated progress bar and status updates for long-running processes.
- **🏗️ GDAL-Powered**: Built on top of robust GDAL processing for reliable results.

---

## 🧠 Understanding Interpolation Methods

Choosing the right interpolation method is critical for accurate terrain analysis. The plugin supports:

1.  **Nearest Neighbor (Box Filter)**:
    - **Logic**: Assigns the value of the single closest pixel from the source grid to the target pixel without any averaging.
    - **Calculation**: If the projected coordinate is $(x', y')$, the value $V$ is chosen as $V(round(x'), round(y'))$.
    - **Example**: For a target pixel mapped to source coordinate $(2.1, 3.8)$, the value of the pixel at $(2, 4)$ is used.
    - **Best Use**: Ideal for discrete data (categorical) where averaging values (like 10 and 20 resulting in 15) would create non-existent classes. It is the fastest but produces "jagged" or "staircase" artifacts on continuous terrain.

2.  **Bilinear Interpolation**:
    - **Logic**: Performs linear interpolation first in one direction, then in the other. It uses a 2x2 neighborhood (4 pixels).
    - **Calculation**:
      $$V = (1-dx)(1-dy)V_{0,0} + dx(1-dy)V_{1,0} + (1-dx)dyV_{0,1} + dxdyV_{1,1}$$
      _Where $dx, dy$ are the fractional distances to the neighboring pixels._
    - **Example**: If a target pixel is at source coordinate $(1.2, 2.3)$, $dx = 0.2$ and $dy = 0.3$. The weights for the four pixels would be: top-left (0.56), top-right (0.14), bottom-left (0.24), and bottom-right (0.06).
    - **Best Use**: Standard for DEMs when you need a balance between speed and smoothness. It eliminates the "jaggedness" of Nearest Neighbor but can slightly blur sharp ridges.

3.  **Bicubic Interpolation**:
    - **Logic**: Uses a cubic convolution kernel over a 4x4 grid (16 pixels). It considers the slope (derivative) of the data.
    - **Calculation**: Uses a cubic spline $W(x)$ to weight 16 pixels. The formula is $V = \sum_{i=-1}^{2} \sum_{j=-1}^{2} V_{i,j} \cdot W(dx-i) \cdot W(dy-j)$.
    - **Example**: For the same $(1.2, 2.3)$, Bicubic looks 2 pixels out in every direction, creating a smoother curve that preserves the "flow" of the terrain better than flat linear segments.
    - **Best Use**: Specifically suited for high-quality DEM upsampling where visual aesthetic and curvature preservation are critical.

4.  **Lanczos (Sinc-based)**:
    - **Logic**: Uses a Sinc-based windowed filter (typically $a=3$, using a 6x6 grid or 36 pixels). It is mathematically designed to preserve frequencies.
    - **Calculation**:
      $$L(x) = \text{sinc}(x) \cdot \text{sinc}(x/a) \text{ for } |x| < a$$
      _The weights are calculated using this oscillating kernel which acts as a "low-pass" filter._
    - **Example**: When significantly increasing resolution (e.g., from 30m to 1m), Lanczos minimizes aliasing (staircasing) and maintains sharpness better than any other method by weighting 36 pixels according to the Sinc distribution.
    - **Best Use**: The highest quality option for significant resolution increases and professional terrain visualization. Note: Can occasionally cause "ringing" artifacts in areas of extreme elevation contrast.

---

## 📥 Installation

### Method 1: QGIS Plugin Manager

1.  Download the repository as a ZIP file.
2.  In QGIS, go to **Plugins** -> **Manage and Install Plugins**.
3.  Select **Install from ZIP** and navigate to the downloaded file.

### Method 2: Manual Installation

1.  Navigate to your QGIS plugins folder:
    - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
    - **Windows**: `%AppData%\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
2.  Clone this repository or extract the ZIP into a folder named `Dem_resampler_interpolator`.
3.  Restart QGIS.

---

## 🚀 How to Use

1.  **Open the Plugin**: Locate the **Ineffable Tools** menu in your toolbar or the Plugins menu.
2.  **Select Layer**: Choose the DEM (Raster) layer you want to resample from the dropdown.
3.  **Choose Method**: Select the interpolation method that best fits your needs (check the info panel for details).
4.  **Set Resolution**: Specify the target output resolution in meters (e.g., change 1.0m to 0.1m).
5.  **Run**: Click `Generate Enhanced DEM`. The processed layer will be added to your canvas automatically.

---

## 👨‍💻 Author & License

- **Author**: Vicky Sharma
- **Email**: vsharma@powergrid.in
- **License**: GPL-2.0-or-later

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/ineffablexd">Ineffable</a>
</p>

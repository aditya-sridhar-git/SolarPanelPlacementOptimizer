# 🌞 Solar Building Analyzer

AI-powered satellite image analysis tool for detecting buildings and evaluating solar panel placement potential.

## 🎯 Features

- **Building Detection**: Automatic detection of buildings from satellite imagery using multi-scale analysis
- **Roof Analysis**: Classification of roof types, orientation, and slope estimation
- **Solar Suitability**: Comprehensive solar panel placement evaluation with suitability ratings
- **Shading Analysis**: Assessment of shading impact on solar panel efficiency
- **Energy Estimation**: Annual energy production calculations and CO₂ offset estimates
- **Panel Layout Optimization**: Optimal solar panel placement with capacity calculations
- **Multiple Export Formats**: JSON reports, GeoJSON data, and annotated visualizations

## 📋 Requirements

- Python 3.7+
- OpenCV
- NumPy
- Matplotlib
- scikit-learn
- scikit-image
- SciPy
- Pillow
- Shapely

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/aditya-sridhar-git/Environment-AI-RooftopAnalyzer.git
cd Environment-AI-RooftopAnalyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Basic Usage

Run the interactive analyzer:
```bash
python main.py
```

The program will:
1. Check for satellite images in the current directory or `testcases/` folder
2. Offer to create a sample image if none is found
3. Prompt for location configuration (default: Delhi, India)
4. Analyze buildings and generate comprehensive solar suitability reports

### Custom Location

When prompted, you can specify custom coordinates:
```
Use custom location? (y/n, default: Delhi): y
Enter latitude (e.g., 28.6139): 40.7128
Enter longitude (e.g., 77.2090): -74.0060
Enter meters per pixel (default 0.15): 0.15
```

### Supported Image Formats

- `.jpg` / `.jpeg`
- `.png`

Place your satellite images in the root directory or `testcases/` folder.

## 📊 Output

The analysis generates several outputs in the `output/` folder:

### 1. Annotated Image (`buildings_annotated.jpg`)
Color-coded visualization of detected buildings:
- 🟢 **Green**: Excellent solar potential
- 🟡 **Yellow**: Good solar potential
- 🟠 **Orange**: Fair solar potential
- 🔴 **Red**: Poor solar potential

### 2. Solar Report (`solar_report.json`)
Detailed analysis including:
- Building metrics (roof area, orientation, slope)
- Panel layout specifications (count, capacity)
- Energy production estimates
- Suitability ratings
- Location data and timestamp

### 3. GeoJSON Export (`buildings.geojson`)
GIS-compatible format for integration with mapping tools

## 📈 Analysis Metrics

For each building, the analyzer provides:

- **Roof Area**: Total and usable roof area in m²
- **Roof Type**: Classification (flat, gabled, hipped, complex)
- **Orientation**: Compass direction the roof faces
- **Slope**: Estimated roof angle in degrees
- **Shading Score**: Impact of shadows (0-1 scale)
- **Panel Count**: Number of panels that can be installed
- **Total Capacity**: System capacity in kW
- **Annual Energy**: Estimated production in kWh/year
- **Monthly Average**: Average monthly energy output
- **CO₂ Offset**: Annual carbon dioxide reduction in kg

## 🔧 Configuration

Default solar panel specifications:
- Panel size: 1.0m × 1.7m
- Panel efficiency: 20%
- System losses: 14%
- Minimum roof area: 20m²

You can modify these in the code by adjusting the optimizer configuration in `main.py`.

## 📁 Project Structure

```
Environment-AI-RooftopAnalyzer/
├── main.py                      # Main entry point
├── EnhancedBuildingDetector.py  # Building detection module
├── SolarPanelOptimizer.py       # Solar analysis module
├── requirements.txt             # Python dependencies
├── testcases/                   # Sample satellite images
├── output/                      # Generated results
└── README.md                    # This file
```

## 🛠️ Troubleshooting

### No buildings detected
- Try using a different satellite image with clearer building outlines
- Adjust `min_area` and `max_area` parameters in the detector config

### Low solar ratings
- Ensure the image has good lighting and minimal cloud cover
- Check that buildings have visible rooftops

### Import errors
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure Python version is 3.7 or higher

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- Building detection algorithms based on computer vision techniques
- Solar calculations use location-based solar irradiance models
- GeoJSON export enables integration with GIS platforms

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ☀️ for a sustainable future**


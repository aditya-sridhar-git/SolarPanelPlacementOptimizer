# 🌞 Solar Building Analyzer

AI-powered satellite image analysis tool for detecting buildings and evaluating solar panel placement potential. Automatically analyzes rooftop characteristics, calculates optimal solar panel layouts, and estimates energy production.

## 🎯 Features

- **Intelligent Building Detection**: Multi-scale detection algorithm that automatically adjusts for different image sizes
- **Roof Analysis**: Classification of roof types, orientation, and slope estimation
- **Solar Suitability**: Comprehensive solar panel placement evaluation with color-coded ratings
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
2. Automatically adjust detection parameters based on image size
3. Offer to create a sample image if none is found
4. Prompt for location configuration (default: Delhi, India)
5. Analyze buildings and generate comprehensive solar suitability reports

### Custom Location

When prompted, you can specify custom coordinates:
```
Use custom location? (y/n, default: Delhi): y
Enter latitude (e.g., 28.6139): 40.7128
Enter longitude (e.g., 77.2090): -74.0060
Enter meters per pixel (default 0.15): 0.15
```

### Image Requirements

- **Supported formats**: `.jpg`, `.jpeg`, `.png`
- **Recommended size**: At least 500x500 pixels for accurate detection
- **Small images**: The tool automatically adjusts detection parameters for images smaller than 10,000 pixels

Place your satellite images in:
- Root directory (highest priority)
- `testcases/` folder (checked if no images in root)

### Creating Test Images

Run the sample generator to create a test image:
```bash
python create_sample.py
```

This creates a 1600x1200 pixel sample with 10 buildings for testing.

## 📊 Output

The analysis generates several outputs in the `output/` folder:

### 1. Annotated Image (`buildings_annotated.jpg`)
Color-coded visualization of detected buildings:
- 🟢 **Green**: Excellent solar potential (>80% suitability)
- 🟡 **Yellow**: Good solar potential (60-80%)
- 🟠 **Orange**: Fair solar potential (40-60%)
- 🔴 **Red**: Poor solar potential (<40%)

### 2. Solar Report (`solar_report.json`)
Detailed analysis including:
- Building metrics (roof area, orientation, slope)
- Panel layout specifications (count, capacity, positions)
- Energy production estimates
- Suitability ratings and scores
- Location data and timestamp

### 3. GeoJSON Export (`buildings.geojson`)
GIS-compatible format for integration with mapping tools like QGIS, ArcGIS, or web mapping libraries.

## 📈 Analysis Metrics

For each building, the analyzer provides:

- **Roof Area**: Total and usable roof area in m²
- **Roof Type**: Classification (flat, gabled, hipped, complex)
- **Orientation**: Compass direction the roof faces (0-360°)
- **Slope**: Estimated roof angle in degrees
- **Shading Score**: Impact of shadows (0-1 scale, higher is better)
- **Panel Count**: Number of solar panels that can be installed
- **Total Capacity**: System capacity in kW
- **Annual Energy**: Estimated production in kWh/year
- **Monthly Average**: Average monthly energy output in kWh
- **CO₂ Offset**: Annual carbon dioxide reduction in kg

## 🔧 Configuration

Default solar panel specifications:
- Panel size: 1.0m × 1.7m (standard residential panel)
- Panel efficiency: 20%
- System losses: 14%
- Minimum roof area: 20m²
- Detection thresholds: Auto-adjusted based on image size

Modify these in `main.py` by adjusting the optimizer configuration.

## 📁 Project Structure

```
Environment-AI-RooftopAnalyzer/
├── main.py                      # Main entry point with interactive CLI
├── EnhancedBuildingDetector.py  # Building detection and segmentation
├── SolarPanelOptimizer.py       # Solar analysis and optimization
├── requirements.txt             # Python dependencies
├── testcases/                   # Sample satellite images
├── output/                      # Generated results (git-ignored)
├── create_sample.py             # Sample image generator (optional)
└── README.md                    # This file
```

## 🛠️ Troubleshooting

### No buildings detected
- **Image too small**: Use images at least 500x500 pixels
- **Low contrast**: Ensure buildings have clear edges and good lighting
- **Adjust parameters**: The tool auto-adjusts, but you can manually modify `min_area` in code

### Low solar ratings
- Ensure the image has good lighting and minimal cloud cover
- Check that buildings have visible, unobstructed rooftops
- Trees or shadows near buildings will reduce suitability scores

### Import/Module errors
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Ensure Python version is 3.7 or higher: `python --version`
- Check that module files use correct capitalization (Windows is case-insensitive but Linux/Mac are not)

### JSON serialization errors
- This has been fixed in the current version with automatic numpy array conversion
- If you encounter this, ensure you're using the latest code from the `working-fixes` branch

## 🆕 Recent Updates

- ✅ Fixed module import naming issues
- ✅ Added automatic image size detection and parameter adjustment
- ✅ Fixed JSON serialization for numpy arrays
- ✅ Added testcases folder scanning for images
- ✅ Improved error handling for empty analysis results
- ✅ Added comprehensive README and .gitignore

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

- Building detection algorithms based on computer vision and edge detection techniques
- Solar calculations use location-based solar irradiance models
- GeoJSON export enables integration with popular GIS platforms
- Multi-scale detection approach for robust building identification

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ☀️ for a sustainable future**


# ☀️ Solar Panel Placement Optimizer

An AI-powered tool that analyzes satellite/rooftop images to determine optimal solar panel placement, calculate energy production, and visualize environmental impact.

<img width="1895" height="940" alt="image" src="https://github.com/user-attachments/assets/0da7b7fa-2214-4016-9547-a6e1c9165a92" />


## ✨ Features

- **🏠 Rooftop Detection** - Automatically detects rooftop regions from satellite imagery or pre-segmented masks
- **🔍 Obstacle Avoidance** - Identifies chimneys, vents, skylights, and other obstacles
- **☀️ Optimal Panel Placement** - Calculates best positions for solar panels with proper spacing
- **⚡ Energy Estimation** - Computes annual energy production based on location and panel specs
- **🌱 Environmental Impact** - Shows CO₂ offset, equivalent trees planted, and more
- **🎨 Modern Web Interface** - React + TypeScript frontend with animated visualizations

## 📸 Screenshots

| Input Rooftop | Analysis Output |
|---------------|-----------------|
| <img src="https://github.com/user-attachments/assets/015d1834-5ea7-4ee5-84bf-014e731ef6e2" width="200"/> | <img src="https://github.com/user-attachments/assets/95858066-df56-4024-8186-c64d860e277e" width="200"/> |

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- pip & npm

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/SolarPanelPlacementOptimizer.git
cd SolarPanelPlacementOptimizer

# Install Python dependencies
pip install -r requirements.txt
pip install flask flask-cors

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Running the Application

**Terminal 1 - Start Backend:**
```bash
python app.py
```
> Backend runs at http://localhost:5000

**Terminal 2 - Start Frontend:**
```bash
cd frontend
npm run dev
```
> Frontend runs at http://localhost:3000

### Command Line Usage

You can also use the CLI directly:

```bash
# Analyze a single image
python analyze_rooftop.py testcases/1.jpg

# Specify output directory
python analyze_rooftop.py testcases/5.jpg --output-dir results

# Custom location (latitude/longitude)
python analyze_rooftop.py image.jpg --lat 40.7128 --lon -74.0060
```

## 📁 Project Structure

```
SolarPanelPlacementOptimizer/
├── analyze_rooftop.py      # Core analysis engine
├── app.py                  # Flask API backend
├── requirements.txt        # Python dependencies
├── testcases/              # Sample rooftop images
├── output/                 # Analysis results
└── frontend/               # React + TypeScript UI
    ├── src/
    │   ├── App.tsx
    │   ├── components/
    │   │   ├── HeroSection.tsx
    │   │   ├── UploadZone.tsx
    │   │   ├── DemoGallery.tsx
    │   │   ├── ProgressStepper.tsx
    │   │   ├── ResultsSection.tsx
    │   │   ├── StatsGrid.tsx
    │   │   └── ImpactVisuals.tsx
    │   └── index.css
    └── package.json
```

## ⚙️ Configuration

Default settings in `analyze_rooftop.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `latitude` | 28.6139 | Location latitude (Delhi, India) |
| `longitude` | 77.2090 | Location longitude |
| `pixel_to_meter` | 0.15 | Meters per pixel at zoom 19 |
| `panel_width_m` | 1.0 | Panel width in meters |
| `panel_height_m` | 1.7 | Panel height in meters |
| `panel_efficiency` | 0.20 | 20% panel efficiency |
| `panel_power_w` | 300 | Watts per panel |

## 📊 Output

The analyzer generates:

1. **Visualization Image** (`*_analysis.png`) - Rooftop with panel overlay
2. **JSON Data** (`*_panels.json`) - Complete analysis including:
   - Panel positions and dimensions
   - Energy production estimates
   - Suitability score

### Sample Output Calculations

For a rooftop with **25 panels**:

- **System Capacity:** `25 × 300W / 1000 = 7.5 kW`
- **Solar Irradiance:** `2200 − (28.6 × 8) ≈ 1971 kWh/m²/year`
- **Annual Energy:** `~14,409 kWh/year`
- **Monthly Average:** `~1,201 kWh/month`
- **CO₂ Offset:** `~11,815 kg/year`

## 🧪 Test Cases

The `testcases/` folder contains sample images:

| Image | Type | Detection |
|-------|------|-----------|
| 1.jpg | Pre-segmented mask | ✅ 25 panels |
| 5.jpg | Large building mask | ✅ ~50 panels |
| 9.jpg | Medium rooftop | ✅ ~30 panels |
| 21.jpg | Raw satellite | ⚠️ May vary |

> **Tip:** Pre-segmented masks (white roof on dark background) work best!

## 🛠️ Tech Stack

**Backend:**
- Python 3.x
- OpenCV (cv2)
- NumPy
- Flask + Flask-CORS

**Frontend:**
- React 18
- TypeScript
- Vite
- CSS3 (Glassmorphism, Animations)

## 📄 API Reference

### `POST /api/analyze`

Upload an image for analysis.

**Request:**
- `Content-Type: multipart/form-data`
- `image`: Image file (PNG, JPG, JPEG, WebP, BMP)

**Response:**
```json
{
  "success": true,
  "total_panels": 25,
  "total_capacity_kw": 7.5,
  "total_annual_kwh": 14409,
  "total_co2_offset": 11815,
  "analysis_image_url": "/output/xyz_analysis.png",
  "analyses": [...]
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV for image processing
- React & Vite for the modern frontend
- The open-source community

---

<p align="center">
  Made with ☀️ for a greener future
</p>

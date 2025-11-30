"""
Complete Solar Building Analysis Pipeline
Run this file to analyze satellite images for solar panel placement
"""

import cv2
import numpy as np
import os
from pathlib import Path

# Import our modules
from EnhancedBuildingDetector import EnhancedBuildingDetector
from SolarPanelOptimizer import SolarPanelOptimizer


def check_dependencies():
    """Check if all required packages are installed"""
    required = ["cv2", "numpy", "matplotlib", "sklearn", "skimage", "scipy"]
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print("❌ Missing packages:", ", ".join(missing))
        print("\n📦 Install them with:")
        print(
            "pip install opencv-python numpy matplotlib scikit-learn scikit-image scipy pillow"
        )
        return False

    print("✅ All dependencies installed!\n")
    return True


def create_sample_image():
    """Create a sample satellite image if none exists (for testing)"""
    print("📸 Creating sample satellite image for testing...")

    # Create a simple image with rectangles representing buildings
    img = np.ones((800, 1000, 3), dtype=np.uint8) * 200  # Gray background

    # Add some "buildings" (rectangles)
    buildings = [
        (100, 100, 200, 150),  # (x, y, width, height)
        (400, 150, 180, 200),
        (700, 100, 150, 180),
        (150, 400, 220, 160),
        (500, 450, 190, 140),
    ]

    for x, y, w, h in buildings:
        # Building body (lighter color)
        cv2.rectangle(img, (x, y), (x + w, y + h), (220, 210, 200), -1)
        # Roof edges (darker)
        cv2.rectangle(img, (x, y), (x + w, y + h), (180, 170, 160), 2)
        # Add some texture
        for i in range(5):
            cv2.line(
                img, (x + i * w // 5, y), (x + i * w // 5, y + h), (200, 190, 180), 1
            )

    # Add some trees/shadows (darker regions)
    cv2.circle(img, (320, 280), 40, (100, 120, 80), -1)
    cv2.circle(img, (600, 350), 35, (100, 120, 80), -1)

    cv2.imwrite("sample_satellite.jpg", img)
    print("✅ Sample image created: sample_satellite.jpg\n")
    return "sample_satellite.jpg"


def find_satellite_image():
    """Find a satellite image to process"""
    # Check for common image names
    common_names = [
        "satellite.jpg",
        "satellite.png",
        "satellite_image.jpg",
        "satellite_image.png",
        "aerial.jpg",
        "aerial.png",
        "sample_satellite.jpg",
    ]

    # Check current directory
    for name in common_names:
        if os.path.exists(name):
            print(f"✅ Found image: {name}\n")
            return name

    # Check for any jpg/png files
    image_files = list(Path(".").glob("*.jpg")) + list(Path(".").glob("*.png"))
    if image_files:
        img_path = str(image_files[0])
        print(f"✅ Found image: {img_path}\n")
        return img_path

    # No image found, create sample
    print("❌ No satellite image found in current directory")
    response = input("📸 Create a sample image for testing? (y/n): ")
    if response.lower() == "y":
        return create_sample_image()
    else:
        print("\n💡 Please add a satellite image and run again!")
        print("   Supported formats: .jpg, .png")
        return None


def run_complete_analysis(image_path, location_config=None):
    """
    Run complete building detection and solar analysis

    Args:
        image_path: Path to satellite image
        location_config: Dict with 'latitude', 'longitude', 'pixel_to_meter'
    """
    print("=" * 70)
    print("🏗️  SOLAR BUILDING ANALYSIS PIPELINE")
    print("=" * 70)

    # Load image
    print(f"\n📂 Loading image: {image_path}")
    image = cv2.imread(image_path)

    if image is None:
        print("❌ Error: Could not load image!")
        return

    h, w = image.shape[:2]
    print(f"✅ Image loaded: {w}x{h} pixels\n")

    # Step 1: Detect Buildings
    print("-" * 70)
    print("STEP 1: BUILDING DETECTION")
    print("-" * 70)

    detector = EnhancedBuildingDetector(
        config={
            "min_area": 500,  # Adjust based on your image
            "max_area": 50000,
        }
    )

    print("🔍 Detecting buildings at multiple scales...")
    contours = detector.multi_scale_detection(image, scales=[0.8, 1.0, 1.2])
    print(f"✅ Found {len(contours)} buildings\n")

    if len(contours) == 0:
        print("❌ No buildings detected! Try:")
        print("   1. Use a different satellite image")
        print("   2. Adjust min_area and max_area in config")
        return

    # Regularize polygons
    print("📐 Regularizing building polygons...")
    regularized = [detector.regularize_polygon(cnt) for cnt in contours]
    print("✅ Polygons regularized\n")

    # Step 2: Solar Analysis
    print("-" * 70)
    print("STEP 2: SOLAR PANEL ANALYSIS")
    print("-" * 70)

    # Default to Delhi if no location provided
    if location_config is None:
        location_config = {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "pixel_to_meter": 0.15,
        }
        print(f"📍 Using default location: Delhi, India")
    else:
        print(
            f"📍 Location: {location_config['latitude']}, {location_config['longitude']}"
        )

    optimizer = SolarPanelOptimizer(
        config={
            **location_config,
            "panel_width": 1.0,
            "panel_height": 1.7,
            "panel_efficiency": 0.20,
            "min_roof_area": 20,
            "system_losses": 0.14,
        }
    )

    print(f"🌞 Analyzing {len(regularized)} buildings for solar potential...\n")
    solar_results = optimizer.batch_analyze_buildings(image, regularized)

    # Step 3: Results Summary
    print("\n" + "=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)

    # Count by rating
    ratings = {"Excellent": 0, "Good": 0, "Fair": 0, "Poor": 0}
    for result in solar_results:
        ratings[result["suitability_rating"]] += 1

    print(f"\n🏆 Building Ratings:")
    print(f"   Excellent: {ratings['Excellent']} buildings")
    print(f"   Good:      {ratings['Good']} buildings")
    print(f"   Fair:      {ratings['Fair']} buildings")
    print(f"   Poor:      {ratings['Poor']} buildings")

    # Total capacity and energy
    total_capacity = sum(r["panel_layout"]["total_capacity_kw"] for r in solar_results)
    total_energy = sum(r["estimated_annual_energy_kwh"] for r in solar_results)
    total_panels = sum(r["panel_layout"]["num_panels"] for r in solar_results)

    print(f"\n⚡ Energy Summary:")
    print(f"   Total panels:          {total_panels}")
    print(f"   Total capacity:        {total_capacity:.1f} kW")
    print(f"   Annual production:     {total_energy:.0f} kWh/year")
    print(f"   Monthly average:       {total_energy / 12:.0f} kWh/month")
    print(f"   CO₂ offset:            {total_energy * 0.82:.0f} kg/year")

    # Top 3 buildings
    if solar_results:
        print(f"\n🥇 Top 3 Buildings by Solar Potential:")
        for i, result in enumerate(solar_results[:3], 1):
            print(f"\n   #{i} - Building {result['building_id']}:")
            print(f"      Rating: {result['suitability_rating']}")
            print(f"      Roof area: {result['roof_area_m2']:.1f} m²")
            print(f"      Panels: {result['panel_layout']['num_panels']}")
            print(
                f"      Annual energy: {result['estimated_annual_energy_kwh']:.0f} kWh/year"
            )
    else:
        print("\n⚠️  No buildings were successfully analyzed")
        print("   This may be due to buildings being too small or detection issues")
        return

    # Step 4: Save Results
    print("\n" + "=" * 70)
    print("💾 SAVING RESULTS")
    print("=" * 70)

    # Create output directory
    os.makedirs("output", exist_ok=True)

    # Save annotated image
    output_image = image.copy()
    for i, cnt in enumerate(regularized):
        result = solar_results[i]

        # Color based on rating
        color_map = {
            "Excellent": (0, 255, 0),  # Green
            "Good": (0, 255, 255),  # Yellow
            "Fair": (0, 165, 255),  # Orange
            "Poor": (0, 0, 255),  # Red
        }
        color = color_map[result["suitability_rating"]]

        cv2.drawContours(output_image, [cnt], -1, color, 3)

        # Add label
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(
                output_image,
                f"#{result['building_id']}",
                (cx - 20, cy),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

    output_path = "output/buildings_annotated.jpg"
    cv2.imwrite(output_path, output_image)
    print(f"✅ Annotated image saved: {output_path}")

    # Save JSON report
    optimizer.export_solar_report(solar_results, "output/solar_report.json")

    # Save GeoJSON
    metrics = [detector.calculate_building_metrics(cnt) for cnt in regularized]
    detector.export_to_geojson(
        regularized, metrics, output_path="output/buildings.geojson"
    )
    print(f"✅ GeoJSON saved: output/buildings.geojson")

    # Step 5: Visualization
    print("\n" + "=" * 70)
    print("📈 GENERATING VISUALIZATIONS")
    print("=" * 70)

    response = input("\n📊 Show detailed visualization for top building? (y/n): ")
    if response.lower() == "y":
        top_building = solar_results[0]
        building_id = top_building["building_id"] - 1
        optimizer.visualize_solar_analysis(
            image, regularized[building_id], top_building
        )

    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE!")
    print("=" * 70)
    print("\n📁 Check the 'output' folder for:")
    print("   • buildings_annotated.jpg - Color-coded buildings")
    print("   • solar_report.json - Detailed analysis data")
    print("   • buildings.geojson - GIS-compatible format")
    print("\n🌟 Done! Thank you for using Solar Building Analyzer!")


def interactive_mode():
    """Interactive mode with menu"""
    print("\n" + "=" * 70)
    print("🌞 SOLAR BUILDING ANALYZER - INTERACTIVE MODE")
    print("=" * 70)

    # Find or create image
    image_path = find_satellite_image()
    if not image_path:
        return

    # Ask for location
    print("\n📍 Location Configuration")
    print("-" * 70)
    use_custom = input("Use custom location? (y/n, default: Delhi): ")

    if use_custom.lower() == "y":
        try:
            lat = float(input("Enter latitude (e.g., 28.6139): "))
            lon = float(input("Enter longitude (e.g., 77.2090): "))
            pixel_m = float(input("Enter meters per pixel (default 0.15): ") or "0.15")

            location_config = {
                "latitude": lat,
                "longitude": lon,
                "pixel_to_meter": pixel_m,
            }
        except ValueError:
            print("❌ Invalid input, using defaults")
            location_config = None
    else:
        location_config = None

    # Run analysis
    run_complete_analysis(image_path, location_config)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    print("\n")
    print("🏗️ " + "=" * 66 + " 🏗️")
    print("   SOLAR BUILDING ANALYZER - Satellite Image Analysis Tool")
    print("🏗️ " + "=" * 66 + " 🏗️")

    # Check dependencies
    if not check_dependencies():
        exit(1)

    # Run interactive mode
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error occurred: {e}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Make sure image file exists")
        print("   2. Check that image is not corrupted")
        print("   3. Verify all dependencies are installed")
        import traceback

        traceback.print_exc()

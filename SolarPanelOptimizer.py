"""
Solar Panel Placement Optimizer for Satellite Images
New Features for Solar Energy Analysis:
1. Roof surface segmentation and analysis
2. Roof orientation and slope calculation
3. Solar exposure scoring (considering shadows)
4. Optimal panel placement zones
5. Panel capacity estimation
6. Annual energy yield prediction
7. Shading impact analysis
"""

import cv2
import numpy as np
from typing import List, Dict, Tuple
import json
from datetime import datetime
import matplotlib.pyplot as plt
from scipy.ndimage import label, binary_erosion


class SolarPanelOptimizer:
    """Analyzes satellite imagery for optimal solar panel placement"""

    def __init__(self, config: Dict = None):
        self.config = config or {
            "latitude": 28.6139,  # Default: Delhi, India
            "longitude": 77.2090,
            "panel_width": 1.0,  # meters
            "panel_height": 1.7,  # meters
            "panel_efficiency": 0.20,  # 20% efficiency
            "system_losses": 0.14,  # 14% system losses
            "min_roof_area": 20,  # m² minimum
            "pixel_to_meter": 0.15,  # meters per pixel at zoom 19
        }

    def analyze_roof_for_solar(
        self, image: np.ndarray, building_contour: np.ndarray
    ) -> Dict:
        """
        Complete solar analysis for a single building
        Returns comprehensive solar suitability report
        """
        # Extract roof region
        roof_mask = self._create_roof_mask(image, building_contour)
        roof_image = cv2.bitwise_and(image, image, mask=roof_mask)

        # Analyze roof characteristics
        roof_type = self._classify_roof_type(roof_image, roof_mask)
        roof_area = self._calculate_roof_area(building_contour)
        roof_orientation = self._calculate_roof_orientation(building_contour)
        roof_slope = self._estimate_roof_slope(roof_image, roof_mask)

        # Solar analysis
        shading_score = self._analyze_shading(image, building_contour, roof_mask)
        solar_zones = self._identify_optimal_zones(roof_image, roof_mask, shading_score)
        panel_layout = self._calculate_panel_layout(solar_zones, roof_area)

        # Energy calculations
        solar_irradiance = self._calculate_solar_irradiance(
            roof_orientation, roof_slope, shading_score
        )
        annual_energy = self._estimate_annual_energy(
            panel_layout["num_panels"], solar_irradiance
        )

        return {
            "roof_type": roof_type,
            "roof_area_m2": roof_area,
            "usable_area_m2": solar_zones["usable_area"],
            "roof_orientation": roof_orientation,
            "roof_slope_degrees": roof_slope,
            "shading_score": shading_score,  # 0-1, higher is better
            "solar_zones": solar_zones,
            "panel_layout": panel_layout,
            "solar_irradiance_kwh_m2_year": solar_irradiance,
            "estimated_annual_energy_kwh": annual_energy,
            "suitability_rating": self._calculate_suitability_rating(
                roof_area, shading_score, roof_orientation, roof_slope
            ),
        }

    def _create_roof_mask(self, image: np.ndarray, contour: np.ndarray) -> np.ndarray:
        """Create binary mask for roof region"""
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)
        return mask

    def _classify_roof_type(self, roof_image: np.ndarray, mask: np.ndarray) -> str:
        """
        Classify roof type: flat, gabled, hipped, complex
        Uses texture and color analysis
        """
        if len(roof_image.shape) == 3:
            gray = cv2.cvtColor(roof_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = roof_image

        # Analyze texture variance
        masked_gray = cv2.bitwise_and(gray, gray, mask=mask)
        roi = masked_gray[mask > 0]

        if len(roi) == 0:
            return "unknown"

        std_dev = np.std(roi)
        mean_intensity = np.mean(roi)

        # Edge detection for roof structure
        edges = cv2.Canny(masked_gray, 50, 150)
        edge_density = np.sum(edges) / np.sum(mask > 0)

        # Classification based on texture and edges
        if std_dev < 20 and edge_density < 0.05:
            return "flat"  # Best for solar!
        elif edge_density > 0.15:
            return "complex"  # Multiple roof sections
        elif std_dev > 30:
            return "gabled"  # Pitched roof
        else:
            return "hipped"

    def _calculate_roof_area(self, contour: np.ndarray) -> float:
        """Calculate roof area in square meters"""
        pixel_area = cv2.contourArea(contour)
        meter_per_pixel = self.config["pixel_to_meter"]
        area_m2 = pixel_area * (meter_per_pixel**2)
        return area_m2

    def _calculate_roof_orientation(self, contour: np.ndarray) -> float:
        """
        Calculate roof orientation (azimuth angle)
        0° = North, 90° = East, 180° = South, 270° = West
        South-facing is optimal in Northern Hemisphere
        """
        rect = cv2.minAreaRect(contour)
        angle = rect[2]

        # Convert to compass bearing (0-360)
        # Assuming image is oriented with North up
        azimuth = (90 - angle) % 360

        return azimuth

    def _estimate_roof_slope(self, roof_image: np.ndarray, mask: np.ndarray) -> float:
        """
        Estimate roof slope/pitch in degrees
        Uses shadow analysis and building height estimation
        """
        # Simplified estimation based on brightness variation
        if len(roof_image.shape) == 3:
            gray = cv2.cvtColor(roof_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = roof_image

        masked = cv2.bitwise_and(gray, gray, mask=mask)
        roi = masked[mask > 0]

        if len(roi) == 0:
            return 0.0

        # Analyze brightness gradient (bright = steep)
        brightness_range = np.max(roi) - np.min(roi)

        # Heuristic: map brightness range to slope
        # 0-30 range → flat (0-10°)
        # 30-60 range → moderate (10-30°)
        # 60+ range → steep (30-45°)

        if brightness_range < 30:
            slope = brightness_range / 3  # 0-10°
        elif brightness_range < 60:
            slope = 10 + (brightness_range - 30) / 1.5  # 10-30°
        else:
            slope = min(45, 30 + (brightness_range - 60) / 4)  # 30-45°

        return slope

    def _analyze_shading(
        self, image: np.ndarray, contour: np.ndarray, roof_mask: np.ndarray
    ) -> float:
        """
        Analyze shading on roof from trees, nearby buildings
        Returns shading score: 0 (fully shaded) to 1 (no shade)
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Analyze roof region brightness
        roof_pixels = gray[roof_mask > 0]

        if len(roof_pixels) == 0:
            return 0.5

        # Compare with surrounding area
        kernel = np.ones((50, 50), np.uint8)
        dilated = cv2.dilate(roof_mask, kernel, iterations=1)
        surrounding = gray[dilated > 0]

        roof_brightness = np.mean(roof_pixels)
        surrounding_brightness = np.mean(surrounding)

        # Detect very dark regions (shadows)
        shadow_threshold = np.percentile(roof_pixels, 25)
        shadow_pixels = np.sum(roof_pixels < shadow_threshold)
        shadow_ratio = shadow_pixels / len(roof_pixels)

        # Calculate shading score
        brightness_ratio = roof_brightness / (surrounding_brightness + 1e-6)
        shading_score = brightness_ratio * (1 - shadow_ratio * 0.5)

        return np.clip(shading_score, 0, 1)

    def _identify_optimal_zones(
        self, roof_image: np.ndarray, mask: np.ndarray, shading_score: float
    ) -> Dict:
        """
        Identify optimal zones for panel placement
        Avoids edges, shaded areas, obstructions
        """
        # Erode mask to avoid roof edges (5% margin)
        kernel_size = max(3, int(np.sqrt(np.sum(mask > 0)) * 0.05))
        kernel = cv2.getStructuringElement(
            cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
        )
        usable_mask = cv2.erode(mask, kernel, iterations=2)

        # Detect obstructions (chimneys, vents, etc.)
        if len(roof_image.shape) == 3:
            gray = cv2.cvtColor(roof_image, cv2.COLOR_BGR2GRAY)
        else:
            gray = roof_image

        # Find very bright or very dark spots (obstructions)
        _, bright = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        _, dark = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        obstructions = cv2.bitwise_or(bright, dark)

        # Remove obstructions from usable area
        usable_mask = cv2.bitwise_and(usable_mask, cv2.bitwise_not(obstructions))

        # Calculate usable area
        usable_pixels = np.sum(usable_mask > 0)
        usable_area_m2 = usable_pixels * (self.config["pixel_to_meter"] ** 2)

        # Create zone quality map (0-255)
        quality_map = usable_mask.copy()

        return {
            "usable_mask": usable_mask,
            "usable_area": usable_area_m2,
            "quality_map": quality_map,
            "obstruction_mask": obstructions,
        }

    def _calculate_panel_layout(self, solar_zones: Dict, roof_area: float) -> Dict:
        """
        Calculate optimal panel layout
        Returns number of panels, arrangement, coverage
        """
        panel_area = self.config["panel_width"] * self.config["panel_height"]  # m²
        usable_area = solar_zones["usable_area"]

        # Account for spacing between panels (10% loss)
        effective_area = usable_area * 0.90

        # Calculate number of panels
        num_panels = int(effective_area / panel_area)

        # Calculate panel dimensions in pixels
        meter_to_pixel = 1 / self.config["pixel_to_meter"]
        panel_width_px = int(self.config["panel_width"] * meter_to_pixel)
        panel_height_px = int(self.config["panel_height"] * meter_to_pixel)

        # Generate panel positions (grid layout)
        mask = solar_zones["usable_mask"]
        panel_positions = self._generate_panel_grid(
            mask, panel_width_px, panel_height_px, num_panels
        )

        # Calculate system capacity (kW)
        panel_capacity_kw = 0.3  # Typical 300W panel
        total_capacity_kw = num_panels * panel_capacity_kw

        return {
            "num_panels": num_panels,
            "panel_positions": panel_positions,
            "total_capacity_kw": total_capacity_kw,
            "coverage_ratio": (num_panels * panel_area) / roof_area
            if roof_area > 0
            else 0,
            "panel_area_m2": num_panels * panel_area,
        }

    def _generate_panel_grid(
        self, mask: np.ndarray, panel_w: int, panel_h: int, max_panels: int
    ) -> List[Tuple[int, int]]:
        """Generate grid of panel positions within usable area"""
        positions = []
        h, w = mask.shape

        spacing = 5  # pixels between panels

        for y in range(0, h - panel_h, panel_h + spacing):
            for x in range(0, w - panel_w, panel_w + spacing):
                # Check if panel area is fully within usable zone
                panel_region = mask[y : y + panel_h, x : x + panel_w]
                if (
                    panel_region.size > 0
                    and np.sum(panel_region) > 0.8 * panel_region.size * 255
                ):
                    positions.append((x, y))
                    if len(positions) >= max_panels:
                        return positions

        return positions

    def _calculate_solar_irradiance(
        self, orientation: float, slope: float, shading_score: float
    ) -> float:
        """
        Calculate annual solar irradiance (kWh/m²/year)
        Considers location, roof orientation, slope, and shading
        """
        # Base irradiance for location (Delhi example: ~1800 kWh/m²/year)
        latitude = self.config["latitude"]

        # Estimate base irradiance from latitude
        # Equator ≈ 2000, higher latitudes lower
        base_irradiance = 2200 - abs(latitude) * 8

        # Orientation factor (South-facing is optimal in Northern Hemisphere)
        if latitude > 0:  # Northern Hemisphere
            optimal_azimuth = 180  # South
        else:  # Southern Hemisphere
            optimal_azimuth = 0  # North

        azimuth_deviation = abs(orientation - optimal_azimuth)
        azimuth_deviation = min(azimuth_deviation, 360 - azimuth_deviation)
        orientation_factor = 1.0 - (azimuth_deviation / 180) * 0.25

        # Slope factor (optimal ≈ latitude angle)
        optimal_slope = abs(latitude)
        slope_deviation = abs(slope - optimal_slope)
        slope_factor = 1.0 - (slope_deviation / 90) * 0.15

        # Apply factors
        adjusted_irradiance = (
            base_irradiance * orientation_factor * slope_factor * shading_score
        )

        return adjusted_irradiance

    def _estimate_annual_energy(
        self, num_panels: int, solar_irradiance: float
    ) -> float:
        """
        Estimate annual energy production (kWh/year)
        """
        panel_area = self.config["panel_width"] * self.config["panel_height"]
        total_area = num_panels * panel_area

        efficiency = self.config["panel_efficiency"]
        system_losses = self.config["system_losses"]

        # Annual energy = Area × Irradiance × Efficiency × (1 - Losses)
        annual_energy = total_area * solar_irradiance * efficiency * (1 - system_losses)

        return annual_energy

    def _calculate_suitability_rating(
        self, roof_area: float, shading_score: float, orientation: float, slope: float
    ) -> str:
        """
        Overall suitability rating: Excellent, Good, Fair, Poor
        """
        score = 0

        # Area score (0-30 points)
        if roof_area >= 50:
            score += 30
        elif roof_area >= 30:
            score += 20
        elif roof_area >= 20:
            score += 10

        # Shading score (0-30 points)
        score += shading_score * 30

        # Orientation score (0-25 points)
        latitude = self.config["latitude"]
        optimal_azimuth = 180 if latitude > 0 else 0
        azimuth_deviation = abs(orientation - optimal_azimuth)
        azimuth_deviation = min(azimuth_deviation, 360 - azimuth_deviation)
        orientation_score = (1 - azimuth_deviation / 180) * 25
        score += orientation_score

        # Slope score (0-15 points)
        optimal_slope = abs(latitude)
        slope_deviation = abs(slope - optimal_slope)
        slope_score = (1 - slope_deviation / 90) * 15
        score += slope_score

        # Rating
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Fair"
        else:
            return "Poor"

    def visualize_solar_analysis(
        self, image: np.ndarray, contour: np.ndarray, analysis: Dict
    ) -> None:
        """
        Create comprehensive visualization of solar analysis
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle(
            f"Solar Panel Analysis - {analysis['suitability_rating']} Rating",
            fontsize=16,
            fontweight="bold",
        )

        # 1. Original building
        output1 = image.copy()
        cv2.drawContours(output1, [contour], -1, (0, 255, 0), 3)
        axes[0, 0].imshow(cv2.cvtColor(output1, cv2.COLOR_BGR2RGB))
        axes[0, 0].set_title("Building Location")
        axes[0, 0].axis("off")

        # 2. Usable roof area
        mask = analysis["solar_zones"]["usable_mask"]
        colored_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        colored_mask[:, :, 1] = mask  # Green channel
        overlay = cv2.addWeighted(image, 0.5, colored_mask, 0.5, 0)
        axes[0, 1].imshow(cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB))
        axes[0, 1].set_title(f"Usable Area: {analysis['usable_area_m2']:.1f} m²")
        axes[0, 1].axis("off")

        # 3. Panel layout
        output3 = image.copy()
        for x, y in analysis["panel_layout"]["panel_positions"]:
            meter_to_px = 1 / self.config["pixel_to_meter"]
            w = int(self.config["panel_width"] * meter_to_px)
            h = int(self.config["panel_height"] * meter_to_px)
            cv2.rectangle(output3, (x, y), (x + w, y + h), (255, 0, 0), 2)
        axes[0, 2].imshow(cv2.cvtColor(output3, cv2.COLOR_BGR2RGB))
        axes[0, 2].set_title(
            f"Panel Layout: {analysis['panel_layout']['num_panels']} panels"
        )
        axes[0, 2].axis("off")

        # 4. Key metrics
        axes[1, 0].axis("off")
        metrics_text = f"""
        Roof Type: {analysis["roof_type"].capitalize()}
        Roof Area: {analysis["roof_area_m2"]:.1f} m²
        Usable Area: {analysis["usable_area_m2"]:.1f} m²
        
        Orientation: {analysis["roof_orientation"]:.0f}°
        Slope: {analysis["roof_slope_degrees"]:.1f}°
        Shading Score: {analysis["shading_score"]:.2f}
        
        System Capacity: {analysis["panel_layout"]["total_capacity_kw"]:.1f} kW
        """
        axes[1, 0].text(
            0.1,
            0.5,
            metrics_text,
            fontsize=12,
            verticalalignment="center",
            family="monospace",
        )
        axes[1, 0].set_title("Key Metrics")

        # 5. Energy production
        axes[1, 1].axis("off")
        energy_text = f"""
        Solar Irradiance: {analysis["solar_irradiance_kwh_m2_year"]:.0f} kWh/m²/year
        
        Annual Production: {analysis["estimated_annual_energy_kwh"]:.0f} kWh/year
        
        Monthly Average: {analysis["estimated_annual_energy_kwh"] / 12:.0f} kWh/month
        
        Daily Average: {analysis["estimated_annual_energy_kwh"] / 365:.1f} kWh/day
        
        CO₂ Offset: {analysis["estimated_annual_energy_kwh"] * 0.82:.0f} kg/year
        """
        axes[1, 1].text(
            0.1,
            0.5,
            energy_text,
            fontsize=12,
            verticalalignment="center",
            family="monospace",
            color="darkgreen",
        )
        axes[1, 1].set_title("Energy Production")

        # 6. Suitability gauge
        ax = axes[1, 2]
        ratings = ["Poor", "Fair", "Good", "Excellent"]
        colors = ["red", "orange", "yellow", "green"]
        rating_idx = ratings.index(analysis["suitability_rating"])

        ax.barh(ratings, [1, 1, 1, 1], color=["lightgray"] * 4)
        ax.barh(ratings[rating_idx], 1, color=colors[rating_idx])
        ax.set_xlim(0, 1)
        ax.set_title("Suitability Rating")
        ax.set_xlabel("Rating")

        plt.tight_layout()
        plt.show()

    def batch_analyze_buildings(
        self, image: np.ndarray, contours: List[np.ndarray]
    ) -> List[Dict]:
        """
        Analyze multiple buildings and rank by solar potential
        """
        results = []

        print(f"🌞 Analyzing {len(contours)} buildings for solar potential...\n")

        for i, contour in enumerate(contours):
            print(f"[{i + 1}/{len(contours)}] Analyzing building...")

            try:
                analysis = self.analyze_roof_for_solar(image, contour)
                analysis["building_id"] = i + 1
                results.append(analysis)

                print(
                    f"  ✓ {analysis['suitability_rating']} - "
                    f"{analysis['panel_layout']['num_panels']} panels, "
                    f"{analysis['estimated_annual_energy_kwh']:.0f} kWh/year\n"
                )
            except Exception as e:
                print(f"  ✗ Failed: {e}\n")

        # Sort by annual energy production
        results.sort(key=lambda x: x["estimated_annual_energy_kwh"], reverse=True)

        return results

    def _make_json_serializable(self, obj):
        """Convert numpy types to Python native types for JSON serialization"""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, dict):
            return {
                key: self._make_json_serializable(value) for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj

    def export_solar_report(
        self, results: List[Dict], output_path: str = "solar_report.json"
    ):
        """Export comprehensive solar analysis report"""
        # Convert results to JSON-serializable format
        serializable_results = self._make_json_serializable(results)

        report = {
            "timestamp": datetime.now().isoformat(),
            "location": {
                "latitude": self.config["latitude"],
                "longitude": self.config["longitude"],
            },
            "total_buildings": len(results),
            "total_capacity_kw": sum(
                r["panel_layout"]["total_capacity_kw"] for r in results
            ),
            "total_annual_energy_kwh": sum(
                r["estimated_annual_energy_kwh"] for r in results
            ),
            "buildings": serializable_results,
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"📄 Exported solar report to {output_path}")

        # Print summary
        excellent = sum(1 for r in results if r["suitability_rating"] == "Excellent")
        good = sum(1 for r in results if r["suitability_rating"] == "Good")
        fair = sum(1 for r in results if r["suitability_rating"] == "Fair")
        poor = sum(1 for r in results if r["suitability_rating"] == "Poor")

        print(f"\n📊 Summary:")
        print(f"   Excellent: {excellent} buildings")
        print(f"   Good: {good} buildings")
        print(f"   Fair: {fair} buildings")
        print(f"   Poor: {poor} buildings")
        print(f"   Total capacity: {report['total_capacity_kw']:.1f} kW")
        print(
            f"   Total annual energy: {report['total_annual_energy_kwh']:.0f} kWh/year"
        )


# Example usage
if __name__ == "__main__":
    print("🌞 Solar Panel Placement Optimizer")
    print("=" * 60)

    # Initialize optimizer with location
    optimizer = SolarPanelOptimizer(
        config={
            "latitude": 28.6139,  # Delhi
            "longitude": 77.2090,
            "pixel_to_meter": 0.15,
            "panel_efficiency": 0.20,
        }
    )

    print("\n✓ Optimizer initialized for Delhi, India")
    print("\nFeatures:")
    print("  • Roof type classification")
    print("  • Orientation and slope analysis")
    print("  • Shading impact assessment")
    print("  • Optimal panel placement")
    print("  • Energy yield estimation")
    print("  • Suitability rating")

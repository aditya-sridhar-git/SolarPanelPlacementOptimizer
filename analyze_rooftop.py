"""
Solar Panel Rooftop Analyzer
============================
A unified entry point for analyzing any satellite/rooftop image and determining
optimal solar panel placement with complete geometry output.

Usage:
    python analyze_rooftop.py <image_path> [--output-dir OUTPUT_DIR]
    
Example:
    python analyze_rooftop.py testcases/1.jpg
    python analyze_rooftop.py testcases/5.jpg --output-dir results
"""

import cv2
import numpy as np
import os
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import math


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_CONFIG = {
    # Location settings (default: Delhi, India)
    'latitude': 28.6139,
    'longitude': 77.2090,
    
    # Image resolution
    'pixel_to_meter': 0.15,  # meters per pixel at zoom 19
    
    # Solar panel specifications (standard residential panel)
    'panel_width_m': 1.0,      # meters
    'panel_height_m': 1.7,     # meters
    'panel_efficiency': 0.20,  # 20% efficiency
    'panel_power_w': 300,      # watts per panel
    
    # Detection settings
    'min_building_area': 500,   # minimum building area in pixels
    'max_building_area': 50000, # maximum building area in pixels
    
    # Panel placement settings
    'edge_margin_percent': 0.10,  # 10% margin from roof edges
    'panel_spacing_m': 0.1,       # 10cm spacing between panels
}


# ============================================================================
# BUILDING DETECTOR
# ============================================================================

class RooftopDetector:
    """Detects rooftop regions from satellite imagery"""
    
    def __init__(self, config: Dict = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
    
    def detect_rooftops(self, image: np.ndarray) -> List[Dict]:
        """
        Detect all rooftop regions in the image.
        
        Handles two types of input:
        1. Pre-segmented masks (white roof on dark background)
        2. Raw satellite imagery
        
        Returns:
            List of rooftop dictionaries with 'contour', 'area_pixels', 'center', etc.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # Check if this is a pre-segmented mask (mostly black with white regions)
        mean_intensity = np.mean(gray)
        white_ratio = np.sum(gray > 200) / gray.size
        
        if white_ratio > 0.05 and white_ratio < 0.8:
            # This appears to be a pre-segmented roof mask
            # Use simple thresholding
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            valid_contours = []
            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area > 100:  # Minimum area threshold
                    valid_contours.append(cnt)
        else:
            # Raw satellite image - use edge detection approach
            blur = cv2.bilateralFilter(gray, 9, 75, 75)
            
            all_contours = []
            for scale in [0.75, 1.0, 1.25]:
                h, w = blur.shape
                resized = cv2.resize(blur, (int(w * scale), int(h * scale)))
                edges = cv2.Canny(resized, 50, 150)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for cnt in contours:
                    scaled_cnt = (cnt / scale).astype(np.int32)
                    area = cv2.contourArea(scaled_cnt)
                    if self.config['min_building_area'] < area < self.config['max_building_area']:
                        all_contours.append(scaled_cnt)
            
            valid_contours = self._non_max_suppression(all_contours)
        
        # Build rooftop info list
        rooftops = []
        for i, contour in enumerate(valid_contours):
            rooftops.append(self._analyze_rooftop(i + 1, contour, image))
        
        return rooftops
    
    def _analyze_rooftop(self, roof_id: int, contour: np.ndarray, image: np.ndarray) -> Dict:
        """Analyze a single rooftop region"""
        area_pixels = cv2.contourArea(contour)
        area_m2 = area_pixels * (self.config['pixel_to_meter'] ** 2)
        
        # Get the minimum area rectangle (oriented bounding box)
        rect = cv2.minAreaRect(contour)
        center, (width, height), angle = rect
        box_points = cv2.boxPoints(rect).astype(np.int32)
        
        # Calculate centroid
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
        else:
            cx, cy = int(center[0]), int(center[1])
        
        return {
            'id': roof_id,
            'contour': contour,
            'area_pixels': float(area_pixels),
            'area_m2': float(area_m2),
            'center': {'x': cx, 'y': cy},
            'bounding_rect': {
                'center': {'x': float(center[0]), 'y': float(center[1])},
                'width': float(max(width, height)),
                'height': float(min(width, height)),
                'angle': float(angle)
            },
            'box_points': box_points.tolist()
        }
    
    def _non_max_suppression(self, contours: List[np.ndarray], overlap_thresh: float = 0.3) -> List[np.ndarray]:
        """Remove overlapping detections"""
        if len(contours) == 0:
            return []
        
        boxes = np.array([cv2.boundingRect(cnt) for cnt in contours])
        areas = boxes[:, 2] * boxes[:, 3]
        idxs = np.argsort(areas)[::-1]
        
        keep = []
        while len(idxs) > 0:
            i = idxs[0]
            keep.append(i)
            
            if len(idxs) == 1:
                break
            
            xx1 = np.maximum(boxes[i, 0], boxes[idxs[1:], 0])
            yy1 = np.maximum(boxes[i, 1], boxes[idxs[1:], 1])
            xx2 = np.minimum(boxes[i, 0] + boxes[i, 2], boxes[idxs[1:], 0] + boxes[idxs[1:], 2])
            yy2 = np.minimum(boxes[i, 1] + boxes[i, 3], boxes[idxs[1:], 1] + boxes[idxs[1:], 3])
            
            w = np.maximum(0, xx2 - xx1)
            h = np.maximum(0, yy2 - yy1)
            overlap = (w * h) / areas[idxs[1:]]
            
            idxs = idxs[1:][overlap <= overlap_thresh]
        
        return [contours[i] for i in keep]


# ============================================================================
# SOLAR PANEL OPTIMIZER
# ============================================================================

class SolarPanelOptimizer:
    """Calculates optimal solar panel placement with obstacle avoidance and irregular roof support"""
    
    def __init__(self, config: Dict = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        
        # Pre-calculate panel dimensions in pixels
        self.panel_width_px = int(self.config['panel_width_m'] / self.config['pixel_to_meter'])
        self.panel_height_px = int(self.config['panel_height_m'] / self.config['pixel_to_meter'])
    
    def analyze_rooftop(self, image: np.ndarray, rooftop: Dict) -> Dict:
        """
        Analyze a rooftop for solar panel placement with obstacle avoidance.
        
        Returns complete analysis including panel shapes and positions.
        """
        contour = rooftop['contour']
        
        # Create roof mask
        mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)
        
        # Detect obstacles (chimneys, vents, AC units, skylights, etc.)
        obstacle_mask = self._detect_obstacles(image, mask)
        
        # Calculate usable area (erode edges + remove obstacles)
        margin_px = max(2, int(max(self.panel_width_px, self.panel_height_px) * 
                       self.config['edge_margin_percent']))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (margin_px, margin_px))
        usable_mask = cv2.erode(mask, kernel, iterations=1)
        
        # Remove obstacle areas from usable mask
        usable_mask = cv2.bitwise_and(usable_mask, cv2.bitwise_not(obstacle_mask))
        
        # Get roof orientation for optimal panel alignment
        roof_angle = rooftop['bounding_rect']['angle']
        
        # Calculate optimal panels with both orientations
        panels = self._place_panels_optimized(usable_mask, roof_angle, contour)
        
        # Calculate energy production
        energy_info = self._calculate_energy(len(panels))
        
        # Count obstacles found
        obstacle_count = self._count_obstacles(obstacle_mask)
        
        return {
            'rooftop_id': rooftop['id'],
            'roof_area_m2': rooftop['area_m2'],
            'usable_area_m2': np.sum(usable_mask > 0) * (self.config['pixel_to_meter'] ** 2),
            'roof_orientation_degrees': float(roof_angle),
            'obstacles_detected': obstacle_count,
            'panel_count': len(panels),
            'panels': panels,
            'energy': energy_info,
            'suitability': self._rate_suitability(rooftop, len(panels), obstacle_count)
        }
    
    def _detect_obstacles(self, image: np.ndarray, roof_mask: np.ndarray) -> np.ndarray:
        """
        Detect obstacles on the roof (chimneys, vents, AC units, skylights).
        
        Uses multiple detection methods:
        1. Very dark spots (shadows/chimneys)
        2. Very bright spots (skylights/reflective surfaces)
        3. High contrast regions (equipment)
        4. Internal contours (structural features)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        obstacle_mask = np.zeros_like(gray)
        
        # Only analyze within roof region
        roof_region = cv2.bitwise_and(gray, gray, mask=roof_mask)
        
        # Get intensity statistics within roof
        roof_pixels = gray[roof_mask > 0]
        if len(roof_pixels) == 0:
            return obstacle_mask
        
        mean_intensity = np.mean(roof_pixels)
        std_intensity = np.std(roof_pixels)
        
        # Method 1: Detect very dark spots (chimneys, vents)
        dark_threshold = max(20, mean_intensity - 2 * std_intensity)
        _, dark_spots = cv2.threshold(roof_region, dark_threshold, 255, cv2.THRESH_BINARY_INV)
        dark_spots = cv2.bitwise_and(dark_spots, roof_mask)
        
        # Method 2: Detect very bright spots (skylights, metal surfaces)
        bright_threshold = min(235, mean_intensity + 2 * std_intensity)
        _, bright_spots = cv2.threshold(roof_region, bright_threshold, 255, cv2.THRESH_BINARY)
        bright_spots = cv2.bitwise_and(bright_spots, roof_mask)
        
        # Method 3: Find internal contours (holes/features inside the roof)
        contours, hierarchy = cv2.findContours(roof_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        internal_mask = np.zeros_like(gray)
        if hierarchy is not None:
            for i, h in enumerate(hierarchy[0]):
                # h[3] is parent index - if it has a parent, it's internal
                if h[3] != -1:
                    area = cv2.contourArea(contours[i])
                    if 10 < area < 500:  # Small internal features
                        cv2.drawContours(internal_mask, [contours[i]], -1, 255, -1)
        
        # Combine all obstacle detections
        obstacle_mask = cv2.bitwise_or(dark_spots, bright_spots)
        obstacle_mask = cv2.bitwise_or(obstacle_mask, internal_mask)
        
        # Clean up: remove tiny noise and expand obstacle regions slightly
        kernel_small = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        obstacle_mask = cv2.morphologyEx(obstacle_mask, cv2.MORPH_OPEN, kernel_small)
        
        # Expand obstacles slightly for safety margin
        kernel_expand = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        obstacle_mask = cv2.dilate(obstacle_mask, kernel_expand, iterations=1)
        
        return obstacle_mask
    
    def _count_obstacles(self, obstacle_mask: np.ndarray) -> int:
        """Count distinct obstacle regions"""
        contours, _ = cv2.findContours(obstacle_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return len([c for c in contours if cv2.contourArea(c) > 10])
    
    def _place_panels_optimized(self, usable_mask: np.ndarray, roof_angle: float,
                                 roof_contour: np.ndarray) -> List[Dict]:
        """
        Place solar panels with optimization for irregular roofs.
        
        Tries both portrait and landscape orientations and picks the better one.
        Uses point-in-contour testing for irregular shapes.
        """
        # Try landscape orientation (width > height)
        panels_landscape = self._place_panels_with_orientation(
            usable_mask, self.panel_width_px, self.panel_height_px, roof_angle, roof_contour
        )
        
        # Try portrait orientation (height > width)
        panels_portrait = self._place_panels_with_orientation(
            usable_mask, self.panel_height_px, self.panel_width_px, roof_angle, roof_contour
        )
        
        # Choose the orientation that fits more panels
        if len(panels_landscape) >= len(panels_portrait):
            return panels_landscape
        else:
            return panels_portrait
    
    def _place_panels_with_orientation(self, usable_mask: np.ndarray, 
                                        panel_w: int, panel_h: int,
                                        roof_angle: float, roof_contour: np.ndarray) -> List[Dict]:
        """Place panels with specific orientation"""
        panels = []
        h, w = usable_mask.shape
        
        spacing = max(1, int(self.config['panel_spacing_m'] / self.config['pixel_to_meter']))
        step_x = panel_w + spacing
        step_y = panel_h + spacing
        
        panel_id = 1
        
        # Create a working copy to mark placed panels
        available = usable_mask.copy()
        
        for y in range(0, h - panel_h, step_y):
            for x in range(0, w - panel_w, step_x):
                # Check if panel fits in usable area
                panel_region = available[y:y + panel_h, x:x + panel_w]
                if panel_region.size == 0:
                    continue
                
                # Calculate coverage - what percentage of panel is in usable area
                coverage = np.sum(panel_region > 0) / panel_region.size
                
                # For irregular roofs, also check if center and corners are inside
                center_x, center_y = x + panel_w // 2, y + panel_h // 2
                corners_valid = self._check_corners_in_contour(
                    x, y, panel_w, panel_h, roof_contour
                )
                
                # Panel must have 90% coverage AND corners inside for irregular roofs
                if coverage > 0.90 and corners_valid:
                    panel = self._create_panel_geometry(
                        panel_id, x, y, panel_w, panel_h, roof_angle
                    )
                    panels.append(panel)
                    panel_id += 1
                    
                    # Mark this area as used (prevents overlapping)
                    available[y:y + panel_h, x:x + panel_w] = 0
        
        return panels
    
    def _check_corners_in_contour(self, x: int, y: int, w: int, h: int, 
                                   contour: np.ndarray) -> bool:
        """Check if panel corners are inside the roof contour"""
        corners = [
            (x + w // 4, y + h // 4),       # inner top-left
            (x + 3 * w // 4, y + h // 4),   # inner top-right
            (x + w // 4, y + 3 * h // 4),   # inner bottom-left
            (x + 3 * w // 4, y + 3 * h // 4) # inner bottom-right
        ]
        
        valid_count = 0
        for cx, cy in corners:
            result = cv2.pointPolygonTest(contour, (float(cx), float(cy)), False)
            if result >= 0:  # Inside or on edge
                valid_count += 1
        
        # At least 3 of 4 corner checks must pass
        return valid_count >= 3
    
    def _create_panel_geometry(self, panel_id: int, x: int, y: int, 
                                width: int, height: int, angle: float) -> Dict:
        """
        Create complete geometry for a single panel.
        
        Returns dictionary with center, corners, dimensions, and rotation.
        """
        # Calculate center
        center_x = x + width / 2
        center_y = y + height / 2
        
        # Calculate corners (before rotation)
        corners_local = [
            (x, y),                    # top-left
            (x + width, y),            # top-right  
            (x + width, y + height),   # bottom-right
            (x, y + height)            # bottom-left
        ]
        
        # Apply rotation around center
        angle_rad = math.radians(angle)
        corners_rotated = []
        for cx, cy in corners_local:
            # Translate to origin
            dx = cx - center_x
            dy = cy - center_y
            # Rotate
            rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
            ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
            # Translate back
            corners_rotated.append({
                'x': round(center_x + rx, 2),
                'y': round(center_y + ry, 2)
            })
        
        return {
            'panel_id': panel_id,
            'center': {
                'x': round(center_x, 2),
                'y': round(center_y, 2)
            },
            'corners': corners_rotated,
            'rotation_degrees': round(angle, 2),
            'dimensions_pixels': {
                'width': width,
                'height': height
            },
            'dimensions_meters': {
                'width': round(width * self.config['pixel_to_meter'], 2),
                'height': round(height * self.config['pixel_to_meter'], 2)
            }
        }
    
    def _calculate_energy(self, num_panels: int) -> Dict:
        """Calculate energy production estimates"""
        panel_area_m2 = self.config['panel_width_m'] * self.config['panel_height_m']
        total_area_m2 = num_panels * panel_area_m2
        capacity_kw = (num_panels * self.config['panel_power_w']) / 1000
        
        # Estimate annual irradiance based on latitude
        lat = self.config['latitude']
        base_irradiance = 2200 - abs(lat) * 8  # kWh/m²/year
        
        # Annual energy = Area × Irradiance × Efficiency × (1 - system losses)
        annual_kwh = total_area_m2 * base_irradiance * self.config['panel_efficiency'] * 0.86
        
        return {
            'system_capacity_kw': round(capacity_kw, 2),
            'total_panel_area_m2': round(total_area_m2, 2),
            'estimated_annual_kwh': round(annual_kwh, 0),
            'estimated_monthly_kwh': round(annual_kwh / 12, 0),
            'estimated_daily_kwh': round(annual_kwh / 365, 1),
            'co2_offset_kg_year': round(annual_kwh * 0.82, 0)
        }
    
    def _rate_suitability(self, rooftop: Dict, num_panels: int, obstacle_count: int) -> Dict:
        """Rate the suitability of the rooftop for solar"""
        score = 0
        
        # Area score (0-35 points)
        area = rooftop['area_m2']
        if area >= 50:
            score += 35
        elif area >= 30:
            score += 25
        elif area >= 20:
            score += 15
        
        # Panel count score (0-35 points)
        if num_panels >= 10:
            score += 35
        elif num_panels >= 5:
            score += 25
        elif num_panels >= 2:
            score += 15
        
        # Shape score (0-15 points) - more rectangular is better
        rect = rooftop['bounding_rect']
        aspect_ratio = rect['width'] / rect['height'] if rect['height'] > 0 else 1
        if 0.8 <= aspect_ratio <= 1.5:
            score += 15
        elif 0.5 <= aspect_ratio <= 2.0:
            score += 10
        
        # Obstacle penalty (0-15 points deduction)
        if obstacle_count == 0:
            score += 15
        elif obstacle_count <= 2:
            score += 10
        elif obstacle_count <= 5:
            score += 5
        # More than 5 obstacles: no bonus
        
        if score >= 80:
            rating = 'Excellent'
        elif score >= 60:
            rating = 'Good'
        elif score >= 40:
            rating = 'Fair'
        else:
            rating = 'Poor'
        
        return {
            'score': score,
            'rating': rating,
            'max_score': 100,
            'obstacles_found': obstacle_count
        }


# ============================================================================
# VISUALIZATION
# ============================================================================

class ResultVisualizer:
    """Visualizes solar panel analysis results"""
    
    def __init__(self, config: Dict = None):
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        
        # Color scheme
        self.colors = {
            'Excellent': (0, 255, 0),    # Green
            'Good': (0, 255, 255),       # Yellow (BGR)
            'Fair': (0, 165, 255),       # Orange
            'Poor': (0, 0, 255)          # Red
        }
    
    def draw_results(self, image: np.ndarray, analyses: List[Dict]) -> np.ndarray:
        """Draw analysis results on image"""
        output = image.copy()
        
        for analysis in analyses:
            rating = analysis['suitability']['rating']
            color = self.colors.get(rating, (128, 128, 128))
            
            # Draw panels
            for panel in analysis['panels']:
                pts = np.array([[c['x'], c['y']] for c in panel['corners']], dtype=np.int32)
                cv2.fillPoly(output, [pts], (255, 200, 0))  # Light blue fill
                cv2.polylines(output, [pts], True, (0, 100, 255), 2)  # Orange outline
            
            # Draw rooftop label
            center = analysis['panels'][0]['center'] if analysis['panels'] else {'x': 100, 'y': 50}
            label = f"#{analysis['rooftop_id']}: {analysis['panel_count']} panels"
            cv2.putText(output, label, 
                       (int(center['x']) - 40, int(center['y']) - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return output
    
    def create_summary_image(self, image: np.ndarray, analyses: List[Dict]) -> np.ndarray:
        """Create summary visualization with legend"""
        annotated = self.draw_results(image, analyses)
        
        # Add summary text
        h, w = annotated.shape[:2]
        summary_height = 120
        summary = np.zeros((summary_height, w, 3), dtype=np.uint8)
        summary[:] = (40, 40, 40)  # Dark gray background
        
        # Stats
        total_panels = sum(a['panel_count'] for a in analyses)
        total_kwh = sum(a['energy']['estimated_annual_kwh'] for a in analyses)
        total_capacity = sum(a['energy']['system_capacity_kw'] for a in analyses)
        
        y_offset = 25
        cv2.putText(summary, f"SOLAR ANALYSIS SUMMARY", (10, y_offset), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        y_offset += 30
        cv2.putText(summary, f"Rooftops: {len(analyses)}  |  Panels: {total_panels}  |  " +
                   f"Capacity: {total_capacity:.1f} kW  |  Annual Energy: {total_kwh:.0f} kWh", 
                   (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
        
        # Legend
        y_offset += 35
        x_offset = 10
        for rating, color in self.colors.items():
            cv2.rectangle(summary, (x_offset, y_offset - 12), (x_offset + 15, y_offset + 3), color, -1)
            cv2.putText(summary, rating, (x_offset + 20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
            x_offset += 100
        
        return np.vstack([annotated, summary])


# ============================================================================
# MAIN ANALYSIS FUNCTION
# ============================================================================

def analyze_image(image_path: str, config: Dict = None, output_dir: str = 'output') -> Dict:
    """
    Main entry point: Analyze a satellite/rooftop image for solar panel placement.
    
    Args:
        image_path: Path to the input image
        config: Optional configuration dictionary
        output_dir: Directory to save results
        
    Returns:
        Dictionary containing complete analysis results with panel geometries
    """
    config = {**DEFAULT_CONFIG, **(config or {})}
    
    # Validate input
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    print(f"\n{'='*60}")
    print(f"🌞 SOLAR PANEL PLACEMENT ANALYZER")
    print(f"{'='*60}")
    print(f"📂 Input: {image_path}")
    
    # Load image
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Could not load image: {image_path}")
    
    h, w = image.shape[:2]
    print(f"📐 Image size: {w}x{h} pixels")
    
    # Step 1: Detect rooftops
    print(f"\n🔍 Detecting rooftops...")
    detector = RooftopDetector(config)
    rooftops = detector.detect_rooftops(image)
    print(f"   Found {len(rooftops)} rooftop(s)")
    
    if len(rooftops) == 0:
        print("❌ No rooftops detected!")
        return {'success': False, 'error': 'No rooftops detected', 'analyses': []}
    
    # Step 2: Analyze each rooftop
    print(f"\n⚡ Analyzing solar potential...")
    optimizer = SolarPanelOptimizer(config)
    analyses = []
    
    for rooftop in rooftops:
        analysis = optimizer.analyze_rooftop(image, rooftop)
        analyses.append(analysis)
        print(f"   Rooftop #{rooftop['id']}: {analysis['panel_count']} panels, "
              f"{analysis['suitability']['rating']} rating")
    
    # Step 3: Create visualizations
    print(f"\n🎨 Creating visualizations...")
    os.makedirs(output_dir, exist_ok=True)
    
    visualizer = ResultVisualizer(config)
    result_image = visualizer.create_summary_image(image, analyses)
    
    # Save outputs
    base_name = Path(image_path).stem
    output_image_path = os.path.join(output_dir, f"{base_name}_analysis.png")
    output_json_path = os.path.join(output_dir, f"{base_name}_panels.json")
    
    cv2.imwrite(output_image_path, result_image)
    print(f"   ✅ Saved: {output_image_path}")
    
    # Prepare JSON output (remove non-serializable contours)
    json_output = {
        'timestamp': datetime.now().isoformat(),
        'input_image': image_path,
        'image_size': {'width': w, 'height': h},
        'config': {k: v for k, v in config.items() if not callable(v)},
        'summary': {
            'rooftop_count': len(analyses),
            'total_panels': sum(a['panel_count'] for a in analyses),
            'total_capacity_kw': sum(a['energy']['system_capacity_kw'] for a in analyses),
            'total_annual_kwh': sum(a['energy']['estimated_annual_kwh'] for a in analyses)
        },
        'rooftops': analyses
    }
    
    with open(output_json_path, 'w') as f:
        json.dump(json_output, f, indent=2, default=str)
    print(f"   ✅ Saved: {output_json_path}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 ANALYSIS COMPLETE")
    print(f"{'='*60}")
    total_panels = sum(a['panel_count'] for a in analyses)
    total_kwh = sum(a['energy']['estimated_annual_kwh'] for a in analyses)
    total_kw = sum(a['energy']['system_capacity_kw'] for a in analyses)
    
    print(f"   Total panels:     {total_panels}")
    print(f"   System capacity:  {total_kw:.1f} kW")
    print(f"   Annual energy:    {total_kwh:.0f} kWh/year")
    print(f"   Monthly average:  {total_kwh/12:.0f} kWh/month")
    print(f"   CO₂ offset:       {total_kwh * 0.82:.0f} kg/year")
    
    print(f"\n📂 Results saved to: {output_dir}/")
    
    return {
        'success': True,
        'output_image': output_image_path,
        'output_json': output_json_path,
        'analyses': analyses
    }


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Analyze satellite/rooftop images for optimal solar panel placement',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python analyze_rooftop.py testcases/1.jpg
    python analyze_rooftop.py testcases/5.jpg --output-dir results
    python analyze_rooftop.py path/to/image.png --lat 40.7128 --lon -74.0060
        """
    )
    
    parser.add_argument('image', help='Path to the satellite/rooftop image')
    parser.add_argument('--output-dir', '-o', default='output', 
                       help='Output directory for results (default: output)')
    parser.add_argument('--lat', type=float, default=28.6139,
                       help='Latitude for solar calculations (default: 28.6139 - Delhi)')
    parser.add_argument('--lon', type=float, default=77.2090,
                       help='Longitude (default: 77.2090)')
    parser.add_argument('--pixel-to-meter', '-p', type=float, default=0.15,
                       help='Meters per pixel (default: 0.15)')
    
    args = parser.parse_args()
    
    config = {
        'latitude': args.lat,
        'longitude': args.lon,
        'pixel_to_meter': args.pixel_to_meter
    }
    
    try:
        result = analyze_image(args.image, config, args.output_dir)
        if not result['success']:
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

// API Response Types
export interface PanelCorner {
    x: number;
    y: number;
}

export interface Panel {
    panel_id: number;
    center: { x: number; y: number };
    corners: PanelCorner[];
    rotation_degrees: number;
    dimensions_pixels: { width: number; height: number };
    dimensions_meters: { width: number; height: number };
}

export interface EnergyInfo {
    system_capacity_kw: number;
    total_panel_area_m2: number;
    estimated_annual_kwh: number;
    estimated_monthly_kwh: number;
    estimated_daily_kwh: number;
    co2_offset_kg_year: number;
}

export interface Suitability {
    score: number;
    rating: 'Excellent' | 'Good' | 'Fair' | 'Poor';
    max_score: number;
    obstacles_found: number;
}

export interface RooftopAnalysis {
    rooftop_id: number;
    roof_area_m2: number;
    usable_area_m2: number;
    roof_orientation_degrees: number;
    obstacles_detected: number;
    panel_count: number;
    panels: Panel[];
    energy: EnergyInfo;
    suitability: Suitability;
}

export interface AnalysisResult {
    success: boolean;
    error?: string;
    output_image?: string;
    output_json?: string;
    analysis_image_url?: string;
    uploaded_image_url?: string;
    total_panels?: number;
    total_capacity_kw?: number;
    total_annual_kwh?: number;
    total_co2_offset?: number;
    analyses?: RooftopAnalysis[];
}

import type { AnalysisResult, RooftopAnalysis } from '../types';
import StatsGrid from './StatsGrid';

interface ResultsSectionProps {
    result: AnalysisResult;
    onNewAnalysis: () => void;
}

function ResultsSection({ result, onNewAnalysis }: ResultsSectionProps) {
    const analyses = result.analyses || [];
    const bestRating = analyses.length > 0
        ? analyses.reduce((best, curr) =>
            curr.suitability.score > best.suitability.score ? curr : best
        ).suitability
        : null;

    const handleDownload = () => {
        if (result.analysis_image_url) {
            const link = document.createElement('a');
            link.href = result.analysis_image_url;
            link.download = 'solar_analysis.png';
            link.click();
        }
    };

    return (
        <section className="results-section">
            <h2 className="section-title">Analysis Results</h2>

            {/* Stats Grid */}
            <StatsGrid
                panels={result.total_panels || 0}
                capacityKw={result.total_capacity_kw || 0}
                annualKwh={result.total_annual_kwh || 0}
                co2Offset={result.total_co2_offset || 0}
            />

            {/* Analysis Image */}
            <div className="analysis-container">
                <div className="analysis-header">
                    <h3>Panel Placement Visualization</h3>
                    {bestRating && (
                        <div className={`rating-badge ${bestRating.rating.toLowerCase()}`}>
                            <span className="rating-score">{bestRating.score}</span>
                            <span className="rating-label">{bestRating.rating}</span>
                        </div>
                    )}
                </div>
                <div className="analysis-image-wrapper">
                    {result.analysis_image_url && (
                        <img src={result.analysis_image_url} alt="Solar panel analysis" />
                    )}
                </div>
            </div>

            {/* Rooftop Details */}
            {analyses.length > 0 && (
                <>
                    <h2 className="section-title">Rooftop Details</h2>
                    <div className="rooftop-cards">
                        {analyses.map((analysis: RooftopAnalysis) => (
                            <RooftopCard key={analysis.rooftop_id} analysis={analysis} />
                        ))}
                    </div>
                </>
            )}

            {/* Actions */}
            <div className="actions">
                <button className="btn btn-secondary" onClick={onNewAnalysis}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" />
                        <line x1="12" y1="3" x2="12" y2="15" />
                    </svg>
                    Analyze New Image
                </button>
                <button className="btn btn-primary" onClick={handleDownload}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="7 10 12 15 17 10" />
                        <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                    Download Analysis
                </button>
            </div>
        </section>
    );
}

interface RooftopCardProps {
    analysis: RooftopAnalysis;
}

function RooftopCard({ analysis }: RooftopCardProps) {
    return (
        <div className="rooftop-card">
            <h4>
                Rooftop #{analysis.rooftop_id}
                <span className={analysis.suitability.rating.toLowerCase()}>
                    {analysis.suitability.rating}
                </span>
            </h4>
            <div className="rooftop-stats">
                <div className="rooftop-stat">
                    <span className="rooftop-stat-value">{analysis.panel_count}</span>
                    <span className="rooftop-stat-label">Panels</span>
                </div>
                <div className="rooftop-stat">
                    <span className="rooftop-stat-value">{analysis.roof_area_m2.toFixed(1)} m²</span>
                    <span className="rooftop-stat-label">Roof Area</span>
                </div>
                <div className="rooftop-stat">
                    <span className="rooftop-stat-value">{analysis.usable_area_m2.toFixed(1)} m²</span>
                    <span className="rooftop-stat-label">Usable Area</span>
                </div>
                <div className="rooftop-stat">
                    <span className="rooftop-stat-value">{analysis.obstacles_detected}</span>
                    <span className="rooftop-stat-label">Obstacles</span>
                </div>
                <div className="rooftop-stat">
                    <span className="rooftop-stat-value">{analysis.energy.system_capacity_kw} kW</span>
                    <span className="rooftop-stat-label">Capacity</span>
                </div>
                <div className="rooftop-stat">
                    <span className="rooftop-stat-value">{analysis.energy.estimated_daily_kwh} kWh</span>
                    <span className="rooftop-stat-label">Daily Energy</span>
                </div>
            </div>
        </div>
    );
}

export default ResultsSection;

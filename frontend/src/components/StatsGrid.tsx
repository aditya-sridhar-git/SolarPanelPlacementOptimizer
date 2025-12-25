import AnimatedCounter from './AnimatedCounter';

interface StatsGridProps {
    panels: number;
    capacityKw: number;
    annualKwh: number;
    co2Offset: number;
}

function StatsGrid({ panels, capacityKw, annualKwh, co2Offset }: StatsGridProps) {
    return (
        <div className="stats-grid">
            {/* Panels */}
            <div className="stat-card panels">
                <div className="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" />
                        <line x1="3" y1="9" x2="21" y2="9" />
                        <line x1="3" y1="15" x2="21" y2="15" />
                        <line x1="9" y1="3" x2="9" y2="21" />
                        <line x1="15" y1="3" x2="15" y2="21" />
                    </svg>
                </div>
                <div>
                    <span className="stat-value">
                        <AnimatedCounter value={panels} />
                    </span>
                    <span className="stat-label">Solar Panels</span>
                </div>
            </div>

            {/* Capacity */}
            <div className="stat-card capacity">
                <div className="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                    </svg>
                </div>
                <div>
                    <span className="stat-value">
                        <AnimatedCounter value={capacityKw} decimals={1} /> <small>kW</small>
                    </span>
                    <span className="stat-label">System Capacity</span>
                </div>
            </div>

            {/* Annual Energy */}
            <div className="stat-card energy">
                <div className="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="12" cy="12" r="10" />
                        <polyline points="12 6 12 12 16 14" />
                    </svg>
                </div>
                <div>
                    <span className="stat-value">
                        <AnimatedCounter value={annualKwh} /> <small>kWh/yr</small>
                    </span>
                    <span className="stat-label">Annual Energy</span>
                </div>
            </div>

            {/* CO2 Offset */}
            <div className="stat-card co2">
                <div className="stat-icon">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z" />
                        <path d="M7 12.5c1-2.5 6-2.5 7 0" />
                        <circle cx="8.5" cy="9" r="0.5" fill="currentColor" />
                        <circle cx="15.5" cy="9" r="0.5" fill="currentColor" />
                    </svg>
                </div>
                <div>
                    <span className="stat-value">
                        <AnimatedCounter value={co2Offset} /> <small>kg/yr</small>
                    </span>
                    <span className="stat-label">CO₂ Offset</span>
                </div>
            </div>
        </div>
    );
}

export default StatsGrid;

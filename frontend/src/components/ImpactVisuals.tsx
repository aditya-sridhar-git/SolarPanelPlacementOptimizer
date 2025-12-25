import AnimatedCounter from './AnimatedCounter';

interface ImpactVisualsProps {
    annualKwh: number;
    co2Offset: number;
}

function ImpactVisuals({ annualKwh, co2Offset }: ImpactVisualsProps) {
    // Calculate environmental equivalents
    const treesEquivalent = Math.round(co2Offset / 21); // ~21kg CO2 per tree per year
    const carsOffRoad = Math.round(co2Offset / 4600); // ~4600kg CO2 per car per year
    const homesEnergy = Math.round(annualKwh / 10500 * 100) / 100; // ~10,500 kWh per home
    const phoneCharges = Math.round(annualKwh / 0.012); // ~0.012 kWh per phone charge
    const coffeeBrews = Math.round(annualKwh / 0.3); // ~0.3 kWh per coffee brew

    return (
        <div className="impact-section">
            <h2 className="section-title">Environmental Impact</h2>
            <p className="impact-subtitle">Your solar installation's positive contribution</p>

            <div className="impact-grid">
                {/* Trees */}
                <div className="impact-card trees">
                    <div className="impact-visual">
                        <div className="tree-forest">
                            {Array.from({ length: Math.min(treesEquivalent, 10) }).map((_, i) => (
                                <span key={i} className="tree" style={{ animationDelay: `${i * 0.1}s` }}>🌳</span>
                            ))}
                        </div>
                    </div>
                    <div className="impact-data">
                        <span className="impact-value">
                            <AnimatedCounter value={treesEquivalent} />
                        </span>
                        <span className="impact-label">Trees planted equivalent</span>
                    </div>
                </div>

                {/* Cars */}
                <div className="impact-card cars">
                    <div className="impact-visual">
                        <div className="car-animation">
                            <span className="car">🚗</span>
                            <span className="smoke">💨</span>
                            <span className="no-symbol">🚫</span>
                        </div>
                    </div>
                    <div className="impact-data">
                        <span className="impact-value">
                            <AnimatedCounter value={carsOffRoad} decimals={1} />
                        </span>
                        <span className="impact-label">Cars taken off the road (yearly)</span>
                    </div>
                </div>

                {/* Homes */}
                <div className="impact-card homes">
                    <div className="impact-visual">
                        <div className="home-power">
                            <span className="home">🏠</span>
                            <span className="lightning">⚡</span>
                        </div>
                    </div>
                    <div className="impact-data">
                        <span className="impact-value">
                            <AnimatedCounter value={homesEnergy} decimals={2} />
                        </span>
                        <span className="impact-label">Homes powered for a year</span>
                    </div>
                </div>

                {/* Fun facts */}
                <div className="impact-card fun">
                    <div className="impact-visual">
                        <div className="fun-icons">
                            <span>📱</span>
                            <span>☕</span>
                        </div>
                    </div>
                    <div className="impact-data">
                        <span className="impact-value">
                            <AnimatedCounter value={phoneCharges} />
                        </span>
                        <span className="impact-label">Phone charges OR</span>
                        <span className="impact-value secondary">
                            <AnimatedCounter value={coffeeBrews} />
                        </span>
                        <span className="impact-label">Cups of coffee brewed</span>
                    </div>
                </div>
            </div>

            {/* Animated energy flow */}
            <div className="energy-flow">
                <div className="flow-line">
                    <span className="flow-sun">☀️</span>
                    <div className="flow-path">
                        <span className="flow-particle" style={{ animationDelay: '0s' }} />
                        <span className="flow-particle" style={{ animationDelay: '0.3s' }} />
                        <span className="flow-particle" style={{ animationDelay: '0.6s' }} />
                    </div>
                    <span className="flow-panel">🔋</span>
                    <div className="flow-path">
                        <span className="flow-particle" style={{ animationDelay: '0.15s' }} />
                        <span className="flow-particle" style={{ animationDelay: '0.45s' }} />
                        <span className="flow-particle" style={{ animationDelay: '0.75s' }} />
                    </div>
                    <span className="flow-home">🏠</span>
                </div>
                <span className="flow-label">Clean energy powering your life</span>
            </div>
        </div>
    );
}

export default ImpactVisuals;

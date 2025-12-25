import { useEffect, useRef } from 'react';

function HeroSection() {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const resize = () => {
            canvas.width = canvas.offsetWidth * window.devicePixelRatio;
            canvas.height = canvas.offsetHeight * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        };
        resize();
        window.addEventListener('resize', resize);

        // Particles
        const particles: { x: number; y: number; vx: number; vy: number; size: number; alpha: number }[] = [];
        for (let i = 0; i < 50; i++) {
            particles.push({
                x: Math.random() * canvas.offsetWidth,
                y: Math.random() * canvas.offsetHeight,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 3 + 1,
                alpha: Math.random() * 0.5 + 0.2,
            });
        }

        let animationId: number;
        const animate = () => {
            ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);

            particles.forEach((p) => {
                p.x += p.vx;
                p.y += p.vy;

                if (p.x < 0) p.x = canvas.offsetWidth;
                if (p.x > canvas.offsetWidth) p.x = 0;
                if (p.y < 0) p.y = canvas.offsetHeight;
                if (p.y > canvas.offsetHeight) p.y = 0;

                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(245, 158, 11, ${p.alpha})`;
                ctx.fill();
            });

            animationId = requestAnimationFrame(animate);
        };
        animate();

        return () => {
            window.removeEventListener('resize', resize);
            cancelAnimationFrame(animationId);
        };
    }, []);

    return (
        <section className="hero-section">
            <canvas ref={canvasRef} className="hero-particles" />

            <div className="hero-content">
                <div className="hero-badge">
                    <span className="pulse-dot" />
                    AI-Powered Analysis
                </div>

                <h1 className="hero-title">
                    <span className="gradient-text">Maximize Your</span>
                    <br />
                    <span className="highlight">Solar Potential</span>
                </h1>

                <p className="hero-description">
                    Upload a satellite image of your rooftop and let our AI calculate
                    the optimal solar panel placement, energy production, and environmental impact.
                </p>

                <div className="hero-stats">
                    <div className="hero-stat">
                        <span className="hero-stat-value">500+</span>
                        <span className="hero-stat-label">Rooftops Analyzed</span>
                    </div>
                    <div className="hero-stat">
                        <span className="hero-stat-value">98%</span>
                        <span className="hero-stat-label">Accuracy Rate</span>
                    </div>
                    <div className="hero-stat">
                        <span className="hero-stat-value">5MW+</span>
                        <span className="hero-stat-label">Capacity Planned</span>
                    </div>
                </div>
            </div>

            <div className="hero-visual">
                <div className="sun-animation">
                    <div className="sun-core" />
                    <div className="sun-ray ray-1" />
                    <div className="sun-ray ray-2" />
                    <div className="sun-ray ray-3" />
                    <div className="sun-ray ray-4" />
                    <div className="sun-ray ray-5" />
                    <div className="sun-ray ray-6" />
                    <div className="sun-ray ray-7" />
                    <div className="sun-ray ray-8" />
                </div>
                <div className="orbit orbit-1">
                    <div className="orbit-panel" />
                </div>
                <div className="orbit orbit-2">
                    <div className="orbit-panel" />
                </div>
            </div>
        </section>
    );
}

export default HeroSection;

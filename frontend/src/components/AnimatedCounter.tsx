import { useEffect, useRef } from 'react';

interface AnimatedCounterProps {
    value: number;
    duration?: number;
    decimals?: number;
}

function AnimatedCounter({ value, duration = 1000, decimals = 0 }: AnimatedCounterProps) {
    const counterRef = useRef<HTMLSpanElement>(null);
    const startRef = useRef<number | null>(null);
    const frameRef = useRef<number | null>(null);

    useEffect(() => {
        const startValue = 0;
        const endValue = value;

        const animate = (timestamp: number) => {
            if (startRef.current === null) {
                startRef.current = timestamp;
            }

            const progress = Math.min((timestamp - startRef.current) / duration, 1);
            const easeProgress = 1 - Math.pow(1 - progress, 3); // Ease out cubic
            const currentValue = startValue + (endValue - startValue) * easeProgress;

            if (counterRef.current) {
                counterRef.current.textContent = currentValue.toLocaleString('en-US', {
                    minimumFractionDigits: decimals,
                    maximumFractionDigits: decimals,
                });
            }

            if (progress < 1) {
                frameRef.current = requestAnimationFrame(animate);
            }
        };

        startRef.current = null;
        frameRef.current = requestAnimationFrame(animate);

        return () => {
            if (frameRef.current) {
                cancelAnimationFrame(frameRef.current);
            }
        };
    }, [value, duration, decimals]);

    return <span ref={counterRef}>0</span>;
}

export default AnimatedCounter;

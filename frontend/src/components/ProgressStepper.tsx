interface ProgressStepperProps {
    currentStep: number;
}

const STEPS = [
    { id: 1, label: 'Upload Image', icon: '📤' },
    { id: 2, label: 'Detect Rooftop', icon: '🏠' },
    { id: 3, label: 'Find Obstacles', icon: '🔍' },
    { id: 4, label: 'Place Panels', icon: '☀️' },
    { id: 5, label: 'Calculate Energy', icon: '⚡' },
];

function ProgressStepper({ currentStep }: ProgressStepperProps) {
    return (
        <div className="progress-stepper">
            <div className="stepper-track">
                <div
                    className="stepper-progress"
                    style={{ width: `${((currentStep - 1) / (STEPS.length - 1)) * 100}%` }}
                />
            </div>
            <div className="stepper-steps">
                {STEPS.map((step) => (
                    <div
                        key={step.id}
                        className={`stepper-step ${step.id < currentStep ? 'completed' : ''} ${step.id === currentStep ? 'active' : ''}`}
                    >
                        <div className="step-icon">
                            {step.id < currentStep ? (
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                                    <polyline points="20 6 9 17 4 12" />
                                </svg>
                            ) : (
                                <span>{step.icon}</span>
                            )}
                        </div>
                        <span className="step-label">{step.label}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ProgressStepper;

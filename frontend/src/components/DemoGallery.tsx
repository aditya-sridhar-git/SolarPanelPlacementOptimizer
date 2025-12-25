interface DemoGalleryProps {
    onSelectDemo: (imagePath: string) => void;
}

interface DemoImage {
    id: number;
    name: string;
    path: string;
    description: string;
    works: boolean;
    panelCount?: number;
    note: string;
    icon: 'house' | 'building' | 'warehouse' | 'apartment' | 'office' | 'school';
    color: string;
}

// Verified testcase images with detection status
const DEMO_IMAGES: DemoImage[] = [
    {
        id: 1,
        name: 'Residential Home',
        path: '/testcases/1.jpg',
        description: 'Single family house',
        works: true,
        panelCount: 25,
        note: '25 panels detected',
        icon: 'house',
        color: '#10b981'
    },
    {
        id: 5,
        name: 'Large Building',
        path: '/testcases/5.jpg',
        description: 'Commercial property',
        works: true,
        panelCount: 50,
        note: '~50 panels detected',
        icon: 'building',
        color: '#3b82f6'
    },
    {
        id: 9,
        name: 'Warehouse',
        path: '/testcases/9.jpg',
        description: 'Industrial facility',
        works: true,
        panelCount: 30,
        note: '~30 panels detected',
        icon: 'warehouse',
        color: '#8b5cf6'
    },
    {
        id: 3,
        name: 'Small Roof',
        path: '/testcases/3.jpg',
        description: 'Compact structure',
        works: true,
        panelCount: 15,
        note: '~15 panels detected',
        icon: 'apartment',
        color: '#06b6d4'
    },
    {
        id: 21,
        name: 'Satellite View',
        path: '/testcases/21.jpg',
        description: 'Raw satellite image',
        works: false,
        note: 'Detection may vary',
        icon: 'office',
        color: '#f59e0b'
    },
    {
        id: 15,
        name: 'Complex Shape',
        path: '/testcases/15.jpg',
        description: 'Irregular rooftop',
        works: false,
        note: 'Detection may fail',
        icon: 'school',
        color: '#ef4444'
    },
];

const Icons = {
    house: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
            <polyline points="9 22 9 12 15 12 15 22" />
        </svg>
    ),
    building: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="4" y="2" width="16" height="20" rx="2" />
            <line x1="9" y1="6" x2="9" y2="6.01" />
            <line x1="15" y1="6" x2="15" y2="6.01" />
            <line x1="9" y1="10" x2="9" y2="10.01" />
            <line x1="15" y1="10" x2="15" y2="10.01" />
            <line x1="9" y1="14" x2="9" y2="14.01" />
            <line x1="15" y1="14" x2="15" y2="14.01" />
            <path d="M9 18h6v4H9z" />
        </svg>
    ),
    warehouse: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M22 8.35V20a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V8.35A2 2 0 0 1 3.26 6.5l8-3.2a2 2 0 0 1 1.48 0l8 3.2A2 2 0 0 1 22 8.35Z" />
            <path d="M6 18h4" />
            <path d="M14 18h4" />
            <path d="M6 14h4" />
            <path d="M14 14h4" />
        </svg>
    ),
    apartment: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <rect x="2" y="6" width="8" height="16" rx="1" />
            <rect x="14" y="2" width="8" height="20" rx="1" />
            <line x1="5" y1="10" x2="7" y2="10" />
            <line x1="5" y1="14" x2="7" y2="14" />
            <line x1="17" y1="6" x2="19" y2="6" />
            <line x1="17" y1="10" x2="19" y2="10" />
            <line x1="17" y1="14" x2="19" y2="14" />
        </svg>
    ),
    office: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <circle cx="12" cy="12" r="10" />
            <path d="M2 12h20" />
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
        </svg>
    ),
    school: (
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            <line x1="12" y1="6" x2="12" y2="10" />
            <line x1="10" y1="8" x2="14" y2="8" />
        </svg>
    ),
};

function DemoGallery({ onSelectDemo }: DemoGalleryProps) {
    return (
        <div className="demo-gallery">
            <div className="demo-header">
                <span className="demo-label">✨ Try a Demo</span>
                <h3>No image? Try one of our samples</h3>
                <p className="demo-note">
                    <span className="badge-works">✓ Works</span> = Rooftop detected &nbsp;&nbsp;
                    <span className="badge-varies">? May vary</span> = Detection depends on image
                </p>
            </div>
            <div className="demo-grid">
                {DEMO_IMAGES.map((demo) => (
                    <button
                        key={demo.id}
                        className={`demo-card ${demo.works ? 'verified' : 'experimental'}`}
                        onClick={() => onSelectDemo(demo.path)}
                    >
                        <div className="demo-icon-wrapper" style={{ background: `linear-gradient(135deg, ${demo.color}22, ${demo.color}44)` }}>
                            <div className="demo-icon" style={{ color: demo.color }}>
                                {Icons[demo.icon]}
                            </div>
                            <div className="demo-play-overlay">
                                <svg viewBox="0 0 24 24" fill="currentColor">
                                    <polygon points="10 8 16 12 10 16 10 8" />
                                </svg>
                            </div>
                            <span className={`demo-status ${demo.works ? 'works' : 'varies'}`}>
                                {demo.works ? '✓' : '?'}
                            </span>
                        </div>
                        <div className="demo-info">
                            <span className="demo-name">{demo.name}</span>
                            <span className="demo-desc">{demo.description}</span>
                            <span className={`demo-badge ${demo.works ? 'success' : 'warning'}`}>
                                {demo.note}
                            </span>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
}

export default DemoGallery;

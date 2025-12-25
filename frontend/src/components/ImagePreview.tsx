interface ImagePreviewProps {
    previewUrl: string;
    isAnalyzing: boolean;
    onAnalyze: () => void;
    onChangeImage: () => void;
}

function ImagePreview({ previewUrl, isAnalyzing, onAnalyze, onChangeImage }: ImagePreviewProps) {
    return (
        <div className="preview-container">
            <img src={previewUrl} alt="Selected rooftop" className="preview-image" />
            <div className="preview-actions">
                <button className="btn btn-secondary" onClick={onChangeImage} disabled={isAnalyzing}>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" />
                        <line x1="12" y1="3" x2="12" y2="15" />
                    </svg>
                    Change Image
                </button>
                <button className="btn btn-primary" onClick={onAnalyze} disabled={isAnalyzing}>
                    {isAnalyzing ? (
                        <>
                            <svg className="spinner" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                                <circle cx="12" cy="12" r="10" strokeDasharray="31.42" strokeLinecap="round" />
                            </svg>
                            Analyzing...
                        </>
                    ) : (
                        <>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <circle cx="12" cy="12" r="5" />
                                <line x1="12" y1="1" x2="12" y2="3" />
                                <line x1="12" y1="21" x2="12" y2="23" />
                                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                            </svg>
                            Analyze Rooftop
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}

export default ImagePreview;

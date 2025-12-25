import { useState, useCallback, useEffect } from 'react';
import './App.css';
import type { AnalysisResult } from './types';
import HeroSection from './components/HeroSection';
import UploadZone from './components/UploadZone';
import DemoGallery from './components/DemoGallery';
import ImagePreview from './components/ImagePreview';
import ProgressStepper from './components/ProgressStepper';
import ResultsSection from './components/ResultsSection';
import ImpactVisuals from './components/ImpactVisuals';
import Toast from './components/Toast';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStep, setAnalysisStep] = useState(0);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showHero, setShowHero] = useState(true);

  const handleFileSelect = useCallback((file: File) => {
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
    setError(null);
    setShowHero(false);
  }, []);

  const handleDemoSelect = useCallback(async (imagePath: string) => {
    try {
      const response = await fetch(imagePath);
      const blob = await response.blob();
      const file = new File([blob], imagePath.split('/').pop() || 'demo.jpg', { type: blob.type });
      handleFileSelect(file);
    } catch (err) {
      setError('Failed to load demo image');
    }
  }, [handleFileSelect]);

  const handleAnalyze = useCallback(async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setAnalysisStep(1);
    setError(null);

    // Simulate progress steps
    const stepInterval = setInterval(() => {
      setAnalysisStep((prev) => Math.min(prev + 1, 5));
    }, 800);

    try {
      const formData = new FormData();
      formData.append('image', selectedFile);

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      const data: AnalysisResult = await response.json();

      clearInterval(stepInterval);
      setAnalysisStep(5);

      if (data.success) {
        setTimeout(() => {
          setResult(data);
          setAnalysisStep(0);
        }, 500);
      } else {
        setError(data.error || 'Analysis failed');
        setAnalysisStep(0);
      }
    } catch (err) {
      clearInterval(stepInterval);
      setError(err instanceof Error ? err.message : 'Failed to connect to server');
      setAnalysisStep(0);
    } finally {
      setIsAnalyzing(false);
    }
  }, [selectedFile]);

  const handleReset = useCallback(() => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
    setError(null);
    setAnalysisStep(0);
    setShowHero(true);
  }, []);

  // Scroll to top on result
  useEffect(() => {
    if (result) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }, [result]);

  return (
    <>
      <div className="bg-animation" />

      <div className="container">
        {/* Header */}
        <header className="header">
          <div className="sun-icon" onClick={handleReset} style={{ cursor: 'pointer' }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="5" />
              <line x1="12" y1="1" x2="12" y2="3" />
              <line x1="12" y1="21" x2="12" y2="23" />
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
              <line x1="1" y1="12" x2="3" y2="12" />
              <line x1="21" y1="12" x2="23" y2="12" />
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
            </svg>
          </div>
          <div>
            <h1>Solar Panel Optimizer</h1>
            <p>AI-Powered Rooftop Analysis</p>
          </div>
        </header>

        {/* Hero Section */}
        {showHero && !result && <HeroSection />}

        {/* Upload Section */}
        {!result && (
          <section className="upload-section">
            {!previewUrl ? (
              <>
                <UploadZone onFileSelect={handleFileSelect} />
                <DemoGallery onSelectDemo={handleDemoSelect} />
              </>
            ) : (
              <>
                <ImagePreview
                  previewUrl={previewUrl}
                  isAnalyzing={isAnalyzing}
                  onAnalyze={handleAnalyze}
                  onChangeImage={handleReset}
                />
                {analysisStep > 0 && <ProgressStepper currentStep={analysisStep} />}
              </>
            )}
          </section>
        )}

        {/* Results Section */}
        {result && (
          <>
            <ResultsSection
              result={result}
              onNewAnalysis={handleReset}
            />
            {result.total_annual_kwh && result.total_co2_offset && (
              <ImpactVisuals
                annualKwh={result.total_annual_kwh}
                co2Offset={result.total_co2_offset}
              />
            )}
          </>
        )}

        {/* Footer */}
        <footer className="footer">
          <p>🌞 Powered by AI • Helping the planet one rooftop at a time</p>
        </footer>
      </div>

      {/* Error Toast */}
      <Toast message={error} onClose={() => setError(null)} />
    </>
  );
}

export default App;

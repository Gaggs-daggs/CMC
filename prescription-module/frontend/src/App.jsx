import { useState } from 'react'
import './App.css'
import PrescriptionUpload from './components/PrescriptionUpload'
import MedicineCard from './components/MedicineCard'
import AnalysisPanel from './components/AnalysisPanel'
import QAChat from './components/QAChat'
import ScheduleTimeline from './components/ScheduleTimeline'

const LOADING_STEPS = [
    { label: 'Reading prescription image...', icon: '📷' },
    { label: 'Extracting medicine details...', icon: '🔍' },
    { label: 'Analyzing side effects & benefits...', icon: '💊' },
    { label: 'Checking drug interactions...', icon: '⚠️' },
    { label: 'Generating health advice...', icon: '💡' },
]

export default function App() {
    const [view, setView] = useState('upload') // upload | loading | results
    const [result, setResult] = useState(null)
    const [selectedMedicine, setSelectedMedicine] = useState(0)
    const [loadingStep, setLoadingStep] = useState(0)
    const [error, setError] = useState(null)

    const handleUpload = async (file) => {
        setView('loading')
        setLoadingStep(0)
        setError(null)

        // Simulate loading progression
        const stepInterval = setInterval(() => {
            setLoadingStep(prev => {
                if (prev < LOADING_STEPS.length - 1) return prev + 1
                return prev
            })
        }, 3000)

        try {
            const formData = new FormData()
            formData.append('file', file)

            const res = await fetch('/api/v1/prescription/upload', {
                method: 'POST',
                body: formData,
            })

            if (!res.ok) {
                throw new Error('Backend OCR failed')
            }

            const data = await res.json()

            // Check if Gemini actually extracted medicines
            if (data.prescription?.medicines?.length > 0) {
                clearInterval(stepInterval)
                setResult(data)
                setSelectedMedicine(0)
                setView('results')
                return
            }

            // Gemini returned empty — try Puter fallback
            throw new Error('No medicines extracted by Gemini')

        } catch (backendErr) {
            console.warn('Backend OCR failed, trying Puter fallback...', backendErr.message)

            // --- PUTER OCR FALLBACK ---
            try {
                setLoadingStep(1) // "Extracting medicine details..."

                // Convert file to data URL for Puter
                const dataUrl = await new Promise((resolve) => {
                    const reader = new FileReader()
                    reader.onload = () => resolve(reader.result)
                    reader.readAsDataURL(file)
                })

                // Call Puter OCR (client-side, free, no API key)
                const rawText = await window.puter.ai.img2txt(dataUrl)
                console.log('Puter OCR result:', rawText)

                if (!rawText || rawText.trim().length < 10) {
                    throw new Error('Puter OCR returned empty or too short text')
                }

                setLoadingStep(2) // "Analyzing side effects..."

                // Send raw text to backend for medicine parsing + analysis
                const textRes = await fetch('/api/v1/prescription/analyze-text', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ raw_text: rawText }),
                })

                clearInterval(stepInterval)

                if (!textRes.ok) {
                    const errData = await textRes.json().catch(() => ({}))
                    throw new Error(errData.detail || 'Text analysis failed')
                }

                const data = await textRes.json()
                setResult(data)
                setSelectedMedicine(0)
                setView('results')

            } catch (puterErr) {
                clearInterval(stepInterval)
                console.error('Puter fallback also failed:', puterErr)
                setError(
                    'Both AI services failed. ' + puterErr.message +
                    ' Please try again or upload a clearer image.'
                )
                setView('upload')
            }
            return
        }
    }

    const handleNewUpload = () => {
        setView('upload')
        setResult(null)
        setSelectedMedicine(0)
        setError(null)
    }

    return (
        <div className="app">
            {/* Header */}
            <header className="app-header">
                <div className="app-logo">
                    <div className="app-logo-icon">💊</div>
                    <div>
                        <h1>CMC Health</h1>
                        <span>Prescription Manager</span>
                    </div>
                </div>
                <div className="app-nav">
                    {view === 'results' && (
                        <button className="nav-btn" onClick={handleNewUpload}>
                            + New Upload
                        </button>
                    )}
                </div>
            </header>

            {/* Main Content */}
            <main className="app-main">
                {/* Error Toast */}
                {error && (
                    <div className="error-toast" onClick={() => setError(null)}>
                        ❌ {error}
                    </div>
                )}

                {/* Upload View */}
                {view === 'upload' && (
                    <PrescriptionUpload onUpload={handleUpload} isLoading={false} />
                )}

                {/* Loading View */}
                {view === 'loading' && (
                    <div className="loading-state">
                        <div className="loading-spinner" />
                        <h3 style={{ marginBottom: 8 }}>Analyzing Your Prescription</h3>
                        <p style={{ color: 'var(--text-dim)', marginBottom: 24 }}>
                            Our AI is reading and analyzing every medicine...
                        </p>
                        <div className="loading-steps">
                            {LOADING_STEPS.map((step, i) => (
                                <div
                                    key={i}
                                    className={`loading-step ${i === loadingStep ? 'active' : ''} ${i < loadingStep ? 'done' : ''}`}
                                >
                                    <span className="loading-step-icon">
                                        {i < loadingStep ? '✅' : step.icon}
                                    </span>
                                    <span>{step.label}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Results View */}
                {view === 'results' && result && (
                    <div className="results-section">
                        <div className="results-header">
                            <h2>🩺 Prescription Analysis</h2>
                        </div>

                        {/* Prescription Metadata */}
                        <div className="prescription-meta">
                            {result.prescription.doctor_name && (
                                <div className="meta-chip">
                                    <span>👨‍⚕️</span>
                                    <span className="label">Doctor:</span>
                                    <span>{result.prescription.doctor_name}</span>
                                </div>
                            )}
                            {result.prescription.patient_name && (
                                <div className="meta-chip">
                                    <span>👤</span>
                                    <span className="label">Patient:</span>
                                    <span>{result.prescription.patient_name}</span>
                                </div>
                            )}
                            {result.prescription.date && (
                                <div className="meta-chip">
                                    <span>📅</span>
                                    <span className="label">Date:</span>
                                    <span>{result.prescription.date}</span>
                                </div>
                            )}
                            {result.prescription.diagnosis && (
                                <div className="meta-chip">
                                    <span>🏥</span>
                                    <span className="label">Diagnosis:</span>
                                    <span>{result.prescription.diagnosis}</span>
                                </div>
                            )}
                            <div className="meta-chip">
                                <span>💊</span>
                                <span className="label">Medicines:</span>
                                <span>{result.prescription.medicines?.length || 0}</span>
                            </div>
                        </div>

                        {/* Overall Advice */}
                        {result.overall_advice && (
                            <div className="advice-box">
                                <h3>💡 Health Advisor</h3>
                                <p>{result.overall_advice}</p>
                            </div>
                        )}

                        {/* Medicine Cards + Analysis Panel */}
                        {result.prescription.medicines?.length > 0 && (
                            <div className="results-grid">
                                <div>
                                    <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, color: 'var(--text-dim)' }}>
                                        MEDICINES ({result.prescription.medicines.length})
                                    </h3>
                                    {result.prescription.medicines.map((med, i) => (
                                        <div key={i} style={{ marginBottom: 12 }}>
                                            <MedicineCard
                                                medicine={med}
                                                analysis={result.medicine_analyses?.[i]}
                                                index={i}
                                                isSelected={selectedMedicine === i}
                                                onClick={() => setSelectedMedicine(i)}
                                            />
                                        </div>
                                    ))}
                                </div>
                                <div>
                                    <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16, color: 'var(--text-dim)' }}>
                                        DETAILED ANALYSIS
                                    </h3>
                                    <AnalysisPanel analysis={result.medicine_analyses?.[selectedMedicine]} />
                                </div>
                            </div>
                        )}

                        {/* Drug Interactions */}
                        {result.drug_interactions?.length > 0 && (
                            <div className="interactions-section">
                                <h3>⚠️ Drug Interactions</h3>
                                {result.drug_interactions.map((inter, i) => (
                                    <div key={i} className={`interaction-card ${inter.severity}`}>
                                        <div className="interaction-drugs">
                                            {inter.drug_a} ↔ {inter.drug_b}
                                            <span className={`tag tag-${inter.severity === 'severe' ? 'danger' : inter.severity === 'moderate' ? 'warning' : 'info'}`}
                                                style={{ marginLeft: 8 }}>
                                                {inter.severity}
                                            </span>
                                        </div>
                                        <div className="interaction-desc">{inter.description}</div>
                                        {inter.recommendation && (
                                            <div className="interaction-rec">💡 {inter.recommendation}</div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}

                        {/* Schedule Timeline */}
                        <ScheduleTimeline medicines={result.prescription.medicines} />

                        {/* Q&A Chat */}
                        <QAChat prescriptionId={result.prescription.prescription_id} />
                    </div>
                )}
            </main>
        </div>
    )
}

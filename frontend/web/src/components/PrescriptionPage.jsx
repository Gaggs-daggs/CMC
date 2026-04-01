import { useState, useRef, useEffect } from 'react'
import atlasLogo from '../assets/atlas-logo.png'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const LOADING_STEPS = [
  { label: 'Reading prescription image...', icon: '📷' },
  { label: 'Extracting medicine details...', icon: '🔍' },
  { label: 'Analyzing side effects & benefits...', icon: '💊' },
  { label: 'Checking drug interactions...', icon: '⚠️' },
  { label: 'Generating health advice...', icon: '💡' },
]

/* ─── Sub-components ─── */

function PrescriptionUpload({ onUpload, isLoading }) {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)
  const dragCounter = useRef(0)

  const handleFile = (f) => {
    if (!f || !f.type.startsWith('image/')) return
    setFile(f)
    const reader = new FileReader()
    reader.onload = (e) => setPreview(e.target.result)
    reader.readAsDataURL(f)
  }

  const handleDragEnter = (e) => {
    e.preventDefault()
    e.stopPropagation()
    dragCounter.current++
    setDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    e.stopPropagation()
    dragCounter.current--
    if (dragCounter.current === 0) setDragging(false)
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    e.stopPropagation()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setDragging(false)
    dragCounter.current = 0
    const f = e.dataTransfer?.files?.[0]
    if (f) handleFile(f)
  }

  return (
    <div className="rx-upload-section">
      <h2>📋 Upload Your Prescription</h2>
      <p>Take a photo or upload an image of your prescription — our AI will analyze every medicine for you.</p>
      <div
        className={`rx-upload-zone ${dragging ? 'dragging' : ''}`}
        onClick={() => !file && inputRef.current?.click()}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input ref={inputRef} type="file" accept="image/*" style={{ display: 'none' }} onChange={(e) => handleFile(e.target.files[0])} />
        {!preview ? (
          <>
            <div className="rx-upload-icon">📷</div>
            <div className="rx-upload-text">
              <h3>Drop your prescription here</h3>
              <p>or <span className="rx-accent">click to browse</span></p>
              <p>Supports JPEG, PNG • Max 10MB</p>
            </div>
          </>
        ) : (
          <div className="rx-upload-preview">
            <img src={preview} alt="Prescription preview" />
            <div className="rx-file-name">{file.name} ({(file.size / 1024).toFixed(0)} KB)</div>
          </div>
        )}
      </div>
      {preview && (
        <div className="rx-upload-actions">
          <button className="rx-btn-secondary" onClick={() => { setFile(null); setPreview(null); if (inputRef.current) inputRef.current.value = '' }} disabled={isLoading}>✕ Clear</button>
          <button className="rx-btn-primary" onClick={() => file && !isLoading && onUpload(file)} disabled={isLoading}>{isLoading ? '⏳ Analyzing...' : '🔍 Analyze Prescription'}</button>
        </div>
      )}
    </div>
  )
}

function MedicineCard({ medicine, analysis, index, isSelected, onClick }) {
  return (
    <div className={`rx-medicine-card ${isSelected ? 'selected' : ''}`} style={{ animationDelay: `${index * 0.1}s` }} onClick={onClick}>
      <div className="rx-medicine-card-header">
        <span className="rx-medicine-name">{medicine.name}</span>
        {medicine.dosage && <span className="rx-medicine-dosage">{medicine.dosage}</span>}
      </div>
      <div className="rx-medicine-details">
        {medicine.frequency && <div className="rx-medicine-detail"><span>🔄</span><span>{medicine.frequency}</span></div>}
        {medicine.duration && <div className="rx-medicine-detail"><span>📅</span><span>{medicine.duration}</span></div>}
        {medicine.timing && <div className="rx-medicine-detail"><span>⏰</span><span>{medicine.timing}</span></div>}
        {medicine.instructions && <div className="rx-medicine-detail"><span>📝</span><span>{medicine.instructions}</span></div>}
      </div>
      {analysis?.purpose && <p style={{ marginTop: 12, fontSize: 13, color: 'rgba(255,255,255,0.5)', lineHeight: 1.5 }}>{analysis.purpose}</p>}
    </div>
  )
}

function AnalysisPanel({ analysis }) {
  if (!analysis) return (
    <div className="rx-analysis-panel"><div className="rx-empty-state"><div style={{ fontSize: 48 }}>👈</div><p>Select a medicine to see detailed analysis</p></div></div>
  )

  return (
    <div className="rx-analysis-panel">
      <h3>💊 {analysis.medicine_name}</h3>
      {analysis.purpose && <div className="rx-analysis-section"><div className="rx-analysis-title">Purpose</div><p>{analysis.purpose}</p></div>}
      {analysis.how_it_works && <div className="rx-analysis-section"><div className="rx-analysis-title">How It Works</div><p>{analysis.how_it_works}</p></div>}
      {analysis.benefits?.length > 0 && <div className="rx-analysis-section"><div className="rx-analysis-title">✅ Benefits</div><div className="rx-tags">{analysis.benefits.map((b, i) => <span key={i} className="rx-tag rx-tag-success">{b}</span>)}</div></div>}
      {analysis.common_side_effects?.length > 0 && <div className="rx-analysis-section"><div className="rx-analysis-title">⚠️ Common Side Effects</div><div className="rx-tags">{analysis.common_side_effects.map((s, i) => <span key={i} className="rx-tag rx-tag-warning">{s}</span>)}</div></div>}
      {analysis.serious_side_effects?.length > 0 && <div className="rx-analysis-section"><div className="rx-analysis-title">🚨 Serious Side Effects</div><div className="rx-tags">{analysis.serious_side_effects.map((s, i) => <span key={i} className="rx-tag rx-tag-danger">{s}</span>)}</div></div>}
      {analysis.precautions?.length > 0 && <div className="rx-analysis-section"><div className="rx-analysis-title">⚡ Precautions</div><div className="rx-tags">{analysis.precautions.map((p, i) => <span key={i} className="rx-tag rx-tag-info">{p}</span>)}</div></div>}
      {analysis.food_interactions && <div className="rx-analysis-section"><div className="rx-analysis-title">🍽️ Food Interactions</div><p>{analysis.food_interactions}</p></div>}
      {analysis.contraindications?.length > 0 && <div className="rx-analysis-section"><div className="rx-analysis-title">🚫 Contraindications</div><div className="rx-tags">{analysis.contraindications.map((c, i) => <span key={i} className="rx-tag rx-tag-danger">{c}</span>)}</div></div>}
    </div>
  )
}

function ScheduleTimeline({ medicines }) {
  if (!medicines?.length) return null
  const parseTimings = (med) => {
    const freq = (med.frequency || '').toLowerCase()
    const timing = (med.timing || '').toLowerCase()
    if (freq.includes('once') || freq.includes('1')) return [timing.includes('night') || timing.includes('evening') ? '🌙 Night' : '🌅 Morning']
    if (freq.includes('twice') || freq.includes('2')) return ['🌅 Morning', '🌙 Night']
    if (freq.includes('thrice') || freq.includes('three') || freq.includes('3')) return ['🌅 Morning', '☀️ Afternoon', '🌙 Night']
    if (freq.includes('four') || freq.includes('4')) return ['🌅 Morning', '☀️ Noon', '🌇 Evening', '🌙 Night']
    return ['💊 As prescribed']
  }
  return (
    <div className="rx-schedule-section">
      <h3>📅 Medication Schedule</h3>
      <div className="rx-schedule-grid">
        {medicines.map((med, i) => (
          <div key={i} className="rx-schedule-card" style={{ animationDelay: `${i * 0.1}s` }}>
            <div className="rx-schedule-med-name">{med.name}</div>
            <div className="rx-schedule-info">{med.dosage}{med.dosage && med.duration && ' • '}{med.duration}</div>
            {med.instructions && <div className="rx-schedule-info" style={{ fontStyle: 'italic', opacity: 0.6 }}>{med.instructions}</div>}
            <div className="rx-schedule-timing">{parseTimings(med).map((t, j) => <span key={j} className="rx-timing-badge">{t}</span>)}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

function QAChat({ prescriptionId }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const send = async () => {
    const q = input.trim()
    if (!q || loading) return
    setInput('')
    setMessages(p => [...p, { role: 'user', content: q }])
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/prescription/${prescriptionId}/ask`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question: q }) })
      if (!res.ok) throw new Error('Failed')
      const data = await res.json()
      setMessages(p => [...p, { role: 'assistant', content: data.answer }])
    } catch { setMessages(p => [...p, { role: 'assistant', content: "Sorry, I couldn't process your question. Please try again." }]) }
    finally { setLoading(false) }
  }

  const suggestions = ['Can I take these with food?', 'What should I avoid?', 'Any serious side effects?', 'Can I stop early if I feel better?']

  return (
    <div className="rx-qa-section">
      <h3>💬 Ask About Your Prescription</h3>
      <div className="rx-chat-container">
        <div className="rx-chat-messages">
          {messages.length === 0 && (
            <div className="rx-empty-state" style={{ padding: '24px 0' }}>
              <div style={{ fontSize: 48 }}>🤖</div>
              <p style={{ marginBottom: 16 }}>Ask me anything about your medicines</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, justifyContent: 'center' }}>
                {suggestions.map((s, i) => <button key={i} className="rx-btn-secondary" style={{ fontSize: 12, padding: '6px 12px' }} onClick={() => setInput(s)}>{s}</button>)}
              </div>
            </div>
          )}
          {messages.map((msg, i) => (
            <div key={i} className={`rx-chat-message ${msg.role}`}>
              <div className="rx-chat-avatar">{msg.role === 'user' ? '👤' : '🤖'}</div>
              <div className="rx-chat-bubble">{msg.content}</div>
            </div>
          ))}
          {loading && <div className="rx-chat-message assistant"><div className="rx-chat-avatar">🤖</div><div className="rx-chat-bubble" style={{ opacity: 0.6 }}>Thinking...</div></div>}
          <div ref={endRef} />
        </div>
        <div className="rx-chat-input-area">
          <input className="rx-chat-input" type="text" placeholder="Ask about side effects, dosage, interactions..." value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), send())} disabled={loading} />
          <button className="rx-chat-send-btn" onClick={send} disabled={!input.trim() || loading}>Send</button>
        </div>
      </div>
    </div>
  )
}

/* ─── Main Page Component ─── */

export default function PrescriptionPage({ onBack }) {
  const [view, setView] = useState('upload') // upload | loading | results
  const [result, setResult] = useState(null)
  const [selectedMedicine, setSelectedMedicine] = useState(0)
  const [loadingStep, setLoadingStep] = useState(0)
  const [error, setError] = useState(null)

  const handleUpload = async (file) => {
    setView('loading')
    setLoadingStep(0)
    setError(null)

    const stepInterval = setInterval(() => {
      setLoadingStep(prev => prev < LOADING_STEPS.length - 1 ? prev + 1 : prev)
    }, 3000)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${API_BASE}/prescription/upload`, { method: 'POST', body: formData })
      clearInterval(stepInterval)

      if (!res.ok) {
        const errBody = await res.text()
        throw new Error(`Upload failed (${res.status}): ${errBody}`)
      }

      const data = await res.json()

      if (data.prescription?.medicines?.length > 0) {
        setResult(data)
        setSelectedMedicine(0)
        setView('results')
        return
      }

      // Gemini read the image but found no medicines — still show whatever was extracted
      if (data.prescription?.raw_text || data.prescription?.doctor_name) {
        setResult(data)
        setSelectedMedicine(0)
        setView('results')
        setError('No medicines were detected. The prescription may be unclear — check the raw text below.')
        return
      }

      throw new Error('Could not read prescription. Please upload a clearer image.')
    } catch (err) {
      clearInterval(stepInterval)
      console.error('Prescription upload error:', err)
      setError(err.message || 'Failed to analyze prescription. Please try again with a clearer image.')
      setView('upload')
    }
  }

  return (
    <div className="rx-page">
      {/* Header */}
      <header className="rx-header">
        <div className="rx-header-left">
          <button className="rx-back-btn" onClick={onBack}>← Back</button>
          <div className="rx-header-logo">
            <img src={atlasLogo} alt="Atlas" style={{ width: 32, height: 32, borderRadius: '50%', objectFit: 'cover' }} />
            <div>
              <h1>Prescription Analyzer</h1>
              <span>AI-Powered Medicine Analysis</span>
            </div>
          </div>
        </div>
        <div className="rx-header-right">
          {view === 'results' && <button className="rx-btn-secondary" onClick={() => { setView('upload'); setResult(null); setSelectedMedicine(0); setError(null) }}>+ New Upload</button>}
        </div>
      </header>

      {/* Main */}
      <main className="rx-main">
        {error && <div className="rx-error-toast" onClick={() => setError(null)}>❌ {error}</div>}

        {view === 'upload' && <PrescriptionUpload onUpload={handleUpload} isLoading={false} />}

        {view === 'loading' && (
          <div className="rx-loading-state">
            <div className="rx-loading-spinner" />
            <h3>Analyzing Your Prescription</h3>
            <p style={{ opacity: 0.5, marginBottom: 24 }}>Our AI is reading and analyzing every medicine...</p>
            <div className="rx-loading-steps">
              {LOADING_STEPS.map((step, i) => (
                <div key={i} className={`rx-loading-step ${i === loadingStep ? 'active' : ''} ${i < loadingStep ? 'done' : ''}`}>
                  <span>{i < loadingStep ? '✅' : step.icon}</span>
                  <span>{step.label}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {view === 'results' && result && (
          <div className="rx-results-section">
            <h2>🩺 Prescription Analysis</h2>

            {/* Metadata */}
            <div className="rx-meta">
              {result.prescription.doctor_name && <div className="rx-meta-chip"><span>👨‍⚕️</span><span className="rx-label">Doctor:</span>{result.prescription.doctor_name}</div>}
              {result.prescription.patient_name && <div className="rx-meta-chip"><span>👤</span><span className="rx-label">Patient:</span>{result.prescription.patient_name}</div>}
              {result.prescription.date && <div className="rx-meta-chip"><span>📅</span><span className="rx-label">Date:</span>{result.prescription.date}</div>}
              {result.prescription.diagnosis && <div className="rx-meta-chip"><span>🏥</span><span className="rx-label">Diagnosis:</span>{result.prescription.diagnosis}</div>}
              <div className="rx-meta-chip"><span>💊</span><span className="rx-label">Medicines:</span>{result.prescription.medicines?.length || 0}</div>
            </div>

            {/* Overall Advice */}
            {result.overall_advice && (
              <div className="rx-advice-box">
                <h3>💡 Health Advisor</h3>
                <p>{result.overall_advice}</p>
              </div>
            )}

            {/* Medicines + Analysis */}
            {result.prescription.medicines?.length > 0 && (
              <div className="rx-results-grid">
                <div>
                  <h3 className="rx-section-label">MEDICINES ({result.prescription.medicines.length})</h3>
                  {result.prescription.medicines.map((med, i) => (
                    <div key={i} style={{ marginBottom: 12 }}>
                      <MedicineCard medicine={med} analysis={result.medicine_analyses?.[i]} index={i} isSelected={selectedMedicine === i} onClick={() => setSelectedMedicine(i)} />
                    </div>
                  ))}
                </div>
                <div>
                  <h3 className="rx-section-label">DETAILED ANALYSIS</h3>
                  <AnalysisPanel analysis={result.medicine_analyses?.[selectedMedicine]} />
                </div>
              </div>
            )}

            {/* Drug Interactions */}
            {result.drug_interactions?.length > 0 && (
              <div className="rx-interactions-section">
                <h3>⚠️ Drug Interactions</h3>
                {result.drug_interactions.map((inter, i) => (
                  <div key={i} className={`rx-interaction-card ${inter.severity}`}>
                    <div className="rx-interaction-drugs">{inter.drug_a} ↔ {inter.drug_b} <span className={`rx-tag rx-tag-${inter.severity === 'severe' ? 'danger' : inter.severity === 'moderate' ? 'warning' : 'info'}`} style={{ marginLeft: 8 }}>{inter.severity}</span></div>
                    <div className="rx-interaction-desc">{inter.description}</div>
                    {inter.recommendation && <div className="rx-interaction-rec">💡 {inter.recommendation}</div>}
                  </div>
                ))}
              </div>
            )}

            <ScheduleTimeline medicines={result.prescription.medicines} />
            <QAChat prescriptionId={result.prescription.prescription_id} />
          </div>
        )}
      </main>
    </div>
  )
}

import { useState, useRef, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000/api/v1'
const STORAGE_KEY = 'cmc_health_session'

// All Indian Languages with native script names
const langNames = { 
  en: 'English',
  hi: 'हिंदी (Hindi)',
  ta: 'தமிழ் (Tamil)',
  te: 'తెలుగు (Telugu)',
  bn: 'বাংলা (Bengali)',
  mr: 'मराठी (Marathi)',
  gu: 'ગુજરાતી (Gujarati)',
  kn: 'ಕನ್ನಡ (Kannada)',
  ml: 'മലയാളം (Malayalam)',
  pa: 'ਪੰਜਾਬੀ (Punjabi)',
  or: 'ଓଡ଼ିଆ (Odia)',
  as: 'অসমীয়া (Assamese)',
  ur: 'اردو (Urdu)',
  ne: 'नेपाली (Nepali)'
}

const getSpeechLang = (lang) => {
  const m = { 
    en:'en-IN', hi:'hi-IN', ta:'ta-IN', te:'te-IN', bn:'bn-IN', kn:'kn-IN', 
    ml:'ml-IN', gu:'gu-IN', mr:'mr-IN', pa:'pa-IN', ur:'ur-IN', or:'or-IN',
    as:'as-IN', ne:'ne-NP'
  }
  return m[lang] || 'en-IN'
}

// Load session from localStorage
const loadSession = () => {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const data = JSON.parse(saved)
      if (data.messages) {
        data.messages = data.messages.map(m => ({ ...m, time: new Date(m.time) }))
      }
      return data
    }
  } catch (e) { console.error('Failed to load session:', e) }
  return null
}

// Save session to localStorage
const saveSession = (data) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } catch (e) { console.error('Failed to save session:', e) }
}

const detectLanguage = (text) => {
  if (!text) return 'en'
  if (/[\u0900-\u097F]/.test(text)) return 'hi'
  if (/[\u0B80-\u0BFF]/.test(text)) return 'ta'
  if (/[\u0C00-\u0C7F]/.test(text)) return 'te'
  if (/[\u0980-\u09FF]/.test(text)) return 'bn'
  if (/[\u0C80-\u0CFF]/.test(text)) return 'kn'
  if (/[\u0D00-\u0D7F]/.test(text)) return 'ml'
  if (/[\u0A80-\u0AFF]/.test(text)) return 'gu'
  return 'en'
}

const HeartIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
const MicIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
const SendIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
const VolumeIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14"/><path d="M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
const VolumeOffIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>
const ActivityIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
const UserIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
const BotIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="10" rx="2"/><circle cx="12" cy="5" r="2"/><path d="M12 7v4"/></svg>
const MessageIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
const AlertIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
const DownloadIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
const TrashIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
const PhoneIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
const XIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
const CameraIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>
const ImageIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
const PillIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.5 20.5L3.5 13.5a4.95 4.95 0 1 1 7-7l7 7a4.95 4.95 0 1 1-7 7z"/><line x1="8.5" y1="8.5" x2="15.5" y2="15.5"/></svg>
const ShieldIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
const HeartHandIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M12 5 9.04 7.96a2.17 2.17 0 0 0 0 3.08c.82.82 2.13.85 3 .07l2.07-1.9a2.82 2.82 0 0 1 3.79 0l2.96 2.66"/><path d="m18 15-2-2"/><path d="m15 18-2-2"/></svg>
const LifeBuoyIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/><line x1="4.93" y1="4.93" x2="9.17" y2="9.17"/><line x1="14.83" y1="14.83" x2="19.07" y2="19.07"/><line x1="14.83" y1="9.17" x2="19.07" y2="4.93"/><line x1="14.83" y1="9.17" x2="18.36" y2="5.64"/><line x1="4.93" y1="19.07" x2="9.17" y2="14.83"/></svg>
const ClipboardIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1" ry="1"/></svg>
const StethoscopeIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"/><path d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"/><circle cx="20" cy="10" r="2"/></svg>
const HeartPulseIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/><path d="M3.22 12H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/></svg>
const StopIcon = () => <svg viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>
const StopCircleIcon = () => <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><rect x="9" y="9" width="6" height="6" rx="1"/></svg>

// Format AI response with sections
const FormattedMessage = ({ text, triage, medications, mentalHealth }) => {
  // Check if text has structured sections
  const hasStructure = text.includes('**') || text.includes('Understanding') || text.includes('Treatment') || text.includes('Doctor') || text.includes('Empathy');
  
  if (!hasStructure) {
    // Simple text - just render with basic formatting
    return <div className="simple-message">{text}</div>;
  }
  
  // Parse sections from the response
  const sections = [];
  
  // Try to extract sections using regex
  const conditionMatch = text.match(/\*\*Understanding[^*]*\*\*([^*]*?)(?=\*\*|$)/is) || 
                         text.match(/Understanding Your Condition[^:]*:?\s*([^*]*?)(?=\*\*Treatment|Treatment|$)/is);
  const treatmentMatch = text.match(/\*\*Treatment[^*]*\*\*([^*]*?)(?=\*\*|$)/is) ||
                         text.match(/Treatment & Medications[^:]*:?\s*([^*]*?)(?=\*\*Doctor|Doctor|$)/is);
  const doctorMatch = text.match(/\*\*Doctor[^*]*\*\*([^*]*?)(?=\*\*|$)/is) ||
                      text.match(/Doctor Recommendation[^:]*:?\s*([^*]*?)(?=\*\*Empathy|Empathy|$)/is);
  const empathyMatch = text.match(/\*\*Empathy[^*]*\*\*([^*]*?)$/is) ||
                       text.match(/Empathy & Support[^:]*:?\s*([^*]*?)$/is);
  
  // Clean up extracted text
  const cleanText = (t) => t?.trim()
    .replace(/\*\*/g, '')
    .replace(/^[]\s*/gm, '')
    .trim();
  
  const condition = cleanText(conditionMatch?.[1]);
  const treatment = cleanText(treatmentMatch?.[1]);
  const doctor = cleanText(doctorMatch?.[1]);
  const empathy = cleanText(empathyMatch?.[1]);
  
  // If we couldn't parse sections, show formatted raw text
  if (!condition && !treatment && !doctor && !empathy) {
    return (
      <div className="formatted-message">
        {text.split('\n').map((line, i) => {
          if (line.startsWith('**') && line.endsWith('**')) {
            return <h4 key={i} className="msg-section-title">{line.replace(/\*\*/g, '')}</h4>;
          }
          if (line.startsWith('•') || line.startsWith('-')) {
            return <li key={i} className="msg-list-item">{line.replace(/^[•-]\s*/, '')}</li>;
          }
          if (line.trim()) {
            return <p key={i} className="msg-para">{line}</p>;
          }
          return null;
        })}
      </div>
    );
  }
  
  return (
    <div className="structured-response">
      {condition && (
        <div className="response-section condition-section">
          <div className="section-header">
            <ClipboardIcon />
            <h4>Understanding Your Condition</h4>
          </div>
          <div className="section-content">
            {condition.split('\n').filter(l => l.trim()).map((line, i) => (
              <p key={i}>{line.replace(/^[•-]\s*/, '• ')}</p>
            ))}
          </div>
        </div>
      )}
      
      {treatment && (
        <div className="response-section treatment-section">
          <div className="section-header">
            <PillIcon />
            <h4>Treatment & Medications</h4>
          </div>
          <div className="section-content">
            {treatment.split('\n').filter(l => l.trim()).map((line, i) => (
              <p key={i}>{line.replace(/^[•-]\s*/, '• ')}</p>
            ))}
          </div>
        </div>
      )}
      
      {/* Show OTC medications if available */}
      {medications?.length > 0 && (
        <div className="medications-inline">
          {medications.map((med, j) => (
            <div key={j} className="med-card">
              <div className="med-card-name">{med.name}</div>
              <div className="med-card-dosage">{med.dosage}</div>
              {med.warnings?.[0] && <div className="med-card-warning">⚠️ {med.warnings[0]}</div>}
            </div>
          ))}
        </div>
      )}
      
      {doctor && (
        <div className="response-section doctor-section">
          <div className="section-header">
            <StethoscopeIcon />
            <h4>Doctor Recommendation</h4>
          </div>
          <div className="section-content">
            {doctor.split('\n').filter(l => l.trim()).map((line, i) => (
              <p key={i}>{line.replace(/^[•-]\s*/, '• ')}</p>
            ))}
          </div>
        </div>
      )}
      
      {empathy && (
        <div className="response-section empathy-section">
          <div className="section-header">
            <HeartPulseIcon />
            <h4>Support & Care</h4>
          </div>
          <div className="section-content">
            {empathy.split('\n').filter(l => l.trim()).map((line, i) => (
              <p key={i}>{line}</p>
            ))}
          </div>
        </div>
      )}
      
      {/* Mental health resources */}
      {mentalHealth?.detected && mentalHealth.resources?.length > 0 && (
        <div className="response-section resources-section">
          <div className="section-header">
            <LifeBuoyIcon />
            <h4>Support Resources</h4>
          </div>
          <div className="helpline-cards">
            {mentalHealth.resources.slice(0, 2).map((res, i) => (
              <a key={i} href={`tel:${res.phone}`} className="helpline-card">
                <PhoneIcon />
                <div>
                  <div className="helpline-name">{res.name}</div>
                  <div className="helpline-number">{res.phone}</div>
                </div>
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default function App() {
  // Load saved session
  const savedSession = loadSession()
  
  const [view, setView] = useState(savedSession?.view || 'home')
  const [phone, setPhone] = useState(savedSession?.phone || '')
  const [language, setLanguage] = useState(savedSession?.language || 'en')
  const [detectedLang, setDetectedLang] = useState(savedSession?.detectedLang || 'en')
  const [sessionId, setSessionId] = useState(savedSession?.sessionId || '')
  const [messages, setMessages] = useState(savedSession?.messages || [])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [vitals, setVitals] = useState(savedSession?.vitals || null)
  const [isListening, setIsListening] = useState(false)
  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [connected, setConnected] = useState(true)
  const [showDisclaimer, setShowDisclaimer] = useState(!localStorage.getItem('cmc_disclaimer_accepted'))
  const [detectedSymptoms, setDetectedSymptoms] = useState(savedSession?.symptoms || [])
  const [urgencyLevel, setUrgencyLevel] = useState(savedSession?.urgency || 'low')
  const [showEmergency, setShowEmergency] = useState(false)
  const [showImageUpload, setShowImageUpload] = useState(false)
  const [imageAnalyzing, setImageAnalyzing] = useState(false)
  const [imageResult, setImageResult] = useState(null)
  const [selectedImage, setSelectedImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [suggestedMeds, setSuggestedMeds] = useState(savedSession?.medications || [])
  const [triageInfo, setTriageInfo] = useState(savedSession?.triage || null)
  const [mentalHealthInfo, setMentalHealthInfo] = useState(savedSession?.mentalHealth || null)
  const [showMentalHealthSupport, setShowMentalHealthSupport] = useState(false)
  const [showCrisisBanner, setShowCrisisBanner] = useState(false)
  
  const chatEndRef = useRef(null)
  const recognitionRef = useRef(null)
  const imageInputRef = useRef(null)
  const abortControllerRef = useRef(null)  // For cancelling API requests
  const audioRef = useRef(null)  // For TTS audio playback

  // Save session whenever state changes
  useEffect(() => {
    if (sessionId || messages.length > 0) {
      saveSession({ view, phone, language, detectedLang, sessionId, messages, vitals, symptoms: detectedSymptoms, urgency: urgencyLevel, triage: triageInfo, mentalHealth: mentalHealthInfo })
    }
  }, [view, phone, language, detectedLang, sessionId, messages, vitals, detectedSymptoms, urgencyLevel, triageInfo, mentalHealthInfo])

  // Check for emergency symptoms
  useEffect(() => {
    if (urgencyLevel === 'emergency') {
      setShowEmergency(true)
    }
  }, [urgencyLevel])

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SR()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = true
      recognitionRef.current.lang = getSpeechLang(detectedLang)
      recognitionRef.current.onresult = (e) => {
        const t = Array.from(e.results).map(r => r[0].transcript).join('')
        setInput(t)
        const d = detectLanguage(t)
        if (d !== detectedLang) setDetectedLang(d)
        if (e.results[0].isFinal) setIsListening(false)
      }
      recognitionRef.current.onerror = () => setIsListening(false)
      recognitionRef.current.onend = () => setIsListening(false)
    }
  }, [detectedLang])

  useEffect(() => { chatEndRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const speak = async (text) => {
    if (!voiceEnabled || !text) return
    // Stop any current audio
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    window.speechSynthesis.cancel()
    
    const lang = detectedLang || detectLanguage(text)
    const clean = text.replace(/\*\*/g,'').replace(/[\u{1F300}-\u{1F9FF}]/gu,'').replace(/\n+/g,'. ').trim()
    if (!clean) return
    
    setIsSpeaking(true)
    
    try {
      // Use backend Edge TTS for high-quality neural voices
      const res = await fetch(`${API_BASE}/tts/speak`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: clean, language: lang, slow: false })
      })
      
      if (!res.ok) throw new Error('TTS failed')
      
      const audioBlob = await res.blob()
      const audioUrl = URL.createObjectURL(audioBlob)
      
      const audio = new Audio(audioUrl)
      audioRef.current = audio
      
      audio.onended = () => {
        setIsSpeaking(false)
        URL.revokeObjectURL(audioUrl)
        audioRef.current = null
      }
      audio.onerror = () => {
        setIsSpeaking(false)
        URL.revokeObjectURL(audioUrl)
        audioRef.current = null
        // Fallback to browser TTS
        fallbackSpeak(clean, lang)
      }
      
      await audio.play()
    } catch (e) {
      console.error('Backend TTS error, using fallback:', e)
      // Fallback to browser SpeechSynthesis
      fallbackSpeak(clean, lang)
    }
  }
  
  // Fallback to browser TTS if backend fails
  const fallbackSpeak = (clean, lang) => {
    const doSpeak = () => {
      const u = new SpeechSynthesisUtterance(clean)
      u.lang = getSpeechLang(lang)
      u.rate = 0.85
      const voices = window.speechSynthesis.getVoices()
      const v = voices.find(x => x.lang.startsWith(lang)) || voices[0]
      if (v) u.voice = v
      u.onstart = () => setIsSpeaking(true)
      u.onend = () => setIsSpeaking(false)
      u.onerror = () => setIsSpeaking(false)
      window.speechSynthesis.speak(u)
    }
    if (window.speechSynthesis.getVoices().length === 0) {
      window.speechSynthesis.onvoiceschanged = doSpeak
    } else doSpeak()
  }

  const stopSpeaking = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current = null
    }
    window.speechSynthesis.cancel()
    setIsSpeaking(false)
  }

  const toggleListening = () => {
    if (!recognitionRef.current) { alert('Speech not supported'); return }
    if (isListening) { recognitionRef.current.stop(); setIsListening(false) }
    else { recognitionRef.current.start(); setIsListening(true) }
  }

  const startChat = async () => {
    if (!phone.trim()) return alert('Enter phone number')
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/conversation/start`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: phone, language })
      })
      const data = await res.json()
      setSessionId(data.session_id)
      setMessages([{ role: 'assistant', text: data.greeting, time: new Date() }])
      setView('chat')
      setConnected(true)
      setTimeout(() => speak(data.greeting), 500)
    } catch (e) { setConnected(false); alert('Server offline') }
    setLoading(false)
  }

  const sendMsg = async (override) => {
    const msg = override || input
    if (!msg.trim() || loading) return
    // Use the selected language from dropdown for translation output
    // Auto-detect is only for display, but we use the selected language setting
    const msgLang = detectLanguage(msg)
    if (msgLang !== 'en' && msgLang !== detectedLang) setDetectedLang(msgLang)
    
    // Use the USER-SELECTED language (detectedLang) for response translation
    // This ensures the response comes in the language the user chose
    const outputLang = detectedLang || language || 'en'
    
    setInput('')
    setMessages(m => [...m, { role: 'user', text: msg, time: new Date() }])
    setLoading(true)
    
    // Create AbortController for this request
    abortControllerRef.current = new AbortController()
    
    try {
      const res = await fetch(`${API_BASE}/conversation/message`, {
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: msg, language: outputLang }),
        signal: abortControllerRef.current.signal
      })
      const data = await res.json()
      
      // Handle session not found - start new session
      if (data.detail === 'Session not found') {
        // Clear old session and prompt to restart
        localStorage.removeItem(STORAGE_KEY)
        setMessages(m => [...m, { role: 'assistant', text: 'Session expired. Please refresh and start a new chat.', time: new Date() }])
        setLoading(false)
        return
      }
      
      const txt = data.response || 'No response'
      setMessages(m => [...m, { 
        role: 'assistant', 
        text: txt, 
        time: new Date(), 
        medications: data.medications || [],
        triage: data.triage || null,
        mentalHealth: data.mental_health || null
      }])
      
      // Update symptoms and urgency
      if (data.symptoms_detected?.length > 0) {
        setDetectedSymptoms(prev => [...new Set([...prev, ...data.symptoms_detected])])
      }
      if (data.urgency_level) {
        setUrgencyLevel(data.urgency_level)
        if (data.urgency_level === 'emergency') setShowEmergency(true)
      }
      
      // Update triage information
      if (data.triage) {
        setTriageInfo(data.triage)
        if (data.triage.level === 'emergency') {
          setShowEmergency(true)
        }
      }
      
      // Update mental health information
      if (data.mental_health?.detected) {
        setMentalHealthInfo(data.mental_health)
        if (data.mental_health.is_crisis) {
          setShowCrisisBanner(true)
        } else if (data.mental_health.severity === 'moderate' || data.mental_health.severity === 'high') {
          setShowMentalHealthSupport(true)
        }
      }
      
      // Update suggested medications
      if (data.medications?.length > 0) {
        setSuggestedMeds(data.medications)
      }
      
      speak(txt)
    } catch (e) { 
      // Check if request was aborted (user cancelled)
      if (e.name === 'AbortError') {
        setMessages(m => [...m, { role: 'assistant', text: '⏹️ Response cancelled by user.', time: new Date() }])
      } else {
        setMessages(m => [...m, { role: 'assistant', text: 'Error occurred', time: new Date() }]) 
      }
    }
    abortControllerRef.current = null
    setLoading(false)
  }

  // Cancel ongoing request
  const cancelRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    stopSpeaking()
    setLoading(false)
  }

  // Export chat as text file
  const exportChat = () => {
    const content = [
      '=== CMC Health Consultation ===',
      `Date: ${new Date().toLocaleString()}`,
      `Phone: ${phone}`,
      `Language: ${langNames[language]}`,
      detectedSymptoms.length > 0 ? `Symptoms: ${detectedSymptoms.join(', ')}` : '',
      '---',
      ...messages.map(m => `[${m.role === 'user' ? 'You' : 'AI'}] ${m.text}`),
      '---',
      'Disclaimer: This is AI-generated health information and not a substitute for professional medical advice.'
    ].filter(Boolean).join('\n\n')
    
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `health-consultation-${new Date().toISOString().split('T')[0]}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Clear session
  const clearSession = () => {
    if (confirm('Clear all conversation history?')) {
      localStorage.removeItem(STORAGE_KEY)
      setMessages([])
      setSessionId('')
      setDetectedSymptoms([])
      setUrgencyLevel('low')
      setVitals(null)
      setView('home')
    }
  }

  // Image upload and analysis
  const handleImageSelect = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        alert('Image too large. Max 10MB')
        return
      }
      setSelectedImage(file)
      const reader = new FileReader()
      reader.onload = (e) => setImagePreview(e.target.result)
      reader.readAsDataURL(file)
      setShowImageUpload(true)
    }
  }

  const analyzeImage = async (context = '') => {
    if (!selectedImage) return
    setImageAnalyzing(true)
    setImageResult(null)
    
    try {
      const formData = new FormData()
      formData.append('file', selectedImage)
      formData.append('context', context)
      formData.append('image_type', 'skin')
      
      const res = await fetch(`${API_BASE}/image/analyze`, {
        method: 'POST',
        body: formData
      })
      
      const data = await res.json()
      
      if (data.success) {
        setImageResult(data)
        // Add to chat
        setMessages(m => [...m, 
          { role: 'user', text: `[📷 Image uploaded] ${context || 'Please analyze this image'}`, time: new Date(), image: imagePreview },
          { role: 'assistant', text: data.analysis, time: new Date(), severity: data.severity }
        ])
        speak(data.analysis)
      } else {
        alert(data.detail || 'Analysis failed')
      }
    } catch (e) {
      console.error('Image analysis error:', e)
      alert('Failed to analyze image. Please try again.')
    }
    
    setImageAnalyzing(false)
    setShowImageUpload(false)
    setSelectedImage(null)
    setImagePreview(null)
  }

  const closeImageModal = () => {
    setShowImageUpload(false)
    setSelectedImage(null)
    setImagePreview(null)
    setImageResult(null)
  }

  const getVitals = () => {
    setVitals({
      heartRate: Math.floor(60 + Math.random() * 40),
      spo2: Math.floor(94 + Math.random() * 6),
      temp: (97 + Math.random() * 3).toFixed(1),
      bp: `${Math.floor(110 + Math.random() * 30)}/${Math.floor(70 + Math.random() * 20)}`
    })
  }

  const formatTime = (d) => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  const quickActions = [{ label: 'Headache', msg: 'I have a headache' }, { label: 'Fever', msg: 'I have fever' }, { label: 'Stomach', msg: 'I have stomach pain' }, { label: 'Anxiety', msg: 'I feel anxious' }, { label: 'Sleep', msg: 'I cannot sleep' }]

  if (view === 'home') {
    return (
      <div className="app-container">
        {/* Medical Disclaimer Modal */}
        {showDisclaimer && (
          <div className="modal-overlay">
            <div className="modal">
              <div className="modal-header">
                <AlertIcon />
                <h2>Medical Disclaimer</h2>
              </div>
              <div className="modal-content">
                <p><strong>Important:</strong> CMC Health is an AI-powered health information tool and is NOT a substitute for professional medical advice, diagnosis, or treatment.</p>
                <ul>
                  <li>Always consult a qualified healthcare provider for medical concerns</li>
                  <li>In case of emergency, call 108 (India) or your local emergency number</li>
                  <li>Do not ignore professional medical advice based on AI suggestions</li>
                  <li>The AI may make mistakes - verify important information</li>
                </ul>
                <p>By using this app, you acknowledge that you understand these limitations.</p>
              </div>
              <button className="modal-btn" onClick={() => { localStorage.setItem('cmc_disclaimer_accepted', 'true'); setShowDisclaimer(false) }}>
                I Understand
              </button>
            </div>
          </div>
        )}
        
        <header className="header">
          <div className="logo-container">
            <div className="logo"><HeartIcon /></div>
            <h1 className="app-title">CMC Health</h1>
          </div>
          <p className="app-subtitle">AI-Powered Health Assistant</p>
        </header>
        <main className="main-content">
          <div className="glass-card">
            <div className="status-bar">
              <div className="status-indicator">
                <span className={`status-dot ${connected ? '' : 'offline'}`}></span>
                {connected ? 'Ready' : 'Offline'}
              </div>
            </div>
            <div className="welcome-message">
              <div className="welcome-icon"><MessageIcon /></div>
              <h2 className="welcome-title">Welcome to CMC Health</h2>
              <p className="welcome-text">Your personal AI health assistant. Get instant guidance in your language.</p>
            </div>
            <div className="input-area">
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display:'block', fontSize:'0.875rem', color:'var(--text-secondary)', marginBottom:'0.5rem', fontWeight:'500' }}>Phone Number</label>
                <input type="tel" className="input-field" value={phone} onChange={e => setPhone(e.target.value)} placeholder="+91 9876543210" style={{ width:'100%' }} />
              </div>
              <div className="language-selector" style={{ marginBottom:'1rem', justifyContent:'flex-start' }}>
                <label>Language</label>
                <select className="language-select" value={language} onChange={e => { setLanguage(e.target.value); setDetectedLang(e.target.value) }}>
                  {Object.entries(langNames).map(([c, n]) => <option key={c} value={c}>{n}</option>)}
                </select>
              </div>
              <div style={{ display:'flex', alignItems:'center', gap:'0.5rem', marginBottom:'1.5rem' }}>
                <input type="checkbox" id="voice" checked={voiceEnabled} onChange={e => setVoiceEnabled(e.target.checked)} style={{ width:'18px', height:'18px', accentColor:'var(--primary-color)' }} />
                <label htmlFor="voice" style={{ fontSize:'0.9rem', color:'var(--text-secondary)', cursor:'pointer' }}>Enable voice responses</label>
              </div>
              <button className="action-btn send-btn" onClick={startChat} disabled={loading} style={{ width:'100%', height:'50px', fontSize:'1rem', fontWeight:'600' }}>
                {loading ? <div className="loading-spinner"></div> : 'Start Consultation'}
              </button>
            </div>
          </div>
        </main>
        <footer className="footer"><p>For informational purposes only. Consult a healthcare professional.</p></footer>
      </div>
    )
  }

  return (
    <div className="app-container">
      {/* Emergency Banner */}
      {showEmergency && (
        <div className="emergency-banner">
          <div className="emergency-content">
            <AlertIcon />
            <span>Emergency symptoms detected! Please seek immediate medical attention.</span>
          </div>
          <div className="emergency-actions">
            <a href="tel:108" className="emergency-call"><PhoneIcon /> Call 108</a>
            <button onClick={() => setShowEmergency(false)}><XIcon /></button>
          </div>
        </div>
      )}
      
      {/* Mental Health Crisis Banner */}
      {showCrisisBanner && (
        <div className="crisis-banner">
          <div className="crisis-content">
            <HeartHandIcon />
            <div className="crisis-text">
              <strong>You're not alone. Help is available.</strong>
              <span>If you're in crisis, please reach out to a helpline.</span>
            </div>
          </div>
          <div className="crisis-actions">
            <a href="tel:9152987821" className="crisis-call"><PhoneIcon /> iCall: 9152987821</a>
            <a href="tel:18602662345" className="crisis-call"><PhoneIcon /> Vandrevala: 1860-2662-345</a>
            <button onClick={() => setShowCrisisBanner(false)}><XIcon /></button>
          </div>
        </div>
      )}
      
      {/* Mental Health Support Panel */}
      {showMentalHealthSupport && mentalHealthInfo && !showCrisisBanner && (
        <div className="mental-health-panel">
          <div className="mh-panel-header">
            <HeartHandIcon />
            <span>Mental Health Support</span>
            <button onClick={() => setShowMentalHealthSupport(false)}><XIcon /></button>
          </div>
          <div className="mh-panel-content">
            {mentalHealthInfo.categories?.length > 0 && (
              <div className="mh-categories">
                {mentalHealthInfo.categories.map((cat, i) => (
                  <span key={i} className={`mh-tag ${cat}`}>{cat}</span>
                ))}
              </div>
            )}
            {mentalHealthInfo.grounding_exercise && (
              <div className="mh-exercise">
                <strong>🧘 Grounding Exercise:</strong>
                <p>{mentalHealthInfo.grounding_exercise}</p>
              </div>
            )}
            {mentalHealthInfo.breathing_exercise && (
              <div className="mh-exercise">
                <strong>🌬️ Breathing Exercise:</strong>
                <p>{mentalHealthInfo.breathing_exercise}</p>
              </div>
            )}
            {mentalHealthInfo.resources?.length > 0 && (
              <div className="mh-resources">
                <strong>📞 Support Resources:</strong>
                {mentalHealthInfo.resources.map((res, i) => (
                  <div key={i} className="mh-resource">
                    <span>{res.name}</span>
                    <a href={`tel:${res.phone}`}>{res.phone}</a>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
      
      {/* Image Upload Modal */}
      {showImageUpload && (
        <div className="modal-overlay" onClick={closeImageModal}>
          <div className="modal image-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <CameraIcon />
              <h2>Analyze Image</h2>
              <button className="close-btn" onClick={closeImageModal}><XIcon /></button>
            </div>
            <div className="modal-content">
              {imagePreview && (
                <div className="image-preview-container">
                  <img src={imagePreview} alt="Preview" className="image-preview" />
                </div>
              )}
              <p className="image-hint">AI will analyze this image for visible health conditions (skin, wounds, rashes, etc.)</p>
              <input
                type="text"
                className="image-context-input"
                placeholder="Add context: e.g., 'appeared 2 days ago, itchy'"
                onKeyDown={e => e.key === 'Enter' && analyzeImage(e.target.value)}
              />
              <div className="image-modal-actions">
                <button className="modal-btn secondary" onClick={closeImageModal}>Cancel</button>
                <button 
                  className="modal-btn primary" 
                  onClick={() => analyzeImage(document.querySelector('.image-context-input')?.value || '')}
                  disabled={imageAnalyzing}
                >
                  {imageAnalyzing ? 'Analyzing...' : 'Analyze Image'}
                </button>
              </div>
              <p className="disclaimer-text">⚠️ AI analysis is not a medical diagnosis. Consult a healthcare professional.</p>
            </div>
          </div>
        </div>
      )}
      
      <header className="header">
        <div className="logo-container">
          <div className="logo" onClick={() => { setView('home'); stopSpeaking() }} style={{ cursor:'pointer' }}><HeartIcon /></div>
          <h1 className="app-title">CMC Health</h1>
        </div>
        <p className="app-subtitle">Health Consultation</p>
      </header>
      <main className="main-content">
        <div className="glass-card">
          <div className="status-bar">
            <div className="status-indicator">
              <span className={`status-dot ${connected ? '' : 'offline'}`}></span>
              {connected ? 'AI Online' : 'Reconnecting...'}
            </div>
            <div className="status-actions">
              <button className="icon-btn" onClick={exportChat} title="Export Chat"><DownloadIcon /></button>
              <button className="icon-btn" onClick={clearSession} title="Clear Session"><TrashIcon /></button>
            </div>
            <div className="language-selector">
              <label>Language</label>
              <select className="language-select" value={detectedLang} onChange={e => setDetectedLang(e.target.value)}>
                {Object.entries(langNames).map(([c, n]) => <option key={c} value={c}>{n}</option>)}
              </select>
            </div>
          </div>
          
          {/* Symptoms & Triage Summary */}
          {(detectedSymptoms.length > 0 || triageInfo) && (
            <div className={`symptoms-bar ${triageInfo?.level || urgencyLevel}`}>
              {triageInfo && (
                <div className="triage-badge" style={{ backgroundColor: triageInfo.color || '#4ade80' }}>
                  <ShieldIcon />
                  <span>{triageInfo.label || 'Self Care'}</span>
                </div>
              )}
              {detectedSymptoms.length > 0 && (
                <>
                  <span className="symptoms-label">Detected:</span>
                  {detectedSymptoms.slice(0, 5).map((s, i) => <span key={i} className="symptom-tag">{s}</span>)}
                  {detectedSymptoms.length > 5 && <span className="symptom-tag more">+{detectedSymptoms.length - 5}</span>}
                </>
              )}
              {triageInfo?.action && (
                <span className="triage-action">{triageInfo.action}</span>
              )}
              {urgencyLevel === 'emergency' && <span className="urgency-badge emergency">🚨 Emergency</span>}
            </div>
          )}
          <div className="chat-container">
            {messages.length === 0 ? (
              <div className="welcome-message">
                <div className="welcome-icon"><MessageIcon /></div>
                <h2 className="welcome-title">How can I help?</h2>
                <p className="welcome-text">Describe your symptoms or ask health questions.</p>
              </div>
            ) : (
              messages.map((m, i) => (
                <div key={i} className={`message ${m.role}`}>
                  {m.role === 'assistant' && <div className="message-avatar"><BotIcon /></div>}
                  <div className="message-content">
                    {/* Triage level indicator */}
                    {m.role === 'assistant' && m.triage?.level && m.triage.level !== 'self_care' && (
                      <div className="message-triage-badge" style={{ borderLeftColor: m.triage.color }}>
                        <ShieldIcon />
                        <span>{m.triage.label}</span>
                        {m.triage.detected_condition && <span className="triage-condition">• {m.triage.detected_condition}</span>}
                      </div>
                    )}
                    
                    {/* Mental Health indicator for message */}
                    {m.role === 'assistant' && m.mentalHealth?.detected && (
                      <div className={`message-mh-indicator ${m.mentalHealth.is_crisis ? 'crisis' : m.mentalHealth.severity}`}>
                        <HeartHandIcon />
                        <span>{m.mentalHealth.is_crisis ? 'Crisis Support Activated' : 'Mental Health Support'}</span>
                      </div>
                    )}
                    
                    {/* Formatted message content */}
                    {m.role === 'assistant' ? (
                      <FormattedMessage 
                        text={m.text} 
                        triage={m.triage} 
                        medications={m.medications}
                        mentalHealth={m.mentalHealth}
                      />
                    ) : (
                      <div className="user-message-text">{m.text}</div>
                    )}
                    
                    <div className="message-time">{formatTime(m.time)}</div>
                  </div>
                  {m.role === 'user' && <div className="message-avatar"><UserIcon /></div>}
                </div>
              ))
            )}
            {loading && (
              <div className="message assistant">
                <div className="message-avatar"><BotIcon /></div>
                <div className="typing-indicator">
                  <span></span><span></span><span></span>
                  <button className="cancel-btn" onClick={cancelRequest} title="Cancel request">
                    <StopCircleIcon /> Cancel
                  </button>
                </div>
              </div>
            )}
            <div ref={chatEndRef}></div>
          </div>
          <div className="quick-actions">
            {quickActions.map((a, i) => <button key={i} className="quick-action-btn" onClick={() => sendMsg(a.msg)} disabled={loading}>{a.label}</button>)}
          </div>
          <div className="input-area">
            <div className="input-wrapper">
              <button className={`action-btn voice-btn ${isListening ? 'active' : ''}`} onClick={toggleListening}><MicIcon /></button>
              <button className="action-btn camera-btn" onClick={() => imageInputRef.current?.click()} title="Upload image for analysis"><CameraIcon /></button>
              <input type="file" ref={imageInputRef} accept="image/*" onChange={handleImageSelect} style={{ display: 'none' }} />
              <div className="input-field-container">
                <input type="text" className="input-field" value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMsg()} placeholder={isListening ? 'Listening...' : 'Type message...'} disabled={loading} />
              </div>
              {/* Stop Speaking Button - shows when AI is speaking */}
              {isSpeaking && (
                <button className="action-btn stop-btn" onClick={stopSpeaking} title="Stop speaking">
                  <StopIcon />
                </button>
              )}
              <button className={`action-btn speaker-btn ${voiceEnabled ? 'active' : ''}`} onClick={() => isSpeaking ? stopSpeaking() : setVoiceEnabled(!voiceEnabled)}>
                {voiceEnabled ? <VolumeIcon /> : <VolumeOffIcon />}
              </button>
              {/* Show Cancel button when loading, Send button otherwise */}
              {loading ? (
                <button className="action-btn cancel-request-btn" onClick={cancelRequest} title="Cancel request">
                  <StopCircleIcon />
                </button>
              ) : (
                <button className="action-btn send-btn" onClick={() => sendMsg()} disabled={!input.trim()}><SendIcon /></button>
              )}
            </div>
          </div>
        </div>
        <div className="glass-card vitals-card">
          <div className="vitals-header">
            <div className="vitals-title"><ActivityIcon /> Health Vitals</div>
            <button className="quick-action-btn" onClick={getVitals} style={{ margin:0 }}>Sync</button>
          </div>
          <div className="vitals-grid">
            <div className="vital-item">
              <div className="vital-icon heart"><HeartIcon /></div>
              <div className="vital-label">Heart Rate</div>
              <div className="vital-value">{vitals?.heartRate || '--'}<span className="vital-unit"> bpm</span></div>
              {vitals && <span className={`vital-status ${vitals.heartRate < 60 || vitals.heartRate > 100 ? 'warning' : 'normal'}`}>{vitals.heartRate < 60 || vitals.heartRate > 100 ? 'Check' : 'Normal'}</span>}
            </div>
            <div className="vital-item">
              <div className="vital-icon oxygen"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg></div>
              <div className="vital-label">SpO2</div>
              <div className="vital-value">{vitals?.spo2 || '--'}<span className="vital-unit">%</span></div>
              {vitals && <span className={`vital-status ${vitals.spo2 < 95 ? 'warning' : 'normal'}`}>{vitals.spo2 < 95 ? 'Low' : 'Normal'}</span>}
            </div>
            <div className="vital-item">
              <div className="vital-icon temp"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"/></svg></div>
              <div className="vital-label">Temperature</div>
              <div className="vital-value">{vitals?.temp || '--'}<span className="vital-unit">°F</span></div>
              {vitals && <span className={`vital-status ${parseFloat(vitals.temp) > 99 ? 'warning' : 'normal'}`}>{parseFloat(vitals.temp) > 99 ? 'Elevated' : 'Normal'}</span>}
            </div>
            <div className="vital-item">
              <div className="vital-icon bp"><ActivityIcon /></div>
              <div className="vital-label">Blood Pressure</div>
              <div className="vital-value">{vitals?.bp || '--/--'}<span className="vital-unit"> mmHg</span></div>
              {vitals && <span className="vital-status normal">Normal</span>}
            </div>
          </div>
        </div>
      </main>
      <footer className="footer"><p>For informational purposes only. Consult a healthcare professional.</p></footer>
    </div>
  )
}

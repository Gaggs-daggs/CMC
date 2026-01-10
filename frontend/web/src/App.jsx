import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import './App.premium.css'
import WebGLBackground from './components/WebGLBackground'
import SessionSidebar from './components/SessionSidebar'
import {
  MedicalCrossIcon,
  HeartPulseIcon,
  PillIcon,
  StethoscopeIcon,
  ActivityPulseIcon,
  ShieldCheckIcon,
  UserIcon as PremiumUserIcon,
  BotIcon as PremiumBotIcon,
  MicrophoneIcon,
  SendIcon as PremiumSendIcon,
  VolumeIcon as PremiumVolumeIcon,
  VolumeOffIcon as PremiumVolumeOffIcon,
  CameraIcon as PremiumCameraIcon,
  DownloadIcon as PremiumDownloadIcon,
  TrashIcon as PremiumTrashIcon,
  PhoneIcon as PremiumPhoneIcon,
  CloseIcon,
  AlertTriangleIcon,
  MessageSquareIcon,
  ClipboardMedicalIcon,
  LifebuoyIcon,
  HeartHandshakeIcon,
  StopCircleIcon as PremiumStopCircleIcon
} from './components/PremiumIcons'

// API URL: Uses environment variable in production, localhost in development
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
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

// Premium icon wrappers with consistent sizing
const HeartIcon = () => <HeartPulseIcon size={24} />
const MicIcon = () => <MicrophoneIcon size={24} />
const SendIcon = () => <PremiumSendIcon size={24} />
const VolumeIcon = () => <PremiumVolumeIcon size={24} />
const VolumeOffIcon = () => <PremiumVolumeOffIcon size={24} />
const ActivityIcon = () => <ActivityPulseIcon size={24} />
const UserIcon = () => <PremiumUserIcon size={24} />
const BotIcon = () => <PremiumBotIcon size={24} />
const MessageIcon = () => <MessageSquareIcon size={24} />
const AlertIcon = () => <AlertTriangleIcon size={24} />
const DownloadIcon = () => <PremiumDownloadIcon size={24} />
const TrashIcon = () => <PremiumTrashIcon size={24} />
const PhoneIcon = () => <PremiumPhoneIcon size={24} />
const XIcon = () => <CloseIcon size={24} />
const CameraIcon = () => <PremiumCameraIcon size={24} />
const ImageIcon = () => <PremiumCameraIcon size={24} />
const PillIconComponent = () => <PillIcon size={24} />
const ShieldIcon = () => <ShieldCheckIcon size={24} />
const HeartHandIcon = () => <HeartHandshakeIcon size={24} />
const LifeBuoyIcon = () => <LifebuoyIcon size={24} />
const ClipboardIcon = () => <ClipboardMedicalIcon size={24} />
const StethoscopeIconComponent = () => <StethoscopeIcon size={24} />
const HeartPulseIconComponent = () => <HeartPulseIcon size={24} />
const StopIcon = () => <PremiumStopCircleIcon size={24} />
const StopCircleIcon = () => <PremiumStopCircleIcon size={24} />
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
  const [medsExpanded, setMedsExpanded] = useState(false)
  const [triageInfo, setTriageInfo] = useState(savedSession?.triage || null)
  const [mentalHealthInfo, setMentalHealthInfo] = useState(savedSession?.mentalHealth || null)
  const [showMentalHealthSupport, setShowMentalHealthSupport] = useState(false)
  const [showCrisisBanner, setShowCrisisBanner] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)
  
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

  // New state for profile management
  const [profileData, setProfileData] = useState(null)
  const [showProfileForm, setShowProfileForm] = useState(false)
  const [profileForm, setProfileForm] = useState({
    name: '',
    age: '',
    gender: 'not_specified',
    blood_type: '',
    height_cm: '',
    weight_kg: '',
    allergies: [],
    conditions: []
  })
  const [newAllergy, setNewAllergy] = useState('')
  const [newCondition, setNewCondition] = useState('')
  const [isReturningUser, setIsReturningUser] = useState(false)
  
  // BMI Calculation
  const calculateBMI = () => {
    const h = parseFloat(profileForm.height_cm)
    const w = parseFloat(profileForm.weight_kg)
    if (h > 0 && w > 0) {
      const heightM = h / 100
      return (w / (heightM * heightM)).toFixed(1)
    }
    return null
  }
  
  const getBMICategory = (bmi) => {
    if (!bmi) return null
    const b = parseFloat(bmi)
    if (b < 18.5) return { label: 'Underweight', color: '#3b82f6', icon: '📉' }
    if (b < 25) return { label: 'Normal', color: '#22c55e', icon: '✅' }
    if (b < 30) return { label: 'Overweight', color: '#f59e0b', icon: '⚠️' }
    return { label: 'Obese', color: '#ef4444', icon: '🔴' }
  }
  
  const bmi = calculateBMI()
  const bmiCategory = getBMICategory(bmi)
  
  // Autocomplete state
  const [allergySuggestions, setAllergySuggestions] = useState([])
  const [conditionSuggestions, setConditionSuggestions] = useState([])
  const [showAllergySuggestions, setShowAllergySuggestions] = useState(false)
  const [showConditionSuggestions, setShowConditionSuggestions] = useState(false)

  // Debounced autocomplete search
  const searchAllergens = async (query) => {
    if (query.length < 1) {
      setAllergySuggestions([])
      setShowAllergySuggestions(false)
      return
    }
    try {
      const res = await fetch(`${API_BASE}/autocomplete/allergens?q=${encodeURIComponent(query)}&limit=8`)
      const data = await res.json()
      if (data.success) {
        setAllergySuggestions(data.results)
        setShowAllergySuggestions(data.results.length > 0)
      }
    } catch (e) {
      console.error('Allergen search failed:', e)
    }
  }

  const searchConditions = async (query) => {
    if (query.length < 1) {
      setConditionSuggestions([])
      setShowConditionSuggestions(false)
      return
    }
    try {
      const res = await fetch(`${API_BASE}/autocomplete/conditions?q=${encodeURIComponent(query)}&limit=8`)
      const data = await res.json()
      if (data.success) {
        setConditionSuggestions(data.results)
        setShowConditionSuggestions(data.results.length > 0)
      }
    } catch (e) {
      console.error('Condition search failed:', e)
    }
  }

  // Debounce timers
  const allergyTimerRef = useRef(null)
  const conditionTimerRef = useRef(null)

  const handleAllergyInput = (value) => {
    setNewAllergy(value)
    if (allergyTimerRef.current) clearTimeout(allergyTimerRef.current)
    allergyTimerRef.current = setTimeout(() => searchAllergens(value), 200)
  }

  const handleConditionInput = (value) => {
    setNewCondition(value)
    if (conditionTimerRef.current) clearTimeout(conditionTimerRef.current)
    conditionTimerRef.current = setTimeout(() => searchConditions(value), 200)
  }

  const selectAllergySuggestion = (name) => {
    if (!profileForm.allergies.includes(name)) {
      setProfileForm(p => ({ ...p, allergies: [...p.allergies, name] }))
    }
    setNewAllergy('')
    setShowAllergySuggestions(false)
  }

  const selectConditionSuggestion = (name) => {
    if (!profileForm.conditions.includes(name)) {
      setProfileForm(p => ({ ...p, conditions: [...p.conditions, name] }))
    }
    setNewCondition('')
    setShowConditionSuggestions(false)
  }

  const checkProfileAndStart = async () => {
    if (!phone.trim()) return alert('Enter phone number')
    setLoading(true)
    try {
      // First check if profile exists
      const checkRes = await fetch(`${API_BASE}/profile/check`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone_number: phone })
      })
      const checkData = await checkRes.json()
      
      if (checkData.exists) {
        // Returning user - fetch full profile and start chat
        setIsReturningUser(true)
        setProfileData(checkData)
        await startChat(checkData.profile_name)
      } else {
        // New user - show profile creation form
        setShowProfileForm(true)
        setLoading(false)
      }
    } catch (e) { 
      console.error('Profile check failed:', e)
      // Fallback to direct chat start if profile service fails
      await startChat()
    }
  }

  const createProfileAndStart = async () => {
    setLoading(true)
    try {
      // Create the profile
      const createRes = await fetch(`${API_BASE}/profile/create`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone_number: phone,
          name: profileForm.name || 'User',
          age: profileForm.age ? parseInt(profileForm.age) : null,
          gender: profileForm.gender,
          blood_type: profileForm.blood_type || null,
          height_cm: profileForm.height_cm ? parseFloat(profileForm.height_cm) : null,
          weight_kg: profileForm.weight_kg ? parseFloat(profileForm.weight_kg) : null,
          allergies: profileForm.allergies,
          chronic_conditions: profileForm.conditions
        })
      })
      
      if (!createRes.ok) {
        throw new Error('Failed to create profile')
      }
      
      setShowProfileForm(false)
      await startChat(profileForm.name)
    } catch (e) {
      console.error('Profile creation failed:', e)
      alert('Could not create profile. Starting without profile.')
      setShowProfileForm(false)
      await startChat()
    }
  }

  const addAllergy = () => {
    if (newAllergy.trim()) {
      setProfileForm(p => ({ ...p, allergies: [...p.allergies, newAllergy.trim()] }))
      setNewAllergy('')
    }
  }

  const addCondition = () => {
    if (newCondition.trim()) {
      setProfileForm(p => ({ ...p, conditions: [...p.conditions, newCondition.trim()] }))
      setNewCondition('')
    }
  }

  const removeAllergy = (idx) => setProfileForm(p => ({ ...p, allergies: p.allergies.filter((_, i) => i !== idx) }))
  const removeCondition = (idx) => setProfileForm(p => ({ ...p, conditions: p.conditions.filter((_, i) => i !== idx) }))

  const startChat = async (userName = null) => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/conversation/start`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: phone, language, phone_number: phone })
      })
      const data = await res.json()
      setSessionId(data.session_id)
      
      // Personalized greeting for returning users
      let greeting = data.greeting
      if (userName && isReturningUser) {
        greeting = `Welcome back, ${userName}! ${data.greeting}`
      } else if (userName) {
        greeting = `Hello ${userName}! ${data.greeting}`
      }
      
      setMessages([{ role: 'assistant', text: greeting, time: new Date() }])
      setView('chat')
      setConnected(true)
      setTimeout(() => speak(greeting), 500)
    } catch (e) { setConnected(false); alert('Server offline') }
    setLoading(false)
  }

  const sendMsg = async (override) => {
    const msg = override || input
    if (!msg.trim() || loading) return
    
    // Detect language from user's message
    const msgLang = detectLanguage(msg)
    
    // Determine output language priority:
    // 1. Use the dropdown-selected language (detectedLang) - this is what user explicitly wants
    // 2. If message is in a different non-English language, switch to that
    // 3. Fallback to 'en'
    let outputLang = detectedLang || language || 'en'
    
    // If user types in a different non-English language, update selection
    if (msgLang !== 'en' && msgLang !== detectedLang) {
      setDetectedLang(msgLang)
      outputLang = msgLang  // Use the detected language immediately (don't wait for state update)
    }
    
    console.log('📝 Message language:', msgLang, '| Output language:', outputLang, '| Dropdown selection:', detectedLang)
    
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
      
      // Use translated response if available, otherwise fall back to original
      const txt = data.response_translated || data.response || 'No response'
      
      // Detailed logging for debugging translation issues - v2
      console.log('=== API Response Debug ===')
      console.log('🔤 Language sent to API:', outputLang)
      console.log('📥 Response (English):', data.response?.substring(0, 150))
      console.log('📥 Response (Translated):', data.response_translated ? data.response_translated.substring(0, 150) : '❌ NULL/EMPTY - Translation not working!')
      console.log('✅ Displaying text:', txt?.substring(0, 150))
      console.log('📊 Components used:', data.components_used)
      console.log('=========================')
      
      // IMPORTANT: Use translated response, fall back to English only if translation is null
      const displayText = (outputLang !== 'en' && data.response_translated) ? data.response_translated : txt
      
      setMessages(m => [...m, { 
        role: 'assistant', 
        text: displayText,  // Use displayText which prefers translated
        time: new Date(), 
        medications: data.medications || [],
        triage: data.triage || null,
        mentalHealth: data.mental_health || null
      }])
      
      // Update symptoms and urgency - replace with latest, don't accumulate stale ones
      if (data.symptoms_detected?.length > 0) {
        // Only keep meaningful symptoms (filter out context phrases)
        const cleanSymptoms = data.symptoms_detected
          .filter(s => s.split(' ').length <= 3) // Max 3 words
          .slice(0, 5) // Max 5 symptoms shown
        setDetectedSymptoms(cleanSymptoms)
      }
      if (data.urgency_level) {
        setUrgencyLevel(data.urgency_level)
        if (data.urgency_level === 'emergency') setShowEmergency(true)
      }
      
      // Update suggested medications - replace with current response
      if (data.medications?.length > 0) {
        console.log('💊 Setting medications:', data.medications)
        setSuggestedMeds(data.medications)
      } else {
        console.log('💊 No medications in response')
        setSuggestedMeds([]) // Clear if no medications in response
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

  // Session sidebar handlers
  const handleNewSession = (session) => {
    if (session) {
      setSessionId(session.session_id)
      setMessages([{ role: 'assistant', text: 'How can I help you today?', time: new Date() }])
      setDetectedSymptoms([])
      setUrgencyLevel('low')
      setSuggestedMeds([])
      setTriageInfo(null)
      setMentalHealthInfo(null)
      setView('chat')
    } else {
      // Clear current session
      setMessages([])
      setSessionId('')
      setDetectedSymptoms([])
      setUrgencyLevel('low')
    }
  }

  const handleLoadSession = (session) => {
    if (session) {
      setSessionId(session.session_id)
      // Convert messages from API format to app format
      const loadedMessages = (session.messages || []).map(m => ({
        role: m.role,
        text: m.content,
        time: new Date(m.timestamp)
      }))
      setMessages(loadedMessages.length > 0 ? loadedMessages : [{ 
        role: 'assistant', 
        text: 'How can I help you today?', 
        time: new Date() 
      }])
      setDetectedSymptoms(session.symptoms || [])
      setUrgencyLevel(session.urgency_level || 'low')
      setView('chat')
    }
  }

  const handleProfileUpdate = (profile) => {
    setProfileData({ ...profileData, profile })
    if (profile.preferred_language) {
      setLanguage(profile.preferred_language)
      setDetectedLang(profile.preferred_language)
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

  // Animation variants for Framer Motion
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1, transition: { duration: 0.5, staggerChildren: 0.1 } }
  }
  
  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } }
  }
  
  const cardVariants = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1, transition: { duration: 0.4 } },
    hover: { scale: 1.02, boxShadow: "0 20px 40px rgba(0, 212, 170, 0.15)" }
  }
  
  const buttonVariants = {
    hover: { scale: 1.05, boxShadow: "0 10px 30px rgba(0, 212, 170, 0.4)" },
    tap: { scale: 0.95 }
  }

  if (view === 'home') {
    return (
      <div className="app-container premium-theme">
        {/* WebGL Background */}
        <WebGLBackground />
        
        {/* Medical Disclaimer Modal */}
        <AnimatePresence>
          {showDisclaimer && (
            <motion.div 
              className="modal-overlay"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <motion.div 
                className="modal"
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
              >
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
                <motion.button 
                  className="modal-btn" 
                  onClick={() => { localStorage.setItem('cmc_disclaimer_accepted', 'true'); setShowDisclaimer(false) }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  I Understand
                </motion.button>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
        
        <motion.header 
          className="header"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="logo-container">
            <motion.div 
              className="logo premium-logo"
              animate={{ 
                boxShadow: ["0 0 20px rgba(0, 212, 170, 0.3)", "0 0 40px rgba(0, 212, 170, 0.5)", "0 0 20px rgba(0, 212, 170, 0.3)"]
              }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              <MedicalCrossIcon size={32} />
            </motion.div>
            <h1 className="app-title premium-title">CMC Health</h1>
          </div>
          <motion.p 
            className="app-subtitle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            AI-Powered Health Assistant
          </motion.p>
        </motion.header>
        
        <motion.main 
          className="main-content"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          <motion.div 
            className="glass-card premium-card"
            variants={cardVariants}
            whileHover="hover"
          >
            <div className="status-bar">
              <motion.div 
                className="status-indicator"
                animate={{ opacity: [0.7, 1, 0.7] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <span className={`status-dot ${connected ? 'pulse' : 'offline'}`}></span>
                {connected ? 'Ready' : 'Offline'}
              </motion.div>
            </div>
            
            <motion.div className="welcome-message" variants={itemVariants}>
              <motion.div 
                className="welcome-icon premium-welcome-icon"
                animate={{ 
                  rotate: [0, 5, -5, 0],
                  scale: [1, 1.05, 1]
                }}
                transition={{ duration: 3, repeat: Infinity }}
              >
                <HeartPulseIcon size={48} />
              </motion.div>
              <h2 className="welcome-title">Welcome to CMC Health</h2>
              <p className="welcome-text">Your personal AI health assistant. Get instant guidance in your language.</p>
            </motion.div>
            
            <motion.div className="input-area" variants={itemVariants}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display:'block', fontSize:'0.875rem', color:'var(--text-secondary)', marginBottom:'0.5rem', fontWeight:'500' }}>Phone Number</label>
                <motion.input 
                  type="tel" 
                  className="input-field premium-input" 
                  value={phone} 
                  onChange={e => setPhone(e.target.value)} 
                  placeholder="+91 9876543210" 
                  style={{ width:'100%' }}
                  whileFocus={{ boxShadow: "0 0 0 3px rgba(0, 212, 170, 0.3)" }}
                />
              </div>
              <div className="language-selector" style={{ marginBottom:'1rem', justifyContent:'flex-start' }}>
                <label>Language</label>
                <select className="language-select premium-select" value={language} onChange={e => { setLanguage(e.target.value); setDetectedLang(e.target.value) }}>
                  {Object.entries(langNames).map(([c, n]) => <option key={c} value={c}>{n}</option>)}
                </select>
              </div>
              <div style={{ display:'flex', alignItems:'center', gap:'0.5rem', marginBottom:'1.5rem' }}>
                <input type="checkbox" id="voice" checked={voiceEnabled} onChange={e => setVoiceEnabled(e.target.checked)} style={{ width:'18px', height:'18px', accentColor:'var(--accent-teal)' }} />
                <label htmlFor="voice" style={{ fontSize:'0.9rem', color:'var(--text-secondary)', cursor:'pointer' }}>Enable voice responses</label>
              </div>
              <motion.button 
                className="action-btn send-btn premium-btn" 
                onClick={checkProfileAndStart} 
                disabled={loading} 
                style={{ width:'100%', height:'50px', fontSize:'1rem', fontWeight:'600' }}
                variants={buttonVariants}
                whileHover="hover"
                whileTap="tap"
              >
                {loading ? <div className="loading-spinner"></div> : (
                  <>
                    <StethoscopeIcon size={20} />
                    <span style={{ marginLeft: '0.5rem' }}>Start Consultation</span>
                  </>
                )}
              </motion.button>
            </motion.div>
          </motion.div>
        </motion.main>
        
        {/* Premium Profile Creation Modal */}
        <AnimatePresence>
          {showProfileForm && (
            <motion.div 
              style={{
                position: 'fixed',
                inset: 0,
                background: 'rgba(0, 0, 0, 0.8)',
                backdropFilter: 'blur(8px)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000,
                padding: '1rem'
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowProfileForm(false)}
            >
              <motion.div 
                onClick={(e) => e.stopPropagation()}
                initial={{ scale: 0.9, opacity: 0, y: 20 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.9, opacity: 0, y: 20 }}
                transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                style={{
                  background: 'linear-gradient(145deg, rgba(26, 31, 46, 0.98) 0%, rgba(15, 20, 30, 0.98) 100%)',
                  borderRadius: '1.5rem',
                  border: '1px solid rgba(0, 212, 170, 0.2)',
                  boxShadow: '0 25px 80px rgba(0, 0, 0, 0.6), 0 0 60px rgba(0, 212, 170, 0.1)',
                  maxWidth: '600px',
                  width: '100%',
                  maxHeight: '90vh',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                {/* Modal Header */}
                <div style={{
                  background: 'linear-gradient(135deg, rgba(0, 212, 170, 0.15) 0%, rgba(99, 102, 241, 0.1) 100%)',
                  padding: '1.5rem 2rem',
                  borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem'
                }}>
                  <div style={{
                    width: '50px',
                    height: '50px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #00d4aa 0%, #6366f1 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 4px 20px rgba(0, 212, 170, 0.4)'
                  }}>
                    <PremiumUserIcon size={26} />
                  </div>
                  <div>
                    <h2 style={{ margin: 0, fontSize: '1.5rem', fontWeight: '700', color: '#ffffff' }}>
                      Create Your Health Profile
                    </h2>
                    <p style={{ margin: 0, fontSize: '0.875rem', color: 'rgba(255, 255, 255, 0.6)' }}>
                      Personalized care starts with knowing you
                    </p>
                  </div>
                  <button 
                    onClick={() => setShowProfileForm(false)}
                    style={{
                      marginLeft: 'auto',
                      background: 'rgba(255, 255, 255, 0.1)',
                      border: 'none',
                      borderRadius: '50%',
                      width: '36px',
                      height: '36px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      cursor: 'pointer',
                      color: 'rgba(255, 255, 255, 0.6)',
                      fontSize: '1.25rem',
                      transition: 'all 0.2s'
                    }}
                    onMouseEnter={e => { e.target.style.background = 'rgba(255, 255, 255, 0.2)'; e.target.style.color = '#fff' }}
                    onMouseLeave={e => { e.target.style.background = 'rgba(255, 255, 255, 0.1)'; e.target.style.color = 'rgba(255, 255, 255, 0.6)' }}
                  >
                    ×
                  </button>
                </div>

                {/* Modal Body */}
                <div style={{ padding: '1.5rem 2rem', overflowY: 'auto', flex: 1 }}>
                  {/* Personal Info Section */}
                  <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '0.5rem', 
                      marginBottom: '1rem',
                      color: '#00d4aa',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      letterSpacing: '0.1em'
                    }}>
                      <span style={{ width: '20px', height: '1px', background: '#00d4aa' }}></span>
                      Personal Information
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div style={{ gridColumn: 'span 2' }}>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>
                          Full Name <span style={{ color: '#ef4444' }}>*</span>
                        </label>
                        <input 
                          type="text" 
                          value={profileForm.name} 
                          onChange={e => setProfileForm(p => ({ ...p, name: e.target.value }))}
                          placeholder="Enter your full name"
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            transition: 'all 0.2s',
                            boxSizing: 'border-box'
                          }}
                          onFocus={e => { e.target.style.borderColor = '#00d4aa'; e.target.style.boxShadow = '0 0 0 3px rgba(0, 212, 170, 0.1)' }}
                          onBlur={e => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'; e.target.style.boxShadow = 'none' }}
                        />
                      </div>
                      
                      <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>Age</label>
                        <input 
                          type="number" 
                          value={profileForm.age} 
                          onChange={e => setProfileForm(p => ({ ...p, age: e.target.value }))}
                          placeholder="Age"
                          min="0" max="150"
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            boxSizing: 'border-box'
                          }}
                          onFocus={e => { e.target.style.borderColor = '#00d4aa'; e.target.style.boxShadow = '0 0 0 3px rgba(0, 212, 170, 0.1)' }}
                          onBlur={e => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'; e.target.style.boxShadow = 'none' }}
                        />
                      </div>
                      
                      <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>Gender</label>
                        <select 
                          value={profileForm.gender}
                          onChange={e => setProfileForm(p => ({ ...p, gender: e.target.value }))}
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            cursor: 'pointer',
                            boxSizing: 'border-box'
                          }}
                        >
                          <option value="not_specified" style={{ background: '#1a1f2e' }}>Prefer not to say</option>
                          <option value="male" style={{ background: '#1a1f2e' }}>Male</option>
                          <option value="female" style={{ background: '#1a1f2e' }}>Female</option>
                          <option value="other" style={{ background: '#1a1f2e' }}>Other</option>
                        </select>
                      </div>
                      
                      <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>Blood Type</label>
                        <select 
                          value={profileForm.blood_type}
                          onChange={e => setProfileForm(p => ({ ...p, blood_type: e.target.value }))}
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            cursor: 'pointer',
                            boxSizing: 'border-box'
                          }}
                        >
                          <option value="" style={{ background: '#1a1f2e' }}>Unknown</option>
                          <option value="A+" style={{ background: '#1a1f2e' }}>A+</option>
                          <option value="A-" style={{ background: '#1a1f2e' }}>A-</option>
                          <option value="B+" style={{ background: '#1a1f2e' }}>B+</option>
                          <option value="B-" style={{ background: '#1a1f2e' }}>B-</option>
                          <option value="AB+" style={{ background: '#1a1f2e' }}>AB+</option>
                          <option value="AB-" style={{ background: '#1a1f2e' }}>AB-</option>
                          <option value="O+" style={{ background: '#1a1f2e' }}>O+</option>
                          <option value="O-" style={{ background: '#1a1f2e' }}>O-</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  {/* Body Metrics Section with BMI */}
                  <div style={{ marginBottom: '1.5rem' }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '0.5rem', 
                      marginBottom: '1rem',
                      color: '#6366f1',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      letterSpacing: '0.1em'
                    }}>
                      <span style={{ width: '20px', height: '1px', background: '#6366f1' }}></span>
                      Body Metrics & BMI
                    </div>
                    
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', alignItems: 'end' }}>
                      <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>
                          Height (cm)
                        </label>
                        <input 
                          type="number" 
                          value={profileForm.height_cm} 
                          onChange={e => setProfileForm(p => ({ ...p, height_cm: e.target.value }))}
                          placeholder="170"
                          min="50" max="300"
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            boxSizing: 'border-box'
                          }}
                          onFocus={e => { e.target.style.borderColor = '#6366f1'; e.target.style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.1)' }}
                          onBlur={e => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'; e.target.style.boxShadow = 'none' }}
                        />
                      </div>
                      
                      <div>
                        <label style={{ display: 'block', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>
                          Weight (kg)
                        </label>
                        <input 
                          type="number" 
                          value={profileForm.weight_kg} 
                          onChange={e => setProfileForm(p => ({ ...p, weight_kg: e.target.value }))}
                          placeholder="70"
                          min="20" max="500"
                          style={{
                            width: '100%',
                            padding: '0.875rem 1rem',
                            background: 'rgba(255, 255, 255, 0.05)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '0.75rem',
                            color: '#ffffff',
                            fontSize: '0.95rem',
                            outline: 'none',
                            boxSizing: 'border-box'
                          }}
                          onFocus={e => { e.target.style.borderColor = '#6366f1'; e.target.style.boxShadow = '0 0 0 3px rgba(99, 102, 241, 0.1)' }}
                          onBlur={e => { e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)'; e.target.style.boxShadow = 'none' }}
                        />
                      </div>
                      
                      {/* BMI Display Widget */}
                      <div style={{
                        background: bmi ? (
                          parseFloat(bmi) < 18.5 ? 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(59, 130, 246, 0.05) 100%)' :
                          parseFloat(bmi) < 25 ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(34, 197, 94, 0.05) 100%)' :
                          parseFloat(bmi) < 30 ? 'linear-gradient(135deg, rgba(245, 158, 11, 0.2) 0%, rgba(245, 158, 11, 0.05) 100%)' :
                          'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.05) 100%)'
                        ) : 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
                        border: `1px solid ${bmi ? (
                          parseFloat(bmi) < 18.5 ? 'rgba(59, 130, 246, 0.3)' :
                          parseFloat(bmi) < 25 ? 'rgba(34, 197, 94, 0.3)' :
                          parseFloat(bmi) < 30 ? 'rgba(245, 158, 11, 0.3)' :
                          'rgba(239, 68, 68, 0.3)'
                        ) : 'rgba(255, 255, 255, 0.1)'}`,
                        borderRadius: '0.75rem',
                        padding: '0.75rem',
                        textAlign: 'center',
                        minHeight: '70px',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center'
                      }}>
                        {bmi ? (
                          <>
                            <div style={{ 
                              fontSize: '1.5rem', 
                              fontWeight: '700',
                              color: parseFloat(bmi) < 18.5 ? '#3b82f6' :
                                     parseFloat(bmi) < 25 ? '#22c55e' :
                                     parseFloat(bmi) < 30 ? '#f59e0b' : '#ef4444'
                            }}>
                              {bmi}
                            </div>
                            <div style={{ 
                              fontSize: '0.7rem', 
                              color: 'rgba(255, 255, 255, 0.6)',
                              marginTop: '0.25rem',
                              fontWeight: '500'
                            }}>
                              BMI • {parseFloat(bmi) < 18.5 ? 'Underweight' :
                                     parseFloat(bmi) < 25 ? 'Normal' :
                                     parseFloat(bmi) < 30 ? 'Overweight' : 'Obese'}
                            </div>
                          </>
                        ) : (
                          <div style={{ fontSize: '0.75rem', color: 'rgba(255, 255, 255, 0.4)' }}>
                            Enter height & weight<br/>to calculate BMI
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Medical History Section */}
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '0.5rem', 
                      marginBottom: '1rem',
                      color: '#ef4444',
                      fontSize: '0.75rem',
                      fontWeight: '600',
                      textTransform: 'uppercase',
                      letterSpacing: '0.1em'
                    }}>
                      <span style={{ width: '20px', height: '1px', background: '#ef4444' }}></span>
                      Medical History
                    </div>
                    
                    {/* Allergies Input */}
                    <div style={{ marginBottom: '1rem', position: 'relative', zIndex: 20 }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>
                        <AlertTriangleIcon size={14} />
                        Known Allergies
                      </label>
                      <div style={{ display: 'flex', gap: '0.5rem', position: 'relative' }}>
                        <div style={{ flex: 1, position: 'relative' }}>
                          <input 
                            type="text" 
                            value={newAllergy} 
                            onChange={e => handleAllergyInput(e.target.value)}
                            onFocus={e => { 
                              e.target.style.borderColor = '#ef4444'; 
                              e.target.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.1)'; 
                              newAllergy.length > 0 && searchAllergens(newAllergy) 
                            }}
                            onBlur={e => { 
                              e.target.style.borderColor = 'rgba(239, 68, 68, 0.2)'; 
                              e.target.style.boxShadow = 'none'; 
                              setTimeout(() => setShowAllergySuggestions(false), 200) 
                            }}
                            placeholder="Type to search allergies..."
                            onKeyPress={e => e.key === 'Enter' && addAllergy()}
                            style={{
                              width: '100%',
                              padding: '0.75rem 1rem',
                              background: 'rgba(239, 68, 68, 0.05)',
                              border: '1px solid rgba(239, 68, 68, 0.2)',
                              borderRadius: '0.75rem',
                              color: '#ffffff',
                              fontSize: '0.9rem',
                              outline: 'none',
                              boxSizing: 'border-box'
                            }}
                          />
                          {/* Allergy Autocomplete Dropdown */}
                          {showAllergySuggestions && allergySuggestions.length > 0 && (
                            <div style={{
                              position: 'absolute',
                              top: 'calc(100% + 4px)',
                              left: 0,
                              right: 0,
                              background: '#1a1f2e',
                              border: '1px solid rgba(239, 68, 68, 0.3)',
                              borderRadius: '0.75rem',
                              maxHeight: '180px',
                              overflowY: 'auto',
                              zIndex: 9999,
                              boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
                            }}>
                              {allergySuggestions.map((s, i) => (
                                <div 
                                  key={i}
                                  onMouseDown={() => selectAllergySuggestion(s.name)}
                                  style={{
                                    padding: '0.65rem 1rem',
                                    cursor: 'pointer',
                                    borderBottom: i < allergySuggestions.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none',
                                    transition: 'background 0.15s',
                                    background: 'transparent'
                                  }}
                                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'}
                                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                                >
                                  <div style={{ fontWeight: '500', color: '#ffffff', fontSize: '0.85rem' }}>{s.name}</div>
                                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>
                                    {s.category} • <span style={{ color: s.severity_typical === 'severe' ? '#ef4444' : s.severity_typical === 'moderate' ? '#f59e0b' : '#22c55e' }}>{s.severity_typical}</span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                        <button 
                          onClick={addAllergy} 
                          style={{
                            padding: '0.75rem 1.25rem',
                            background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%)',
                            border: '1px solid rgba(239, 68, 68, 0.3)',
                            borderRadius: '0.75rem',
                            color: '#ef4444',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                          }}
                          onMouseEnter={e => { e.target.style.background = 'rgba(239, 68, 68, 0.3)' }}
                          onMouseLeave={e => { e.target.style.background = 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%)' }}
                        >Add</button>
                      </div>
                      {profileForm.allergies.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
                          {profileForm.allergies.map((a, i) => (
                            <motion.span 
                              key={i}
                              initial={{ scale: 0.8, opacity: 0 }}
                              animate={{ scale: 1, opacity: 1 }}
                              style={{ 
                                background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(239, 68, 68, 0.1) 100%)',
                                border: '1px solid rgba(239, 68, 68, 0.3)',
                                color: '#fca5a5', 
                                padding: '0.35rem 0.75rem', 
                                borderRadius: '2rem', 
                                fontSize: '0.8rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                fontWeight: '500'
                              }}
                            >
                              {a}
                              <span onClick={() => removeAllergy(i)} style={{ cursor: 'pointer', fontWeight: 'bold', opacity: 0.7 }}>×</span>
                            </motion.span>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Conditions Input */}
                    <div style={{ position: 'relative', zIndex: 10 }}>
                      <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8rem', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '0.5rem', fontWeight: '500' }}>
                        <HeartPulseIcon size={14} />
                        Medical Conditions
                      </label>
                      <div style={{ display: 'flex', gap: '0.5rem', position: 'relative' }}>
                        <div style={{ flex: 1, position: 'relative' }}>
                          <input 
                            type="text" 
                            value={newCondition} 
                            onChange={e => handleConditionInput(e.target.value)}
                            onFocus={e => { 
                              e.target.style.borderColor = '#00d4aa'; 
                              e.target.style.boxShadow = '0 0 0 3px rgba(0, 212, 170, 0.1)'; 
                              newCondition.length > 0 && searchConditions(newCondition) 
                            }}
                            onBlur={e => { 
                              e.target.style.borderColor = 'rgba(0, 212, 170, 0.2)'; 
                              e.target.style.boxShadow = 'none'; 
                              setTimeout(() => setShowConditionSuggestions(false), 200) 
                            }}
                            placeholder="Type to search conditions..."
                            onKeyPress={e => e.key === 'Enter' && addCondition()}
                            style={{
                              width: '100%',
                              padding: '0.75rem 1rem',
                              background: 'rgba(0, 212, 170, 0.05)',
                              border: '1px solid rgba(0, 212, 170, 0.2)',
                              borderRadius: '0.75rem',
                              color: '#ffffff',
                              fontSize: '0.9rem',
                              outline: 'none',
                              boxSizing: 'border-box'
                            }}
                          />
                          {/* Condition Autocomplete Dropdown */}
                          {showConditionSuggestions && conditionSuggestions.length > 0 && (
                            <div style={{
                              position: 'absolute',
                              top: 'calc(100% + 4px)',
                              left: 0,
                              right: 0,
                              background: '#1a1f2e',
                              border: '1px solid rgba(0, 212, 170, 0.3)',
                              borderRadius: '0.75rem',
                              maxHeight: '180px',
                              overflowY: 'auto',
                              zIndex: 9999,
                              boxShadow: '0 8px 32px rgba(0,0,0,0.5)'
                            }}>
                              {conditionSuggestions.map((s, i) => (
                                <div 
                                  key={i}
                                  onMouseDown={() => selectConditionSuggestion(s.name)}
                                  style={{
                                    padding: '0.65rem 1rem',
                                    cursor: 'pointer',
                                    borderBottom: i < conditionSuggestions.length - 1 ? '1px solid rgba(255,255,255,0.05)' : 'none',
                                    transition: 'background 0.15s',
                                    background: 'transparent'
                                  }}
                                  onMouseEnter={e => e.currentTarget.style.background = 'rgba(0, 212, 170, 0.1)'}
                                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                                >
                                  <div style={{ fontWeight: '500', color: '#ffffff', fontSize: '0.85rem' }}>{s.name}</div>
                                  <div style={{ fontSize: '0.65rem', color: '#94a3b8' }}>
                                    {s.category} {s.icd10_code && <span style={{ color: '#00d4aa' }}>• {s.icd10_code}</span>}
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                        <button 
                          onClick={addCondition} 
                          style={{
                            padding: '0.75rem 1.25rem',
                            background: 'linear-gradient(135deg, rgba(0, 212, 170, 0.2) 0%, rgba(0, 212, 170, 0.1) 100%)',
                            border: '1px solid rgba(0, 212, 170, 0.3)',
                            borderRadius: '0.75rem',
                            color: '#00d4aa',
                            fontWeight: '600',
                            cursor: 'pointer',
                            transition: 'all 0.2s'
                          }}
                          onMouseEnter={e => { e.target.style.background = 'rgba(0, 212, 170, 0.3)' }}
                          onMouseLeave={e => { e.target.style.background = 'linear-gradient(135deg, rgba(0, 212, 170, 0.2) 0%, rgba(0, 212, 170, 0.1) 100%)' }}
                        >Add</button>
                      </div>
                      {profileForm.conditions.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '0.75rem' }}>
                          {profileForm.conditions.map((c, i) => (
                            <motion.span 
                              key={i}
                              initial={{ scale: 0.8, opacity: 0 }}
                              animate={{ scale: 1, opacity: 1 }}
                              style={{ 
                                background: 'linear-gradient(135deg, rgba(0, 212, 170, 0.2) 0%, rgba(0, 212, 170, 0.1) 100%)',
                                border: '1px solid rgba(0, 212, 170, 0.3)',
                                color: '#5eead4', 
                                padding: '0.35rem 0.75rem', 
                                borderRadius: '2rem', 
                                fontSize: '0.8rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.5rem',
                                fontWeight: '500'
                              }}
                            >
                              {c}
                              <span onClick={() => removeCondition(i)} style={{ cursor: 'pointer', fontWeight: 'bold', opacity: 0.7 }}>×</span>
                            </motion.span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Modal Footer */}
                <div style={{ 
                  padding: '1.25rem 2rem', 
                  borderTop: '1px solid rgba(255, 255, 255, 0.1)',
                  background: 'rgba(0, 0, 0, 0.2)',
                  display: 'flex', 
                  gap: '1rem' 
                }}>
                  <motion.button 
                    onClick={() => { setShowProfileForm(false); startChat() }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    style={{
                      flex: 1,
                      padding: '0.875rem 1.5rem',
                      background: 'transparent',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      borderRadius: '0.75rem',
                      color: 'rgba(255, 255, 255, 0.7)',
                      fontWeight: '600',
                      cursor: 'pointer',
                      fontSize: '0.95rem',
                      transition: 'all 0.2s'
                    }}
                  >
                    Skip for Now
                  </motion.button>
                  <motion.button 
                    onClick={createProfileAndStart}
                    disabled={!profileForm.name.trim()}
                    whileHover={{ scale: profileForm.name.trim() ? 1.02 : 1 }}
                    whileTap={{ scale: profileForm.name.trim() ? 0.98 : 1 }}
                    style={{
                      flex: 2,
                      padding: '0.875rem 1.5rem',
                      background: profileForm.name.trim() 
                        ? 'linear-gradient(135deg, #00d4aa 0%, #00b894 100%)'
                        : 'rgba(255, 255, 255, 0.1)',
                      border: 'none',
                      borderRadius: '0.75rem',
                      color: profileForm.name.trim() ? '#000' : 'rgba(255, 255, 255, 0.3)',
                      fontWeight: '700',
                      cursor: profileForm.name.trim() ? 'pointer' : 'not-allowed',
                      fontSize: '0.95rem',
                      boxShadow: profileForm.name.trim() ? '0 4px 20px rgba(0, 212, 170, 0.4)' : 'none',
                      transition: 'all 0.2s',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '0.5rem'
                    }}
                  >
                    {loading ? <div className="loading-spinner" style={{ width: '20px', height: '20px' }}></div> : (
                      <>
                        <span>Create Profile & Start</span>
                        <span style={{ fontSize: '1.1rem' }}>→</span>
                      </>
                    )}
                  </motion.button>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
        
        <motion.footer 
          className="footer"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <p>For informational purposes only. Consult a healthcare professional.</p>
        </motion.footer>
      </div>
    )
  }

  return (
    <div className="app-container premium-theme with-sidebar">
      {/* Session Sidebar */}
      {view === 'chat' && phone && (
        <SessionSidebar
          phone={phone}
          currentSessionId={sessionId}
          onNewSession={handleNewSession}
          onLoadSession={handleLoadSession}
          onProfileUpdate={handleProfileUpdate}
          profileData={profileData}
          isOpen={sidebarOpen}
          setIsOpen={setSidebarOpen}
        />
      )}

      {/* Emergency Banner */}
      <AnimatePresence>
        {showEmergency && (
          <motion.div 
            className="emergency-banner"
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
          >
            <div className="emergency-content">
              <AlertIcon />
              <span>Emergency symptoms detected! Please seek immediate medical attention.</span>
            </div>
            <div className="emergency-actions">
              <a href="tel:108" className="emergency-call"><PhoneIcon /> Call 108</a>
              <button onClick={() => setShowEmergency(false)}><XIcon /></button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
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
      
      <motion.header 
        className="header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="logo-container">
          <motion.div 
            className="logo premium-logo" 
            onClick={() => { setView('home'); stopSpeaking() }} 
            style={{ cursor:'pointer' }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <MedicalCrossIcon size={28} />
          </motion.div>
          <h1 className="app-title premium-title">CMC Health</h1>
        </div>
        <p className="app-subtitle">Health Consultation</p>
      </motion.header>
      <motion.main 
        className="main-content"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <motion.div 
          className="glass-card premium-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
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
          {(detectedSymptoms.length > 0 || triageInfo || urgencyLevel !== 'low') && (
            <motion.div 
              className={`symptoms-bar ${triageInfo?.level || urgencyLevel}`}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              transition={{ duration: 0.3 }}
            >
              {/* Urgency Level Badge */}
              <motion.div 
                className={`urgency-badge-dynamic ${urgencyLevel}`}
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                key={urgencyLevel}
              >
                {urgencyLevel === 'emergency' && <span className="urgency-icon">🚨</span>}
                {urgencyLevel === 'urgent' && <span className="urgency-icon">⚠️</span>}
                {urgencyLevel === 'doctor_soon' && <span className="urgency-icon">🩺</span>}
                {urgencyLevel === 'routine' && <span className="urgency-icon">📋</span>}
                {urgencyLevel === 'self_care' && <span className="urgency-icon">✅</span>}
                <span className="urgency-text">
                  {urgencyLevel === 'emergency' ? 'Emergency' : 
                   urgencyLevel === 'urgent' ? 'Urgent' : 
                   urgencyLevel === 'doctor_soon' ? 'See Doctor Soon' :
                   urgencyLevel === 'routine' ? 'Routine' : 'Self Care'}
                </span>
              </motion.div>

              {/* Detected Symptoms */}
              {detectedSymptoms.length > 0 && (
                <div className="detected-symptoms-section">
                  <span className="symptoms-label">DETECTED:</span>
                  <div className="symptom-tags-container">
                    {detectedSymptoms.slice(0, 5).map((s, i) => (
                      <motion.span 
                        key={i} 
                        className="symptom-tag"
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: i * 0.1 }}
                      >
                        {s}
                      </motion.span>
                    ))}
                    {detectedSymptoms.length > 5 && (
                      <span className="symptom-tag more">+{detectedSymptoms.length - 5} more</span>
                    )}
                  </div>
                </div>
              )}

              {urgencyLevel === 'emergency' && (
                <motion.span 
                  className="urgency-badge emergency"
                  animate={{ scale: [1, 1.1, 1] }}
                  transition={{ duration: 0.5, repeat: Infinity }}
                >
                  🚨 Emergency
                </motion.span>
              )}
            </motion.div>
          )}

          {/* Medications Panel - Compact & Collapsible */}
          {suggestedMeds.length > 0 && (
            <motion.div 
              className={`medications-panel ${medsExpanded ? 'expanded' : ''}`}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="medications-header" onClick={() => setMedsExpanded(!medsExpanded)}>
                <PillIconComponent />
                <span>Suggested Medications ({suggestedMeds.length})</span>
                <span className="expand-icon">{medsExpanded ? '▲' : '▼'}</span>
              </div>
              <div className="medications-list">
                {(medsExpanded ? suggestedMeds : suggestedMeds.slice(0, 4)).map((med, i) => (
                  <motion.div 
                    key={i} 
                    className="medication-card"
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.05 }}
                    title={`${med.name || med}${med.warning ? ` - ⚠️ ${med.warning}` : ''}`}
                  >
                    <div className="med-name">{med.name || med}</div>
                    {med.dosage && <div className="med-dosage">{med.dosage}</div>}
                    {med.frequency && <div className="med-frequency">{med.frequency}</div>}
                    {med.warning && <div className="med-warning">⚠️ {med.warning}</div>}
                  </motion.div>
                ))}
                {!medsExpanded && suggestedMeds.length > 4 && (
                  <div className="medication-card" onClick={() => setMedsExpanded(true)} style={{cursor: 'pointer', justifyContent: 'center', alignItems: 'center'}}>
                    <div className="med-name">+{suggestedMeds.length - 4} more</div>
                  </div>
                )}
              </div>
              <div className="medications-disclaimer">
                ⚠️ Consult a doctor before taking any medication
              </div>
            </motion.div>
          )}
          <div className="chat-wrapper">
            <div className="chat-webgl-bg">
              <WebGLBackground contained />
            </div>
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
                <motion.button 
                  className="action-btn send-btn premium-send" 
                  onClick={() => sendMsg()} 
                  disabled={!input.trim()}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <SendIcon />
                </motion.button>
              )}
            </div>
          </div>
        </motion.div>
      </motion.main>
      <motion.footer 
        className="footer"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        <p>For informational purposes only. Consult a healthcare professional.</p>
      </motion.footer>
    </div>
  )
}

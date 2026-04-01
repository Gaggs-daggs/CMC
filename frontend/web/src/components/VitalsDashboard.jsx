/**
 * VitalsDashboard — Google Fit Connected Smartwatch Vitals
 * Shows real-time heart rate, steps, sleep, calories, SpO2 from Google Fit API
 */

import { useState, useEffect, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

// ─── Mini SVG Icons ──────────────────────────────────────────────
const HeartIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20.42 4.58a5.4 5.4 0 0 0-7.65 0L12 5.36l-.77-.78a5.4 5.4 0 0 0-7.65 7.65l1.06 1.06L12 20.64l7.36-7.36 1.06-1.06a5.4 5.4 0 0 0 0-7.64z"/>
  </svg>
)

const StepsIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M4 16v-2.38C4 11.5 2.97 10.5 3 8c.03-2.72 1.49-6 4.5-6C9.37 2 10 3.8 10 5.5c0 3.11-2 5.66-2 8.68V16"/>
    <path d="M20 20v-2.38c0-2.12 1.03-3.12 1-5.62-.03-2.72-1.49-6-4.5-6C14.63 6 14 7.8 14 9.5c0 3.11 2 5.66 2 8.68V20"/>
  </svg>
)

const SleepIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
  </svg>
)

const FireIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>
  </svg>
)

const O2Icon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <path d="M12 6v6l4 2"/>
  </svg>
)

const WatchIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="7"/>
    <polyline points="12 9 12 12 13.5 13.5"/>
    <path d="M16.51 17.35l-.35 3.83a2 2 0 0 1-2 1.82H9.83a2 2 0 0 1-2-1.82l-.35-3.83m.01-10.7.35-3.83A2 2 0 0 1 9.83 1h4.35a2 2 0 0 1 2 1.82l.35 3.83"/>
  </svg>
)

const RefreshIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="23 4 23 10 17 10"/>
    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
  </svg>
)

const DisconnectIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
  </svg>
)

const AlertIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
    <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
  </svg>
)

const GoogleFitLogo = () => (
  <svg width="20" height="20" viewBox="0 0 24 24">
    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" fill="none"/>
    <path d="M16.2 7.8L12 12l-4.2-4.2" stroke="#4285F4" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
    <path d="M12 12l4.2 4.2" stroke="#EA4335" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
    <path d="M12 12L7.8 16.2" stroke="#34A853" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
    <path d="M12 12V6" stroke="#FBBC05" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
  </svg>
)

const ChevronDown = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="6 9 12 15 18 9"/>
  </svg>
)

const ChevronUp = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="18 15 12 9 6 15"/>
  </svg>
)


// ─── Mini Bar Chart ──────────────────────────────────────────────
const MiniBarChart = ({ data, maxVal, color, label }) => {
  if (!data || data.length === 0) return null
  const max = maxVal || Math.max(...data.map(d => d.value || d.steps || 0), 1)
  return (
    <div style={{ display: 'flex', alignItems: 'flex-end', gap: '2px', height: '40px', marginTop: '0.5rem' }}>
      {data.slice(-7).map((d, i) => {
        const val = d.value || d.steps || d.calories || 0
        const h = Math.max((val / max) * 100, 4)
        return (
          <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px' }}>
            <div
              style={{
                width: '100%',
                maxWidth: '18px',
                height: `${h}%`,
                minHeight: '3px',
                background: `linear-gradient(180deg, ${color} 0%, ${color}88 100%)`,
                borderRadius: '3px 3px 1px 1px',
                transition: 'height 0.5s ease',
              }}
              title={`${d.day || ''}: ${val}`}
            />
            <span style={{ fontSize: '0.55rem', color: 'rgba(255,255,255,0.4)' }}>{d.day?.slice(0, 1) || ''}</span>
          </div>
        )
      })}
    </div>
  )
}

// ─── Heart Rate Mini Timeline ────────────────────────────────────
const HeartTimeline = ({ data, color }) => {
  if (!data || data.length < 2) return null
  const values = data.map(d => d.value)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const w = 200
  const h = 35
  const points = data.map((d, i) => {
    const x = (i / (data.length - 1)) * w
    const y = h - ((d.value - min) / range) * (h - 4) - 2
    return `${x},${y}`
  }).join(' ')

  return (
    <svg width="100%" height={h} viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" style={{ marginTop: '0.5rem' }}>
      <defs>
        <linearGradient id="hrGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3"/>
          <stop offset="100%" stopColor={color} stopOpacity="0"/>
        </linearGradient>
      </defs>
      <polygon points={`0,${h} ${points} ${w},${h}`} fill="url(#hrGrad)"/>
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  )
}


// ─── Circular Progress ───────────────────────────────────────────
const CircularProgress = ({ percent, size = 48, strokeWidth = 4, color, children }) => {
  const r = (size - strokeWidth) / 2
  const circ = 2 * Math.PI * r
  const offset = circ - (percent / 100) * circ
  return (
    <div style={{ position: 'relative', width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth={strokeWidth}/>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={strokeWidth}
          strokeDasharray={circ} strokeDashoffset={offset} strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }}
        />
      </svg>
      <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        {children}
      </div>
    </div>
  )
}


// ═══════════════════════════════════════════════════════════════════
// MAIN COMPONENT
// ═══════════════════════════════════════════════════════════════════
export default function VitalsDashboard({ userId, onVitalsUpdate }) {
  const [connected, setConnected] = useState(false)
  const [configured, setConfigured] = useState(null) // null = checking, true = ready, false = needs setup
  const [loading, setLoading] = useState(false)
  const [syncing, setSyncing] = useState(false)
  const [vitals, setVitals] = useState(null)
  const [error, setError] = useState(null)
  const [expanded, setExpanded] = useState(false)
  const [lastSynced, setLastSynced] = useState(null)

  // Check connection status on mount & when URL params change (callback redirect)
  useEffect(() => {
    if (!userId) return
    checkStatus()

    // Check if we just came back from Google OAuth callback
    const params = new URLSearchParams(window.location.search)
    if (params.get('googlefit') === 'connected') {
      setConnected(true)
      setConfigured(true)
      fetchVitals()
      // Clean URL
      window.history.replaceState({}, '', window.location.pathname)
    }
  }, [userId])

  const checkStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/googlefit/status?user_id=${encodeURIComponent(userId)}`)
      const data = await res.json()
      setConnected(data.connected)
      if (data.connected) {
        setConfigured(true)
        fetchVitals()
      } else {
        // Check if the backend has credentials configured
        checkConfigured()
      }
    } catch (e) {
      console.log('Google Fit status check failed:', e)
      setConfigured(false)
    }
  }

  const checkConfigured = async () => {
    try {
      // Peek at auth-url — if it returns 503, credentials aren't set up
      const res = await fetch(
        `${API_BASE}/googlefit/auth-url?user_id=${encodeURIComponent(userId)}&redirect_after=check`
      )
      if (res.status === 503) {
        setConfigured(false)
      } else {
        const data = await res.json()
        setConfigured(!!data.auth_url || data.configured === true)
      }
    } catch (e) {
      setConfigured(false)
    }
  }

  const connectGoogleFit = async () => {
    setLoading(true)
    setError(null)
    try {
      const redirectAfter = window.location.origin + window.location.pathname
      const res = await fetch(
        `${API_BASE}/googlefit/auth-url?user_id=${encodeURIComponent(userId)}&redirect_after=${encodeURIComponent(redirectAfter)}`
      )
      if (res.status === 503) {
        setConfigured(false)
        setError('Google Fit credentials not configured on server.')
        return
      }
      const data = await res.json()

      if (data.auth_url) {
        // Redirect to Google OAuth consent screen
        window.location.href = data.auth_url
      } else {
        setError(data.detail || 'Failed to get auth URL')
      }
    } catch (e) {
      setError('Cannot connect to server. Make sure backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const disconnectGoogleFit = async () => {
    try {
      await fetch(`${API_BASE}/googlefit/disconnect?user_id=${encodeURIComponent(userId)}`, { method: 'POST' })
      setConnected(false)
      setVitals(null)
      setLastSynced(null)
    } catch (e) {
      console.error('Disconnect error:', e)
    }
  }

  const fetchVitals = useCallback(async () => {
    if (!userId) return
    setSyncing(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/googlefit/vitals?user_id=${encodeURIComponent(userId)}`)
      if (res.status === 401) {
        setConnected(false)
        setError('Session expired. Please reconnect Google Fit.')
        return
      }
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || 'Failed to fetch vitals')
      }
      const data = await res.json()
      setVitals(data)
      setLastSynced(new Date())
      // Notify parent component
      if (onVitalsUpdate) {
        onVitalsUpdate({
          heartRate: data.heart_rate?.current,
          spo2: data.spo2?.current,
          steps: data.steps?.today,
          sleep: data.sleep?.last_night_hours,
          calories: data.calories?.today,
          source: 'google_fit'
        })
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setSyncing(false)
    }
  }, [userId, onVitalsUpdate])

  // Auto-refresh every 5 minutes when connected
  useEffect(() => {
    if (!connected) return
    const interval = setInterval(fetchVitals, 300000) // 5 min
    return () => clearInterval(interval)
  }, [connected, fetchVitals])


  // ─── NOT CONFIGURED STATE — show setup instructions ─────────────
  if (configured === false) {
    return (
      <motion.div
        className="vitals-dashboard-container"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.7) 0%, rgba(30, 41, 59, 0.5) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: '16px',
          padding: '1rem 1.25rem',
          margin: '0.75rem 0',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '36px', height: '36px', borderRadius: '10px',
            background: 'linear-gradient(135deg, rgba(100, 116, 139, 0.2) 0%, rgba(100, 116, 139, 0.1) 100%)',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'rgba(255,255,255,0.35)',
          }}>
            <WatchIcon />
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: '600', fontSize: '0.85rem', color: 'rgba(255,255,255,0.6)' }}>Smartwatch Vitals</div>
            <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.35)' }}>
              Set up Google Cloud credentials to connect your smartwatch
            </div>
          </div>
          <a
            href="https://console.cloud.google.com/apis/library/fitness.googleapis.com"
            target="_blank"
            rel="noopener noreferrer"
            style={{
              background: 'rgba(255,255,255,0.06)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              padding: '0.4rem 0.8rem',
              color: 'rgba(255,255,255,0.5)',
              fontSize: '0.72rem',
              fontWeight: '500',
              textDecoration: 'none',
              cursor: 'pointer',
            }}
          >
            Setup Guide
          </a>
        </div>
      </motion.div>
    )
  }

  // ─── STILL CHECKING STATE ──────────────────────────────────────
  if (configured === null && !connected) {
    return null // Don't render anything while checking
  }

  // ─── NOT CONNECTED STATE (credentials configured, just needs OAuth) ───
  if (!connected) {
    return (
      <motion.div
        className="vitals-dashboard-container"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{
          background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.6) 100%)',
          border: '1px solid rgba(255, 255, 255, 0.06)',
          borderRadius: '16px',
          padding: '1.25rem',
          margin: '0.75rem 0',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{
              width: '40px', height: '40px', borderRadius: '12px',
              background: 'linear-gradient(135deg, #4285F4 0%, #34A853 100%)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
              <WatchIcon />
            </div>
            <div>
              <div style={{ fontWeight: '600', fontSize: '0.95rem', color: '#fff' }}>Smartwatch Vitals</div>
              <div style={{ fontSize: '0.75rem', color: 'rgba(255,255,255,0.5)' }}>Connect Google Fit to see real data</div>
            </div>
          </div>
          <motion.button
            onClick={connectGoogleFit}
            disabled={loading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.97 }}
            style={{
              background: 'linear-gradient(135deg, #4285F4 0%, #34A853 100%)',
              border: 'none',
              borderRadius: '10px',
              padding: '0.55rem 1.1rem',
              color: '#fff',
              fontSize: '0.8rem',
              fontWeight: '600',
              cursor: loading ? 'wait' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              opacity: loading ? 0.6 : 1,
            }}
          >
            <GoogleFitLogo />
            {loading ? 'Connecting...' : 'Connect'}
          </motion.button>
        </div>
        {error && (
          <div style={{
            marginTop: '0.75rem', padding: '0.6rem 0.85rem', borderRadius: '10px',
            background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)',
            color: '#fca5a5', fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '0.5rem'
          }}>
            <AlertIcon /> {error}
          </div>
        )}
      </motion.div>
    )
  }


  // ─── CONNECTED STATE — VITALS DASHBOARD ────────────────────────
  const hr = vitals?.heart_rate
  const steps = vitals?.steps
  const sleep = vitals?.sleep
  const cals = vitals?.calories
  const spo2 = vitals?.spo2
  const alerts = vitals?.alerts || []

  return (
    <motion.div
      className="vitals-dashboard-container"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(30, 41, 59, 0.65) 100%)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '16px',
        padding: '1rem 1.25rem',
        margin: '0.75rem 0',
      }}
    >
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: expanded ? '0.75rem' : 0,
        cursor: 'pointer',
      }}
        onClick={() => setExpanded(!expanded)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            width: '36px', height: '36px', borderRadius: '10px',
            background: 'linear-gradient(135deg, rgba(0, 212, 170, 0.2) 0%, rgba(0, 150, 136, 0.15) 100%)',
            border: '1px solid rgba(0, 212, 170, 0.25)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#00d4aa',
          }}>
            <WatchIcon />
          </div>
          <div>
            <div style={{ fontWeight: '600', fontSize: '0.9rem', color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              Health Vitals
              <span style={{
                fontSize: '0.6rem', background: 'rgba(52, 168, 83, 0.2)', color: '#34A853',
                padding: '0.15rem 0.5rem', borderRadius: '8px', fontWeight: '500',
                border: '1px solid rgba(52, 168, 83, 0.25)',
              }}>LIVE</span>
            </div>
            <div style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
              <GoogleFitLogo /> Google Fit
              {lastSynced && ` · ${lastSynced.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`}
            </div>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {/* Quick vital preview when collapsed */}
          {!expanded && hr?.current && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginRight: '0.5rem' }}>
              <span style={{ color: '#ef4444', fontSize: '0.85rem', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <HeartIcon /> {hr.current}
              </span>
              {steps?.today != null && (
                <span style={{ color: '#3b82f6', fontSize: '0.85rem', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                  <StepsIcon /> {steps.today.toLocaleString()}
                </span>
              )}
            </div>
          )}
          <motion.button
            onClick={(e) => { e.stopPropagation(); fetchVitals() }}
            disabled={syncing}
            whileHover={{ rotate: 180 }}
            whileTap={{ scale: 0.8 }}
            style={{
              background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px', padding: '0.35rem', cursor: 'pointer', color: 'rgba(255,255,255,0.6)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
            title="Refresh vitals"
          >
            <RefreshIcon />
          </motion.button>
          <div style={{ color: 'rgba(255,255,255,0.4)' }}>
            {expanded ? <ChevronUp /> : <ChevronDown />}
          </div>
        </div>
      </div>

      {/* Alerts */}
      <AnimatePresence>
        {alerts.length > 0 && expanded && alerts.map((alert, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            style={{
              padding: '0.5rem 0.75rem', borderRadius: '10px', marginBottom: '0.5rem',
              background: alert.type === 'critical' ? 'rgba(239, 68, 68, 0.12)' : alert.type === 'warning' ? 'rgba(245, 158, 11, 0.12)' : 'rgba(59, 130, 246, 0.1)',
              border: `1px solid ${alert.type === 'critical' ? 'rgba(239, 68, 68, 0.25)' : alert.type === 'warning' ? 'rgba(245, 158, 11, 0.25)' : 'rgba(59, 130, 246, 0.2)'}`,
              color: alert.type === 'critical' ? '#fca5a5' : alert.type === 'warning' ? '#fcd34d' : '#93c5fd',
              fontSize: '0.75rem',
              display: 'flex', alignItems: 'center', gap: '0.5rem',
            }}
          >
            <AlertIcon /> {alert.message}
          </motion.div>
        ))}
      </AnimatePresence>

      {/* Vitals Grid — Expanded */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
          >
            {syncing && !vitals ? (
              <div style={{ textAlign: 'center', padding: '2rem 0', color: 'rgba(255,255,255,0.5)', fontSize: '0.85rem' }}>
                <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
                  <RefreshIcon />
                </motion.div>
                <div style={{ marginTop: '0.5rem' }}>Syncing vitals from Google Fit...</div>
              </div>
            ) : vitals ? (
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
                gap: '0.65rem',
              }}>
                {/* Heart Rate Card */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.05 }}
                  style={{
                    background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.08) 0%, rgba(239, 68, 68, 0.03) 100%)',
                    border: '1px solid rgba(239, 68, 68, 0.15)',
                    borderRadius: '14px', padding: '0.85rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                    <span style={{ color: '#ef4444', display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', fontWeight: '500' }}>
                      <HeartIcon /> Heart Rate
                    </span>
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#fff' }}>
                    {hr?.current ?? '--'}
                    <span style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', fontWeight: '400' }}> bpm</span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.25rem' }}>
                    <span style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.4)' }}>
                      {hr?.min ? `${hr.min}` : '--'} min
                    </span>
                    <span style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.4)' }}>
                      {hr?.max ? `${hr.max}` : '--'} max
                    </span>
                  </div>
                  {hr?.timeline && <HeartTimeline data={hr.timeline} color="#ef4444" />}
                  {hr?.current && (
                    <div style={{
                      marginTop: '0.35rem', fontSize: '0.65rem', fontWeight: '500',
                      color: hr.current >= 60 && hr.current <= 100 ? '#34d399' : '#fbbf24',
                    }}>
                      {hr.current >= 60 && hr.current <= 100 ? 'Normal' : hr.current < 60 ? 'Low' : 'Elevated'}
                    </div>
                  )}
                </motion.div>

                {/* Steps Card */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 }}
                  style={{
                    background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(59, 130, 246, 0.03) 100%)',
                    border: '1px solid rgba(59, 130, 246, 0.15)',
                    borderRadius: '14px', padding: '0.85rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                    <span style={{ color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', fontWeight: '500' }}>
                      <StepsIcon /> Steps
                    </span>
                    {steps?.goal_percent != null && (
                      <CircularProgress percent={steps.goal_percent} size={32} strokeWidth={3} color="#3b82f6">
                        <span style={{ fontSize: '0.5rem', fontWeight: '700', color: '#3b82f6' }}>{steps.goal_percent}%</span>
                      </CircularProgress>
                    )}
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#fff' }}>
                    {steps?.today?.toLocaleString() ?? '--'}
                  </div>
                  <div style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.4)', marginTop: '0.15rem' }}>
                    Goal: 10,000 · Avg: {steps?.average?.toLocaleString() ?? '--'}
                  </div>
                  {steps?.daily && <MiniBarChart data={steps.daily} maxVal={12000} color="#3b82f6" />}
                </motion.div>

                {/* Sleep Card */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.15 }}
                  style={{
                    background: 'linear-gradient(135deg, rgba(139, 92, 246, 0.08) 0%, rgba(139, 92, 246, 0.03) 100%)',
                    border: '1px solid rgba(139, 92, 246, 0.15)',
                    borderRadius: '14px', padding: '0.85rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                    <span style={{ color: '#8b5cf6', display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', fontWeight: '500' }}>
                      <SleepIcon /> Sleep
                    </span>
                    {sleep?.sleep_score != null && (
                      <CircularProgress percent={sleep.sleep_score} size={32} strokeWidth={3} color="#8b5cf6">
                        <span style={{ fontSize: '0.5rem', fontWeight: '700', color: '#8b5cf6' }}>{sleep.sleep_score}</span>
                      </CircularProgress>
                    )}
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#fff' }}>
                    {sleep?.last_night_hours ?? '--'}
                    <span style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', fontWeight: '400' }}> hrs</span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.3rem', flexWrap: 'wrap' }}>
                    {sleep?.deep_sleep_minutes != null && (
                      <span style={{
                        fontSize: '0.6rem', padding: '0.15rem 0.4rem', borderRadius: '6px',
                        background: 'rgba(139, 92, 246, 0.15)', color: '#c4b5fd',
                      }}>
                        Deep: {Math.round(sleep.deep_sleep_minutes / 60 * 10) / 10}h
                      </span>
                    )}
                    {sleep?.rem_sleep_minutes != null && (
                      <span style={{
                        fontSize: '0.6rem', padding: '0.15rem 0.4rem', borderRadius: '6px',
                        background: 'rgba(96, 165, 250, 0.15)', color: '#93c5fd',
                      }}>
                        REM: {Math.round(sleep.rem_sleep_minutes / 60 * 10) / 10}h
                      </span>
                    )}
                    {sleep?.light_sleep_minutes != null && (
                      <span style={{
                        fontSize: '0.6rem', padding: '0.15rem 0.4rem', borderRadius: '6px',
                        background: 'rgba(255, 255, 255, 0.08)', color: 'rgba(255,255,255,0.5)',
                      }}>
                        Light: {Math.round(sleep.light_sleep_minutes / 60 * 10) / 10}h
                      </span>
                    )}
                  </div>
                </motion.div>

                {/* Calories Card */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 }}
                  style={{
                    background: 'linear-gradient(135deg, rgba(245, 158, 11, 0.08) 0%, rgba(245, 158, 11, 0.03) 100%)',
                    border: '1px solid rgba(245, 158, 11, 0.15)',
                    borderRadius: '14px', padding: '0.85rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.4rem' }}>
                    <span style={{ color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', fontWeight: '500' }}>
                      <FireIcon /> Calories
                    </span>
                  </div>
                  <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#fff' }}>
                    {cals?.today?.toLocaleString() ?? '--'}
                    <span style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', fontWeight: '400' }}> kcal</span>
                  </div>
                  <div style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.4)', marginTop: '0.15rem' }}>
                    Avg: {cals?.average?.toLocaleString() ?? '--'} kcal/day
                  </div>
                  {cals?.daily && <MiniBarChart data={cals.daily} color="#f59e0b" />}
                </motion.div>

                {/* SpO2 Card (always show, with placeholder if no data) */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.25 }}
                  style={{
                    background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(6, 182, 212, 0.03) 100%)',
                    border: '1px solid rgba(6, 182, 212, 0.15)',
                    borderRadius: '14px', padding: '0.85rem',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginBottom: '0.4rem' }}>
                    <span style={{ color: '#06b6d4', display: 'flex', alignItems: 'center', gap: '0.35rem', fontSize: '0.75rem', fontWeight: '500' }}>
                      <O2Icon /> SpO2
                    </span>
                  </div>
                  {spo2?.available ? (
                    <>
                      <div style={{ fontSize: '1.5rem', fontWeight: '700', color: '#fff' }}>
                        {spo2?.current ?? '--'}
                        <span style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.4)', fontWeight: '400' }}>%</span>
                      </div>
                      <div style={{
                        marginTop: '0.25rem', fontSize: '0.65rem', fontWeight: '500',
                        color: spo2?.current >= 95 ? '#34d399' : spo2?.current >= 90 ? '#fbbf24' : '#ef4444',
                      }}>
                        {spo2?.current >= 95 ? 'Normal' : spo2?.current >= 90 ? 'Low - Monitor' : 'Critical'}
                      </div>
                    </>
                  ) : (
                    <>
                      <div style={{ fontSize: '1.5rem', fontWeight: '700', color: 'rgba(255,255,255,0.3)' }}>
                        --<span style={{ fontSize: '0.7rem', color: 'rgba(255,255,255,0.2)', fontWeight: '400' }}>%</span>
                      </div>
                      <div style={{ marginTop: '0.25rem', fontSize: '0.6rem', color: 'rgba(255,255,255,0.3)' }}>
                        Not available from watch
                      </div>
                    </>
                  )}
                </motion.div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '1.5rem 0', color: 'rgba(255,255,255,0.4)', fontSize: '0.8rem' }}>
                No vitals data yet. Tap refresh to sync.
              </div>
            )}

            {/* Footer */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              marginTop: '0.75rem', paddingTop: '0.6rem',
              borderTop: '1px solid rgba(255,255,255,0.06)',
            }}>
              <div style={{ fontSize: '0.65rem', color: 'rgba(255,255,255,0.3)' }}>
                Data from your smartwatch via Google Fit
              </div>
              <motion.button
                onClick={disconnectGoogleFit}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                style={{
                  background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)',
                  borderRadius: '8px', padding: '0.3rem 0.65rem', cursor: 'pointer',
                  color: '#fca5a5', fontSize: '0.7rem', fontWeight: '500',
                  display: 'flex', alignItems: 'center', gap: '0.35rem',
                }}
              >
                <DisconnectIcon /> Disconnect
              </motion.button>
            </div>

            {/* Error */}
            {error && (
              <div style={{
                marginTop: '0.5rem', padding: '0.5rem 0.75rem', borderRadius: '10px',
                background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.15)',
                color: '#fca5a5', fontSize: '0.72rem', display: 'flex', alignItems: 'center', gap: '0.5rem',
              }}>
                <AlertIcon /> {error}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}

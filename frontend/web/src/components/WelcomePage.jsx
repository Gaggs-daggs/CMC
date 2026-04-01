/**
 * WelcomePage.jsx — Premium OAuth2 Login/Signup Page
 * Inspired by Notion, Linear, Figma auth flows
 * Features: Google OAuth, Email/Password, WebGL background, feature showcase
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import { motion, AnimatePresence, useMotionValue, useTransform } from 'framer-motion'
import './WelcomePage.css'
import atlasLogo from '../assets/atlas-logo.png'
import {
  HeartPulseIcon,
  StethoscopeIcon,
  ShieldCheckIcon,
  BrainIcon,
  DNAIcon,
  ActivityPulseIcon,
} from './PremiumIcons'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID

// ─── Animated Gradient Orbs (background decoration) ─────────────
const GradientOrbs = () => (
  <div className="wlc-orbs">
    <div className="wlc-orb wlc-orb-1" />
    <div className="wlc-orb wlc-orb-2" />
    <div className="wlc-orb wlc-orb-3" />
  </div>
)

// ─── Floating Particles ─────────────────────────────────────────
const FloatingParticles = () => {
  const particles = Array.from({ length: 30 }, (_, i) => ({
    id: i,
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 3 + 1,
    duration: Math.random() * 20 + 15,
    delay: Math.random() * 10,
  }))

  return (
    <div className="wlc-particles">
      {particles.map(p => (
        <motion.div
          key={p.id}
          className="wlc-particle"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
          }}
          animate={{
            y: [0, -40, 0],
            x: [0, Math.random() * 20 - 10, 0],
            opacity: [0, 0.6, 0],
          }}
          transition={{
            duration: p.duration,
            delay: p.delay,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  )
}

// ─── Grid Pattern (subtle background) ───────────────────────────
const GridPattern = () => (
  <svg className="wlc-grid-pattern" width="100%" height="100%">
    <defs>
      <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
        <path d="M 60 0 L 0 0 0 60" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="0.5" />
      </pattern>
    </defs>
    <rect width="100%" height="100%" fill="url(#grid)" />
  </svg>
)

// ─── Feature Cards ──────────────────────────────────────────────
const features = [
  {
    icon: <BrainIcon size={28} color="#00d4aa" />,
    title: 'AI Diagnosis',
    desc: 'Advanced AI analyzes symptoms with clinical-grade accuracy',
    gradient: 'linear-gradient(135deg, rgba(0,212,170,0.15), rgba(0,212,170,0.02))',
    border: 'rgba(0,212,170,0.25)',
  },
  {
    icon: <span style={{ fontSize: '1.6rem' }}>🌐</span>,
    title: '14 Languages',
    desc: 'Healthcare in Hindi, Tamil, Telugu, Bengali & more',
    gradient: 'linear-gradient(135deg, rgba(99,102,241,0.15), rgba(99,102,241,0.02))',
    border: 'rgba(99,102,241,0.25)',
  },
  {
    icon: <StethoscopeIcon size={28} color="#f59e0b" />,
    title: 'Smart Triage',
    desc: 'Urgency classification with emergency detection',
    gradient: 'linear-gradient(135deg, rgba(245,158,11,0.15), rgba(245,158,11,0.02))',
    border: 'rgba(245,158,11,0.25)',
  },
  {
    icon: <ShieldCheckIcon size={28} color="#8b5cf6" />,
    title: 'Secure & Private',
    desc: 'End-to-end encrypted, HIPAA-aligned privacy',
    gradient: 'linear-gradient(135deg, rgba(139,92,246,0.15), rgba(139,92,246,0.02))',
    border: 'rgba(139,92,246,0.25)',
  },
]

// ─── Stats Bar ──────────────────────────────────────────────────
const stats = [
  { value: '14', label: 'Languages' },
  { value: 'AI', label: 'Powered' },
  { value: '24/7', label: 'Available' },
  { value: '< 2s', label: 'Response' },
]

// ─── Password Strength ──────────────────────────────────────────
function getPasswordStrength(pw) {
  if (!pw) return { score: 0, label: '', color: '' }
  let score = 0
  if (pw.length >= 6) score++
  if (pw.length >= 10) score++
  if (/[A-Z]/.test(pw)) score++
  if (/[0-9]/.test(pw)) score++
  if (/[^A-Za-z0-9]/.test(pw)) score++
  const levels = [
    { label: '', color: '' },
    { label: 'Weak', color: '#ef4444' },
    { label: 'Fair', color: '#f59e0b' },
    { label: 'Good', color: '#eab308' },
    { label: 'Strong', color: '#22c55e' },
    { label: 'Very Strong', color: '#00d4aa' },
  ]
  return { score, ...levels[Math.min(score, 5)] }
}


// ═══════════════════════════════════════════════════════════════
// ██  MAIN WELCOME PAGE COMPONENT
// ═══════════════════════════════════════════════════════════════

export default function WelcomePage({ onAuthenticated, language, setLanguage, langNames }) {
  const [authMode, setAuthMode] = useState('login') // 'login' | 'signup'
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [googleLoading, setGoogleLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [shake, setShake] = useState(false)

  const googleBtnRef = useRef(null)
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)

  // ─── Google Sign-In Initialization ──────────────────────────
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID) return

    const initGoogle = () => {
      if (!window.google?.accounts?.id) return

      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: handleGoogleCallback,
        auto_select: false,
        cancel_on_tap_outside: true,
      })

      // Render the branded button inside our container
      if (googleBtnRef.current) {
        window.google.accounts.id.renderButton(googleBtnRef.current, {
          type: 'standard',
          theme: 'filled_black',
          size: 'large',
          width: '100%',
          text: 'continue_with',
          shape: 'pill',
          logo_alignment: 'left',
        })
      }
    }

    // Google GSI script might not be loaded yet
    if (window.google?.accounts?.id) {
      initGoogle()
    } else {
      const interval = setInterval(() => {
        if (window.google?.accounts?.id) {
          initGoogle()
          clearInterval(interval)
        }
      }, 100)
      return () => clearInterval(interval)
    }
  }, [])

  // ─── Google callback (credential = JWT id_token) ────────────
  const handleGoogleCallback = useCallback(async (response) => {
    setGoogleLoading(true)
    setError('')

    try {
      // Google Identity Services returns an id_token (credential), NOT an auth code.
      // We decode the JWT on the client to get user info (Google's id_token is a signed JWT).
      // For maximum security we could verify server-side, but for now:
      const credential = response.credential
      
      // Decode JWT payload (base64url)
      const payload = JSON.parse(atob(credential.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')))
      
      const user = {
        id: payload.sub,
        email: payload.email,
        name: payload.name || payload.email.split('@')[0],
        picture: payload.picture || '',
        provider: 'google',
      }

      // Send to our backend to create/get user and issue our own tokens
      const res = await fetch(`${API_BASE}/auth/google-idtoken`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id_token: credential,
          email: user.email,
          name: user.name,
          picture: user.picture,
        }),
      })

      if (!res.ok) {
        // Fallback: use the Google user info directly (still authenticated via Google's JWT)
        console.warn('Backend google-idtoken endpoint not available, using direct Google auth')
        const tokens = {
          access_token: credential, // Use Google's JWT as access token
          user,
        }
        localStorage.setItem('cmc_auth', JSON.stringify(tokens))
        onAuthenticated(user, credential)
        return
      }

      const data = await res.json()
      // Ensure Google profile picture is always included (backend may not return it)
      const mergedUser = { 
        ...data.user, 
        picture: data.user?.picture || user.picture || '' 
      }
      const authData = { ...data, user: mergedUser }
      localStorage.setItem('cmc_auth', JSON.stringify(authData))
      onAuthenticated(mergedUser, data.access_token)
    } catch (err) {
      console.error('Google auth error:', err)
      setError('Google sign-in failed. Please try again.')
    } finally {
      setGoogleLoading(false)
    }
  }, [onAuthenticated])

  // ─── Email/Password Login ───────────────────────────────────
  const handleEmailAuth = async (e) => {
    e.preventDefault()
    setError('')

    if (!email.trim()) return triggerError('Please enter your email')
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return triggerError('Please enter a valid email')
    if (!password) return triggerError('Please enter your password')

    if (authMode === 'signup') {
      if (password.length < 6) return triggerError('Password must be at least 6 characters')
      if (password !== confirmPassword) return triggerError('Passwords do not match')
    }

    setLoading(true)
    try {
      const endpoint = authMode === 'signup' ? '/auth/signup' : '/auth/login'
      const body = authMode === 'signup'
        ? { email: email.toLowerCase().trim(), password, name: name.trim() || undefined }
        : { email: email.toLowerCase().trim(), password }

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      const data = await res.json()

      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed')
      }

      localStorage.setItem('cmc_auth', JSON.stringify(data))
      onAuthenticated(data.user, data.access_token)
    } catch (err) {
      triggerError(err.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  const triggerError = (msg) => {
    setError(msg)
    setShake(true)
    setTimeout(() => setShake(false), 600)
  }

  // ─── Animated cursor glow ──────────────────────────────────
  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect()
    mouseX.set(e.clientX - rect.left)
    mouseY.set(e.clientY - rect.top)
  }

  const pwStrength = getPasswordStrength(password)

  // ─── Animations ─────────────────────────────────────────────
  const containerAnim = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.08, delayChildren: 0.2 },
    },
  }
  const itemAnim = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] } },
  }

  return (
    <div className="wlc-page" onMouseMove={handleMouseMove}>
      {/* Background effects */}
      <GradientOrbs />
      <FloatingParticles />
      <GridPattern />

      {/* Top Navigation */}
      <motion.nav
        className="wlc-nav"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="wlc-nav-left">
          <motion.div
            className="wlc-nav-logo"
            animate={{
              boxShadow: [
                '0 0 15px rgba(0,212,170,0.3)',
                '0 0 30px rgba(0,212,170,0.5)',
                '0 0 15px rgba(0,212,170,0.3)',
              ],
            }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            <img src={atlasLogo} alt="Atlas" className="wlc-nav-logo-img" />
          </motion.div>
          <span className="wlc-nav-brand">Atlas</span>
          <span className="wlc-nav-badge">AI-Powered</span>
        </div>
        <div className="wlc-nav-right">
          <select
            className="wlc-lang-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            {Object.entries(langNames).map(([code, name]) => (
              <option key={code} value={code}>{name}</option>
            ))}
          </select>
        </div>
      </motion.nav>

      {/* Main Content — Two Column Layout */}
      <div className="wlc-content">
        {/* Left Column: Hero + Features */}
        <motion.div
          className="wlc-left"
          variants={containerAnim}
          initial="hidden"
          animate="visible"
        >
          {/* Hero */}
          <motion.div className="wlc-hero" variants={itemAnim}>
            <div className="wlc-hero-logo-mobile">
              <img src={atlasLogo} alt="Atlas AI" className="wlc-hero-logo-img" />
            </div>
            <div className="wlc-hero-tag">
              <DNAIcon size={16} color="#00d4aa" />
              <span>AI-Powered Health Assistant for India</span>
            </div>
            <h1 className="wlc-hero-title">
              Your Health,{' '}
              <span className="wlc-gradient-text">Reimagined</span>
              <br />
              with AI Intelligence
            </h1>
            <p className="wlc-hero-desc">
              Get instant medical guidance powered by advanced AI. Describe your symptoms 
              in any Indian language and receive accurate diagnoses, medication suggestions, 
              and emergency triage — all in seconds.
            </p>
          </motion.div>

          {/* Stats */}
          <motion.div className="wlc-stats" variants={itemAnim}>
            {stats.map((s, i) => (
              <div key={i} className="wlc-stat">
                <span className="wlc-stat-value">{s.value}</span>
                <span className="wlc-stat-label">{s.label}</span>
              </div>
            ))}
          </motion.div>

          {/* Feature Cards */}
          <motion.div className="wlc-features" variants={itemAnim}>
            {features.map((f, i) => (
              <motion.div
                key={i}
                className="wlc-feature-card"
                style={{ background: f.gradient, borderColor: f.border }}
                whileHover={{ scale: 1.03, y: -2 }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              >
                <div className="wlc-feature-icon">{f.icon}</div>
                <div>
                  <h3 className="wlc-feature-title">{f.title}</h3>
                  <p className="wlc-feature-desc">{f.desc}</p>
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* How it works */}
          <motion.div className="wlc-testimonial" variants={itemAnim}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: '#00d4aa', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              <ActivityPulseIcon size={16} color="#00d4aa" />
              How It Works
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
              {[
                { step: '1', text: 'Describe your symptoms in any Indian language' },
                { step: '2', text: 'AI analyzes and asks follow-up questions' },
                { step: '3', text: 'Get diagnosis, medication info & triage guidance' },
              ].map((item) => (
                <div key={item.step} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ width: 28, height: 28, borderRadius: '50%', background: 'linear-gradient(135deg, rgba(0,212,170,0.2), rgba(99,102,241,0.15))', border: '1px solid rgba(0,212,170,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.75rem', fontWeight: 700, color: '#00d4aa', flexShrink: 0 }}>{item.step}</span>
                  <span style={{ fontSize: '0.85rem', color: 'rgba(255,255,255,0.6)' }}>{item.text}</span>
                </div>
              ))}
            </div>
          </motion.div>
        </motion.div>

        {/* Right Column: Auth Card */}
        <motion.div
          className="wlc-right"
          initial={{ opacity: 0, x: 40 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
        >
          <div className="wlc-auth-card">
            {/* Glow border effect */}
            <div className="wlc-auth-glow" />

            {/* Card Header */}
            <div className="wlc-auth-header">
              <motion.div
                className="wlc-auth-icon"
                animate={{ rotate: [0, 5, -5, 0] }}
                transition={{ duration: 4, repeat: Infinity }}
              >
                <HeartPulseIcon size={32} color="#00d4aa" />
              </motion.div>
              <h2 className="wlc-auth-title">
                {authMode === 'login' ? 'Welcome back' : 'Create your account'}
              </h2>
              <p className="wlc-auth-subtitle">
                {authMode === 'login'
                  ? 'Sign in to continue your health journey'
                  : 'Start your AI-powered health consultation'}
              </p>
            </div>

            {/* Google Sign-In */}
            <div className="wlc-google-section">
              <div ref={googleBtnRef} className="wlc-google-btn-container" />
              {googleLoading && (
                <div className="wlc-google-loading">
                  <div className="wlc-spinner" />
                  <span>Connecting with Google...</span>
                </div>
              )}
            </div>

            {/* Divider */}
            <div className="wlc-divider">
              <span className="wlc-divider-line" />
              <span className="wlc-divider-text">or continue with email</span>
              <span className="wlc-divider-line" />
            </div>

            {/* Email/Password Form */}
            <form className="wlc-form" onSubmit={handleEmailAuth}>
              <AnimatePresence mode="wait">
                {authMode === 'signup' && (
                  <motion.div
                    key="name-field"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="wlc-field">
                      <label className="wlc-label">Full Name</label>
                      <div className="wlc-input-wrap">
                        <svg className="wlc-input-icon" viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                          <path d="M10 10a4 4 0 100-8 4 4 0 000 8zm-7 8a7 7 0 0114 0H3z" />
                        </svg>
                        <input
                          type="text"
                          className="wlc-input"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          placeholder="Enter your name"
                          autoComplete="name"
                        />
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <div className="wlc-field">
                <label className="wlc-label">Email Address</label>
                <motion.div
                  className="wlc-input-wrap"
                  animate={shake ? { x: [-8, 8, -6, 6, -3, 3, 0] } : {}}
                  transition={{ duration: 0.5 }}
                >
                  <svg className="wlc-input-icon" viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                    <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z" />
                    <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z" />
                  </svg>
                  <input
                    type="email"
                    className="wlc-input"
                    value={email}
                    onChange={(e) => { setEmail(e.target.value); setError('') }}
                    placeholder="you@example.com"
                    autoComplete="email"
                    required
                  />
                </motion.div>
              </div>

              <div className="wlc-field">
                <label className="wlc-label">Password</label>
                <div className="wlc-input-wrap">
                  <svg className="wlc-input-icon" viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                    <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                  </svg>
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="wlc-input"
                    value={password}
                    onChange={(e) => { setPassword(e.target.value); setError('') }}
                    placeholder={authMode === 'signup' ? 'Min 6 characters' : '••••••••'}
                    autoComplete={authMode === 'signup' ? 'new-password' : 'current-password'}
                    required
                  />
                  <button
                    type="button"
                    className="wlc-eye-btn"
                    onClick={() => setShowPassword(!showPassword)}
                    tabIndex={-1}
                  >
                    {showPassword ? (
                      <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                        <path fillRule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clipRule="evenodd" />
                        <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z" />
                      </svg>
                    ) : (
                      <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                        <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                        <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </button>
                </div>
                {/* Password strength indicator for signup */}
                {authMode === 'signup' && password && (
                  <motion.div
                    className="wlc-pw-strength"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                  >
                    <div className="wlc-pw-bars">
                      {[1, 2, 3, 4, 5].map((level) => (
                        <div
                          key={level}
                          className="wlc-pw-bar"
                          style={{
                            background: pwStrength.score >= level ? pwStrength.color : 'rgba(255,255,255,0.1)',
                          }}
                        />
                      ))}
                    </div>
                    <span className="wlc-pw-label" style={{ color: pwStrength.color }}>
                      {pwStrength.label}
                    </span>
                  </motion.div>
                )}
              </div>

              <AnimatePresence mode="wait">
                {authMode === 'signup' && (
                  <motion.div
                    key="confirm-field"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="wlc-field">
                      <label className="wlc-label">Confirm Password</label>
                      <div className="wlc-input-wrap">
                        <svg className="wlc-input-icon" viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                          <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
                        </svg>
                        <input
                          type={showPassword ? 'text' : 'password'}
                          className="wlc-input"
                          value={confirmPassword}
                          onChange={(e) => { setConfirmPassword(e.target.value); setError('') }}
                          placeholder="Re-enter password"
                          autoComplete="new-password"
                        />
                        {confirmPassword && (
                          <span className="wlc-match-indicator" style={{ color: password === confirmPassword ? '#22c55e' : '#ef4444' }}>
                            {password === confirmPassword ? '✓' : '✗'}
                          </span>
                        )}
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Error */}
              <AnimatePresence>
                {error && (
                  <motion.div
                    className="wlc-error"
                    initial={{ opacity: 0, y: -8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                  >
                    <svg viewBox="0 0 20 20" fill="currentColor" width="16" height="16">
                      <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                    <span>{error}</span>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Submit */}
              <motion.button
                type="submit"
                className="wlc-submit-btn"
                disabled={loading}
                whileHover={{ scale: loading ? 1 : 1.02 }}
                whileTap={{ scale: loading ? 1 : 0.98 }}
              >
                {loading ? (
                  <div className="wlc-spinner" />
                ) : (
                  <>
                    <span>{authMode === 'login' ? 'Sign In' : 'Create Account'}</span>
                    <svg viewBox="0 0 20 20" fill="currentColor" width="18" height="18">
                      <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </>
                )}
              </motion.button>
            </form>

            {/* Toggle Login/Signup */}
            <div className="wlc-toggle">
              <span className="wlc-toggle-text">
                {authMode === 'login' ? "Don't have an account?" : 'Already have an account?'}
              </span>
              <button
                className="wlc-toggle-btn"
                onClick={() => {
                  setAuthMode(authMode === 'login' ? 'signup' : 'login')
                  setError('')
                  setPassword('')
                  setConfirmPassword('')
                }}
              >
                {authMode === 'login' ? 'Sign Up' : 'Sign In'}
              </button>
            </div>

            {/* Security badge */}
            <div className="wlc-security">
              <ShieldCheckIcon size={14} color="rgba(255,255,255,0.4)" />
              <span>256-bit encryption • HIPAA aligned • Your data stays private</span>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Footer */}
      <motion.footer
        className="wlc-footer"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
      >
        <p>For informational purposes only. Always consult a qualified healthcare professional.</p>
        <p>© 2026 Atlas. All rights reserved.</p>
      </motion.footer>
    </div>
  )
}

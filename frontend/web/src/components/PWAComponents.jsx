// ============================================================
// Atlas — PWA Install Prompt + Offline Banner + SW Update
// Lightweight components for PWA lifecycle events.
// ============================================================
import { useState, useEffect, useCallback } from 'react'
import './PWAComponents.css'

// ─── "Add to Home Screen" Install Prompt ───────────────────
export function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null)
  const [show, setShow] = useState(false)

  useEffect(() => {
    const handler = (e) => {
      e.preventDefault()
      setDeferredPrompt(e)
      // Don't nag immediately — wait 30 seconds
      setTimeout(() => setShow(true), 30000)
    }
    window.addEventListener('beforeinstallprompt', handler)
    return () => window.removeEventListener('beforeinstallprompt', handler)
  }, [])

  const handleInstall = useCallback(async () => {
    if (!deferredPrompt) return
    deferredPrompt.prompt()
    const { outcome } = await deferredPrompt.userChoice
    if (outcome === 'accepted') {
      console.log('[PWA] User accepted install')
    }
    setDeferredPrompt(null)
    setShow(false)
  }, [deferredPrompt])

  const handleDismiss = useCallback(() => {
    setShow(false)
    // Don't show again for 7 days
    localStorage.setItem('cmc_install_dismissed', Date.now().toString())
  }, [])

  // Respect dismiss cooldown
  useEffect(() => {
    const dismissed = localStorage.getItem('cmc_install_dismissed')
    if (dismissed && Date.now() - parseInt(dismissed) < 7 * 24 * 60 * 60 * 1000) {
      setShow(false)
    }
  }, [])

  if (!show) return null

  return (
    <div className="pwa-install-banner">
      <div className="pwa-install-icon">📲</div>
      <div className="pwa-install-text">
        <strong>Install Atlas</strong>
        <span>Quick access from your home screen — works offline!</span>
      </div>
      <div className="pwa-install-actions">
        <button className="pwa-install-btn" onClick={handleInstall}>Install</button>
        <button className="pwa-dismiss-btn" onClick={handleDismiss}>Later</button>
      </div>
    </div>
  )
}

// ─── Offline / Online Banner ───────────────────────────────
export function OfflineIndicator() {
  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [showReconnected, setShowReconnected] = useState(false)

  useEffect(() => {
    const goOnline = () => {
      setIsOnline(true)
      setShowReconnected(true)
      setTimeout(() => setShowReconnected(false), 3000)
    }
    const goOffline = () => {
      setIsOnline(false)
      setShowReconnected(false)
    }

    window.addEventListener('online', goOnline)
    window.addEventListener('offline', goOffline)
    return () => {
      window.removeEventListener('online', goOnline)
      window.removeEventListener('offline', goOffline)
    }
  }, [])

  if (isOnline && !showReconnected) return null

  return (
    <div className={`pwa-offline-banner ${isOnline ? 'reconnected' : 'offline'}`}>
      {isOnline ? (
        <>✅ Back online — syncing your data</>
      ) : (
        <>📡 You're offline — cached data is available</>
      )}
    </div>
  )
}

// ─── "New Version Available" Update Banner ─────────────────
export function UpdateBanner() {
  const [showUpdate, setShowUpdate] = useState(false)

  useEffect(() => {
    const handler = () => setShowUpdate(true)
    window.addEventListener('sw-update-available', handler)
    return () => window.removeEventListener('sw-update-available', handler)
  }, [])

  if (!showUpdate) return null

  return (
    <div className="pwa-update-banner">
      <span>🆕 A new version of Atlas is available.</span>
      <button
        className="pwa-update-btn"
        onClick={() => window.location.reload()}
      >
        Refresh
      </button>
    </div>
  )
}

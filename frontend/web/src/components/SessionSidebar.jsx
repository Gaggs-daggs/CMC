import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

// Icons
const PlusIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"></line>
    <line x1="5" y1="12" x2="19" y2="12"></line>
  </svg>
)

const ChatIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
  </svg>
)

const TrashIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"></polyline>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
  </svg>
)

const EditIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
  </svg>
)

const UserIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
)

const ChevronIcon = ({ open }) => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ transform: open ? 'rotate(180deg)' : 'rotate(0deg)', transition: 'transform 0.2s' }}>
    <polyline points="6 9 12 15 18 9"></polyline>
  </svg>
)

const MenuIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="3" y1="12" x2="21" y2="12"></line>
    <line x1="3" y1="6" x2="21" y2="6"></line>
    <line x1="3" y1="18" x2="21" y2="18"></line>
  </svg>
)

const CloseIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  </svg>
)

const SaveIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
    <polyline points="17 21 17 13 7 13 7 21"></polyline>
    <polyline points="7 3 7 8 15 8"></polyline>
  </svg>
)

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export default function SessionSidebar({ 
  phone, 
  currentSessionId, 
  onNewSession, 
  onLoadSession,
  onProfileUpdate,
  profileData,
  isOpen,
  setIsOpen
}) {
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(false)
  const [showProfileEdit, setShowProfileEdit] = useState(false)
  const [profileForm, setProfileForm] = useState({
    name: '',
    age: '',
    gender: 'not_specified',
    blood_type: '',
    height_cm: '',
    weight_kg: '',
    preferred_language: 'en'
  })
  const [savingProfile, setSavingProfile] = useState(false)

  // Fetch sessions on mount and when phone changes
  useEffect(() => {
    if (phone) {
      fetchSessions()
    }
  }, [phone])

  // Initialize profile form when profileData changes
  useEffect(() => {
    if (profileData?.profile) {
      const p = profileData.profile
      setProfileForm({
        name: p.name || '',
        age: p.age?.toString() || '',
        gender: p.gender || 'not_specified',
        blood_type: p.blood_type || '',
        height_cm: p.height_cm?.toString() || '',
        weight_kg: p.weight_kg?.toString() || '',
        preferred_language: p.preferred_language || 'en'
      })
    }
  }, [profileData])

  const fetchSessions = async () => {
    if (!phone) return
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE}/sessions/list`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: phone })
      })
      const data = await res.json()
      if (data.success) {
        setSessions(data.sessions || [])
      }
    } catch (e) {
      console.error('Failed to fetch sessions:', e)
    }
    setLoading(false)
  }

  const createNewSession = async () => {
    if (!phone) return
    try {
      const res = await fetch(`${API_BASE}/sessions/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: phone, language: profileForm.preferred_language || 'en' })
      })
      const data = await res.json()
      if (data.success) {
        onNewSession(data.session)
        fetchSessions()
        setIsOpen(false) // Close sidebar on mobile
      }
    } catch (e) {
      console.error('Failed to create session:', e)
    }
  }

  const loadSession = async (sessionId) => {
    try {
      const res = await fetch(`${API_BASE}/sessions/${sessionId}?user_id=${phone}`)
      const data = await res.json()
      if (data.success) {
        onLoadSession(data.session)
        setIsOpen(false) // Close sidebar on mobile
      }
    } catch (e) {
      console.error('Failed to load session:', e)
    }
  }

  const deleteSession = async (sessionId, e) => {
    e.stopPropagation()
    if (!confirm('Archive this session?')) return
    try {
      const res = await fetch(`${API_BASE}/sessions/${sessionId}?user_id=${phone}`, {
        method: 'DELETE'
      })
      const data = await res.json()
      if (data.success) {
        fetchSessions()
        if (sessionId === currentSessionId) {
          onNewSession(null) // Clear current session if deleted
        }
      }
    } catch (e) {
      console.error('Failed to delete session:', e)
    }
  }

  const saveProfile = async () => {
    if (!phone) return
    setSavingProfile(true)
    try {
      const res = await fetch(`${API_BASE}/profile/${phone}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: profileForm.name || undefined,
          age: profileForm.age ? parseInt(profileForm.age) : undefined,
          gender: profileForm.gender || undefined,
          blood_type: profileForm.blood_type || undefined,
          height_cm: profileForm.height_cm ? parseFloat(profileForm.height_cm) : undefined,
          weight_kg: profileForm.weight_kg ? parseFloat(profileForm.weight_kg) : undefined,
          preferred_language: profileForm.preferred_language || undefined
        })
      })
      const data = await res.json()
      if (data.success) {
        setShowProfileEdit(false)
        if (onProfileUpdate) {
          onProfileUpdate(data.profile)
        }
      }
    } catch (e) {
      console.error('Failed to save profile:', e)
      alert('Failed to save profile')
    }
    setSavingProfile(false)
  }

  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    return date.toLocaleDateString()
  }

  // Group sessions by date
  const groupedSessions = sessions.reduce((groups, session) => {
    const date = new Date(session.updated_at || session.created_at)
    const key = date.toDateString()
    if (!groups[key]) groups[key] = []
    groups[key].push(session)
    return groups
  }, {})

  const languages = {
    en: 'English',
    hi: 'हिंदी',
    ta: 'தமிழ்',
    te: 'తెలుగు',
    bn: 'বাংলা',
    mr: 'मराठी',
    gu: 'ગુજરાતી',
    kn: 'ಕನ್ನಡ',
    ml: 'മലയാളം'
  }

  return (
    <>
      {/* Mobile Toggle Button */}
      <button 
        className="sidebar-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle sidebar"
      >
        {isOpen ? <CloseIcon /> : <MenuIcon />}
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div className="sidebar-overlay" onClick={() => setIsOpen(false)} />
      )}

      {/* Sidebar */}
      <motion.aside 
        className={`session-sidebar ${isOpen ? 'open' : ''}`}
        initial={false}
        animate={{ x: isOpen ? 0 : -280 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      >
        {/* New Chat Button */}
        <div className="sidebar-header">
          <button className="new-chat-btn" onClick={createNewSession}>
            <PlusIcon />
            <span>New Chat</span>
          </button>
        </div>

        {/* Sessions List */}
        <div className="sessions-list">
          {loading ? (
            <div className="sidebar-loading">Loading sessions...</div>
          ) : sessions.length === 0 ? (
            <div className="no-sessions">
              <ChatIcon />
              <p>No previous sessions</p>
              <p className="hint">Start a new chat to begin</p>
            </div>
          ) : (
            Object.entries(groupedSessions).map(([dateKey, dateSessions]) => (
              <div key={dateKey} className="session-group">
                <div className="session-date">{formatDate(dateKey)}</div>
                {dateSessions.map(session => (
                  <motion.div
                    key={session.session_id}
                    className={`session-item ${session.session_id === currentSessionId ? 'active' : ''}`}
                    onClick={() => loadSession(session.session_id)}
                    whileHover={{ backgroundColor: 'rgba(255,255,255,0.1)' }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <ChatIcon />
                    <div className="session-info">
                      <span className="session-title">{session.title || 'Health Consultation'}</span>
                      <span className="session-preview">
                        {session.symptom_summary || session.message_count + ' messages'}
                      </span>
                    </div>
                    <div className="session-actions">
                      <button 
                        className="session-action-btn delete"
                        onClick={(e) => deleteSession(session.session_id, e)}
                        title="Archive session"
                      >
                        <TrashIcon />
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>
            ))
          )}
        </div>

        {/* Profile Section */}
        <div className="sidebar-profile">
          <div 
            className="profile-header"
            onClick={() => setShowProfileEdit(!showProfileEdit)}
          >
            <div className="profile-avatar">
              <UserIcon />
            </div>
            <div className="profile-info">
              <span className="profile-name">{profileForm.name || 'User'}</span>
              <span className="profile-phone">{phone}</span>
            </div>
            <ChevronIcon open={showProfileEdit} />
          </div>

          <AnimatePresence>
            {showProfileEdit && (
              <motion.div 
                className="profile-edit-form"
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                <div className="form-group">
                  <label>Name</label>
                  <input
                    type="text"
                    value={profileForm.name}
                    onChange={(e) => setProfileForm(p => ({ ...p, name: e.target.value }))}
                    placeholder="Your name"
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Age</label>
                    <input
                      type="number"
                      value={profileForm.age}
                      onChange={(e) => setProfileForm(p => ({ ...p, age: e.target.value }))}
                      placeholder="Age"
                      min="1"
                      max="120"
                    />
                  </div>
                  <div className="form-group">
                    <label>Gender</label>
                    <select
                      value={profileForm.gender}
                      onChange={(e) => setProfileForm(p => ({ ...p, gender: e.target.value }))}
                    >
                      <option value="not_specified">Not specified</option>
                      <option value="male">Male</option>
                      <option value="female">Female</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Height (cm)</label>
                    <input
                      type="number"
                      value={profileForm.height_cm}
                      onChange={(e) => setProfileForm(p => ({ ...p, height_cm: e.target.value }))}
                      placeholder="cm"
                    />
                  </div>
                  <div className="form-group">
                    <label>Weight (kg)</label>
                    <input
                      type="number"
                      value={profileForm.weight_kg}
                      onChange={(e) => setProfileForm(p => ({ ...p, weight_kg: e.target.value }))}
                      placeholder="kg"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Blood Type</label>
                  <select
                    value={profileForm.blood_type}
                    onChange={(e) => setProfileForm(p => ({ ...p, blood_type: e.target.value }))}
                  >
                    <option value="">Unknown</option>
                    <option value="A+">A+</option>
                    <option value="A-">A-</option>
                    <option value="B+">B+</option>
                    <option value="B-">B-</option>
                    <option value="AB+">AB+</option>
                    <option value="AB-">AB-</option>
                    <option value="O+">O+</option>
                    <option value="O-">O-</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Preferred Language</label>
                  <select
                    value={profileForm.preferred_language}
                    onChange={(e) => setProfileForm(p => ({ ...p, preferred_language: e.target.value }))}
                  >
                    {Object.entries(languages).map(([code, name]) => (
                      <option key={code} value={code}>{name}</option>
                    ))}
                  </select>
                </div>

                <button 
                  className="save-profile-btn"
                  onClick={saveProfile}
                  disabled={savingProfile}
                >
                  <SaveIcon />
                  {savingProfile ? 'Saving...' : 'Save Profile'}
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.aside>

      <style>{`
        .sidebar-toggle {
          position: fixed;
          top: 16px;
          left: 16px;
          z-index: 1001;
          background: rgba(30, 30, 40, 0.9);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          padding: 8px;
          color: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          backdrop-filter: blur(10px);
          transition: all 0.2s;
        }
        .sidebar-toggle:hover {
          background: rgba(60, 60, 80, 0.9);
          transform: scale(1.05);
        }

        .sidebar-overlay {
          position: fixed;
          inset: 0;
          background: rgba(0, 0, 0, 0.5);
          z-index: 999;
          backdrop-filter: blur(2px);
        }

        .session-sidebar {
          position: fixed;
          top: 0;
          left: 0;
          width: 280px;
          height: 100vh;
          background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
          border-right: 1px solid rgba(255, 255, 255, 0.1);
          display: flex;
          flex-direction: column;
          z-index: 1000;
          overflow: hidden;
        }

        .sidebar-header {
          padding: 16px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }

        .new-chat-btn {
          width: 100%;
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          border-radius: 8px;
          color: white;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }
        .new-chat-btn:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .sessions-list {
          flex: 1;
          overflow-y: auto;
          padding: 12px;
        }
        .sessions-list::-webkit-scrollbar {
          width: 6px;
        }
        .sessions-list::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.2);
          border-radius: 3px;
        }

        .sidebar-loading, .no-sessions {
          text-align: center;
          padding: 24px;
          color: rgba(255, 255, 255, 0.5);
        }
        .no-sessions svg {
          width: 48px;
          height: 48px;
          margin-bottom: 12px;
          opacity: 0.3;
        }
        .no-sessions .hint {
          font-size: 12px;
          margin-top: 8px;
        }

        .session-group {
          margin-bottom: 16px;
        }

        .session-date {
          font-size: 11px;
          color: rgba(255, 255, 255, 0.4);
          padding: 8px 12px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .session-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 10px 12px;
          border-radius: 8px;
          cursor: pointer;
          transition: all 0.2s;
          color: rgba(255, 255, 255, 0.8);
        }
        .session-item:hover {
          background: rgba(255, 255, 255, 0.05);
        }
        .session-item.active {
          background: rgba(102, 126, 234, 0.2);
          border-left: 3px solid #667eea;
        }
        .session-item svg {
          flex-shrink: 0;
          opacity: 0.6;
        }

        .session-info {
          flex: 1;
          min-width: 0;
        }
        .session-title {
          display: block;
          font-size: 13px;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .session-preview {
          display: block;
          font-size: 11px;
          color: rgba(255, 255, 255, 0.4);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .session-actions {
          display: flex;
          gap: 4px;
          opacity: 0;
          transition: opacity 0.2s;
        }
        .session-item:hover .session-actions {
          opacity: 1;
        }
        .session-action-btn {
          padding: 4px;
          background: transparent;
          border: none;
          color: rgba(255, 255, 255, 0.5);
          cursor: pointer;
          border-radius: 4px;
          transition: all 0.2s;
        }
        .session-action-btn:hover {
          background: rgba(255, 255, 255, 0.1);
          color: white;
        }
        .session-action-btn.delete:hover {
          background: rgba(239, 68, 68, 0.2);
          color: #ef4444;
        }

        .sidebar-profile {
          border-top: 1px solid rgba(255, 255, 255, 0.1);
          background: rgba(0, 0, 0, 0.2);
        }

        .profile-header {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px;
          cursor: pointer;
          transition: background 0.2s;
        }
        .profile-header:hover {
          background: rgba(255, 255, 255, 0.05);
        }

        .profile-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
        }

        .profile-info {
          flex: 1;
          min-width: 0;
        }
        .profile-name {
          display: block;
          font-size: 14px;
          font-weight: 500;
          color: white;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }
        .profile-phone {
          display: block;
          font-size: 12px;
          color: rgba(255, 255, 255, 0.5);
        }

        .profile-edit-form {
          padding: 0 16px 16px;
          overflow: hidden;
        }

        .form-group {
          margin-bottom: 12px;
        }
        .form-group label {
          display: block;
          font-size: 11px;
          color: rgba(255, 255, 255, 0.5);
          margin-bottom: 4px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
        .form-group input, .form-group select {
          width: 100%;
          padding: 8px 12px;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 6px;
          color: white;
          font-size: 14px;
        }
        .form-group input:focus, .form-group select:focus {
          outline: none;
          border-color: #667eea;
        }
        .form-group input::placeholder {
          color: rgba(255, 255, 255, 0.3);
        }
        .form-group select option {
          background: #1a1a2e;
          color: white;
        }

        .form-row {
          display: flex;
          gap: 12px;
        }
        .form-row .form-group {
          flex: 1;
        }

        .save-profile-btn {
          width: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 8px;
          padding: 10px;
          background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
          border: none;
          border-radius: 6px;
          color: white;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          margin-top: 8px;
        }
        .save-profile-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
        }
        .save-profile-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        /* Desktop styles */
        @media (min-width: 768px) {
          .sidebar-toggle {
            display: none;
          }
          .sidebar-overlay {
            display: none;
          }
          .session-sidebar {
            transform: translateX(0) !important;
          }
        }

        /* Mobile styles */
        @media (max-width: 767px) {
          .session-sidebar {
            transform: translateX(-100%);
          }
          .session-sidebar.open {
            transform: translateX(0);
          }
        }
      `}</style>
    </>
  )
}

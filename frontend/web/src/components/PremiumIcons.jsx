import { motion } from 'framer-motion'

// Premium animated medical icons - replacing emojis with custom SVG icons

// Animated Heart with Pulse
export const HeartPulseIcon = ({ size = 24, color = "currentColor", animate = true }) => (
  <motion.svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    initial={{ scale: 1 }}
    animate={animate ? { scale: [1, 1.1, 1] } : {}}
    transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
  >
    <defs>
      <linearGradient id="heartGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#FF6B6B" />
        <stop offset="100%" stopColor="#EE5A5A" />
      </linearGradient>
    </defs>
    <path
      d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"
      fill="url(#heartGrad)"
    />
    <motion.path
      d="M4 12h3l2-4 3 8 2-4h6"
      stroke="white"
      strokeWidth="1.5"
      strokeLinecap="round"
      fill="none"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ duration: 1.5, repeat: Infinity }}
    />
  </motion.svg>
)

// DNA Helix Icon
export const DNAIcon = ({ size = 24, color = "#00D4AA" }) => (
  <motion.svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    animate={{ rotate: 360 }}
    transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
  >
    <defs>
      <linearGradient id="dnaGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#00D4AA" />
        <stop offset="100%" stopColor="#667eea" />
      </linearGradient>
    </defs>
    <path
      d="M12 2v20M8 4c0 4 8 4 8 8s-8 4-8 8M16 4c0 4-8 4-8 8s8 4 8 8"
      stroke="url(#dnaGrad)"
      strokeWidth="2"
      strokeLinecap="round"
      fill="none"
    />
  </motion.svg>
)

// Shield Check - For Self Care Badge
export const ShieldCheckIcon = ({ size = 20, color = "#00D4AA" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#00D4AA" />
        <stop offset="100%" stopColor="#00B894" />
      </linearGradient>
    </defs>
    <path
      d="M12 2L4 5v6c0 5.55 3.84 10.74 8 12 4.16-1.26 8-6.45 8-12V5l-8-3z"
      fill="url(#shieldGrad)"
    />
    <motion.path
      d="M9 12l2 2 4-4"
      stroke="white"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    />
  </svg>
)

// Warning Triangle - For Urgent Care
export const WarningTriangleIcon = ({ size = 20, color = "#F59E0B" }) => (
  <motion.svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    animate={{ scale: [1, 1.05, 1] }}
    transition={{ duration: 1, repeat: Infinity }}
  >
    <defs>
      <linearGradient id="warnGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#FBBF24" />
        <stop offset="100%" stopColor="#F59E0B" />
      </linearGradient>
    </defs>
    <path
      d="M12 2L2 20h20L12 2z"
      fill="url(#warnGrad)"
    />
    <path d="M12 9v4" stroke="white" strokeWidth="2" strokeLinecap="round" />
    <circle cx="12" cy="16" r="1" fill="white" />
  </motion.svg>
)

// Emergency Cross - For Emergency
export const EmergencyCrossIcon = ({ size = 20, color = "#EF4444" }) => (
  <motion.svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    animate={{ scale: [1, 1.1, 1] }}
    transition={{ duration: 0.8, repeat: Infinity }}
  >
    <defs>
      <linearGradient id="emergGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#EF4444" />
        <stop offset="100%" stopColor="#DC2626" />
      </linearGradient>
    </defs>
    <rect x="2" y="2" width="20" height="20" rx="4" fill="url(#emergGrad)" />
    <path d="M12 6v12M6 12h12" stroke="white" strokeWidth="3" strokeLinecap="round" />
  </motion.svg>
)

// Pill/Medicine Icon
export const PillIcon = ({ size = 24, color = "#667eea" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="pillGrad1" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#667eea" />
        <stop offset="100%" stopColor="#764ba2" />
      </linearGradient>
      <linearGradient id="pillGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#00D4AA" />
        <stop offset="100%" stopColor="#00B894" />
      </linearGradient>
    </defs>
    <rect x="3" y="10" width="18" height="8" rx="4" fill="url(#pillGrad1)" />
    <rect x="3" y="10" width="9" height="8" rx="4" fill="url(#pillGrad2)" />
    <ellipse cx="12" cy="14" rx="1" ry="3" fill="rgba(255,255,255,0.3)" />
  </svg>
)

// Stethoscope Icon
export const StethoscopeIcon = ({ size = 24, color = "#667eea" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="stethGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#667eea" />
        <stop offset="100%" stopColor="#764ba2" />
      </linearGradient>
    </defs>
    <path
      d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.2.2 0 1 0 .3.3"
      stroke="url(#stethGrad)"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <path
      d="M8 15v1a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6v-4"
      stroke="url(#stethGrad)"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <circle cx="20" cy="10" r="2" fill="url(#stethGrad)" />
  </svg>
)

// Clipboard Medical Icon
export const ClipboardMedicalIcon = ({ size = 24, color = "#667eea" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="clipGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#667eea" />
        <stop offset="100%" stopColor="#764ba2" />
      </linearGradient>
    </defs>
    <rect x="4" y="4" width="16" height="18" rx="2" fill="url(#clipGrad)" opacity="0.2" />
    <path
      d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"
      stroke="url(#clipGrad)"
      strokeWidth="2"
    />
    <rect x="8" y="2" width="8" height="4" rx="1" fill="url(#clipGrad)" />
    <path d="M12 10v6M9 13h6" stroke="url(#clipGrad)" strokeWidth="2" strokeLinecap="round" />
  </svg>
)

// Brain/Mental Health Icon
export const BrainIcon = ({ size = 24, color = "#A78BFA" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="brainGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#A78BFA" />
        <stop offset="100%" stopColor="#8B5CF6" />
      </linearGradient>
    </defs>
    <path
      d="M12 2a4 4 0 0 0-4 4 4 4 0 0 0-4 4c0 2.5 1.5 4 3 5v5a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2v-5c1.5-1 3-2.5 3-5a4 4 0 0 0-4-4 4 4 0 0 0-4-4z"
      fill="url(#brainGrad)"
      opacity="0.3"
      stroke="url(#brainGrad)"
      strokeWidth="2"
    />
    <path d="M12 2v6M8 8c0 2 1 3 2 4M16 8c0 2-1 3-2 4" stroke="url(#brainGrad)" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
)

// Thermometer Icon
export const ThermometerIcon = ({ size = 24, color = "#EF4444" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="thermoGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stopColor="#FCA5A5" />
        <stop offset="100%" stopColor="#EF4444" />
      </linearGradient>
    </defs>
    <path
      d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z"
      stroke="#94A3B8"
      strokeWidth="2"
      fill="none"
    />
    <circle cx="11.5" cy="17.5" r="2" fill="url(#thermoGrad)" />
    <rect x="10" y="8" width="3" height="6" rx="1" fill="url(#thermoGrad)" />
  </svg>
)

// Activity/Vitals Icon
export const VitalsIcon = ({ size = 24, color = "#00D4AA" }) => (
  <motion.svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="vitalsGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stopColor="#00D4AA" />
        <stop offset="100%" stopColor="#667eea" />
      </linearGradient>
    </defs>
    <motion.path
      d="M22 12h-4l-3 9L9 3l-3 9H2"
      stroke="url(#vitalsGrad)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ duration: 2, repeat: Infinity }}
    />
  </motion.svg>
)

// AI Bot Icon - Premium
export const AIBotIcon = ({ size = 32, color = "#667eea" }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
    <defs>
      <linearGradient id="botGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#667eea" />
        <stop offset="100%" stopColor="#764ba2" />
      </linearGradient>
      <filter id="botGlow" x="-50%" y="-50%" width="200%" height="200%">
        <feGaussianBlur stdDeviation="2" result="blur" />
        <feMerge>
          <feMergeNode in="blur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>
    </defs>
    <circle cx="20" cy="20" r="18" fill="url(#botGrad)" filter="url(#botGlow)" />
    <rect x="10" y="14" width="20" height="14" rx="3" fill="white" opacity="0.9" />
    <circle cx="15" cy="20" r="2" fill="url(#botGrad)" />
    <circle cx="25" cy="20" r="2" fill="url(#botGrad)" />
    <path d="M20 6v4" stroke="white" strokeWidth="2" strokeLinecap="round" />
    <circle cx="20" cy="5" r="2" fill="white" />
  </svg>
)

// User Avatar Icon
export const UserAvatarIcon = ({ size = 32, color = "#00D4AA" }) => (
  <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
    <defs>
      <linearGradient id="userGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#00D4AA" />
        <stop offset="100%" stopColor="#00B894" />
      </linearGradient>
    </defs>
    <circle cx="20" cy="20" r="18" fill="url(#userGrad)" />
    <circle cx="20" cy="15" r="6" fill="white" />
    <path d="M8 34c0-6.627 5.373-12 12-12s12 5.373 12 12" fill="white" />
  </svg>
)

// Microphone Icon (Premium)
export const MicrophoneIcon = ({ size = 24, isListening = false }) => (
  <motion.svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    animate={isListening ? { scale: [1, 1.1, 1] } : {}}
    transition={{ duration: 0.5, repeat: Infinity }}
  >
    <defs>
      <linearGradient id="micGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor={isListening ? "#EF4444" : "#667eea"} />
        <stop offset="100%" stopColor={isListening ? "#DC2626" : "#764ba2"} />
      </linearGradient>
    </defs>
    <rect x="9" y="2" width="6" height="12" rx="3" fill="url(#micGrad)" />
    <path d="M5 10v1a7 7 0 0 0 14 0v-1" stroke="url(#micGrad)" strokeWidth="2" strokeLinecap="round" />
    <path d="M12 18v4M8 22h8" stroke="url(#micGrad)" strokeWidth="2" strokeLinecap="round" />
    {isListening && (
      <>
        <motion.circle
          cx="12"
          cy="8"
          r="10"
          stroke="#EF4444"
          strokeWidth="2"
          fill="none"
          initial={{ scale: 0.5, opacity: 1 }}
          animate={{ scale: 1.5, opacity: 0 }}
          transition={{ duration: 1, repeat: Infinity }}
        />
      </>
    )}
  </motion.svg>
)

// Camera Icon (Premium)
export const CameraIconPremium = ({ size = 24, color = "#667eea" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="camGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#00D4AA" />
        <stop offset="100%" stopColor="#00B894" />
      </linearGradient>
    </defs>
    <path
      d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"
      fill="url(#camGrad)"
    />
    <circle cx="12" cy="13" r="4" fill="white" />
    <circle cx="12" cy="13" r="2" fill="url(#camGrad)" />
  </svg>
)

// Send Button Icon
export const SendIcon = ({ size = 24 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="sendGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#667eea" />
        <stop offset="100%" stopColor="#764ba2" />
      </linearGradient>
    </defs>
    <path
      d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"
      stroke="url(#sendGrad)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
    />
  </svg>
)

// Volume/Speaker Icon
export const SpeakerIcon = ({ size = 24, isSpeaking = false }) => (
  <motion.svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    animate={isSpeaking ? { scale: [1, 1.05, 1] } : {}}
    transition={{ duration: 0.3, repeat: Infinity }}
  >
    <defs>
      <linearGradient id="speakGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor={isSpeaking ? "#00D4AA" : "#667eea"} />
        <stop offset="100%" stopColor={isSpeaking ? "#00B894" : "#764ba2"} />
      </linearGradient>
    </defs>
    <path d="M11 5L6 9H2v6h4l5 4V5z" fill="url(#speakGrad)" />
    {isSpeaking && (
      <>
        <motion.path
          d="M15.54 8.46a5 5 0 0 1 0 7.07"
          stroke="url(#speakGrad)"
          strokeWidth="2"
          strokeLinecap="round"
          initial={{ opacity: 0.3 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, repeat: Infinity, repeatType: "reverse" }}
        />
        <motion.path
          d="M19.07 4.93a10 10 0 0 1 0 14.14"
          stroke="url(#speakGrad)"
          strokeWidth="2"
          strokeLinecap="round"
          initial={{ opacity: 0.3 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, repeat: Infinity, repeatType: "reverse", delay: 0.2 }}
        />
      </>
    )}
  </motion.svg>
)

// Phone Icon for Emergency
export const PhoneIcon = ({ size = 20, color = "#EF4444" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="phoneGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#EF4444" />
        <stop offset="100%" stopColor="#DC2626" />
      </linearGradient>
    </defs>
    <path
      d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"
      fill="url(#phoneGrad)"
    />
  </svg>
)

// Download Icon
export const DownloadIcon = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
    <polyline points="7 10 12 15 17 10" />
    <line x1="12" y1="15" x2="12" y2="3" />
  </svg>
)

// Trash Icon
export const TrashIcon = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <polyline points="3 6 5 6 21 6" />
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
  </svg>
)

// Close/X Icon
export const CloseIcon = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
    <line x1="18" y1="6" x2="6" y2="18" />
    <line x1="6" y1="6" x2="18" y2="18" />
  </svg>
)

// Stop Icon (for stopping speech)
export const StopIcon = ({ size = 20 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="stopGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#EF4444" />
        <stop offset="100%" stopColor="#DC2626" />
      </linearGradient>
    </defs>
    <rect x="6" y="6" width="12" height="12" rx="2" fill="url(#stopGrad)" />
  </svg>
)

// Life Buoy / Support Icon
export const LifeBuoyIcon = ({ size = 24 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="lifeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#A78BFA" />
        <stop offset="100%" stopColor="#8B5CF6" />
      </linearGradient>
    </defs>
    <circle cx="12" cy="12" r="10" stroke="url(#lifeGrad)" strokeWidth="2" fill="none" />
    <circle cx="12" cy="12" r="4" stroke="url(#lifeGrad)" strokeWidth="2" fill="none" />
    <line x1="4.93" y1="4.93" x2="9.17" y2="9.17" stroke="url(#lifeGrad)" strokeWidth="2" />
    <line x1="14.83" y1="14.83" x2="19.07" y2="19.07" stroke="url(#lifeGrad)" strokeWidth="2" />
    <line x1="14.83" y1="9.17" x2="19.07" y2="4.93" stroke="url(#lifeGrad)" strokeWidth="2" />
    <line x1="4.93" y1="19.07" x2="9.17" y2="14.83" stroke="url(#lifeGrad)" strokeWidth="2" />
  </svg>
)

// Symptom Tag Icons
export const HeadacheIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="10" r="8" stroke="currentColor" strokeWidth="2" fill="none" />
    <path d="M8 10h8M12 6v8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" opacity="0.5" />
    <path d="M6 18l2-2M18 18l-2-2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
)

export const FeverIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z" stroke="currentColor" strokeWidth="2" fill="none" />
    <circle cx="11.5" cy="17.5" r="2" fill="currentColor" />
  </svg>
)

export const StomachIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <ellipse cx="12" cy="14" rx="8" ry="6" stroke="currentColor" strokeWidth="2" fill="none" />
    <path d="M8 12c1 2 3 2 4 0s3-2 4 0" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
)

export const AnxietyIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" fill="none" />
    <path d="M8 9h.01M16 9h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    <path d="M9 15s1.5-2 3-2 3 2 3 2" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
  </svg>
)

export const SleepIcon = ({ size = 16 }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" strokeWidth="2" fill="none" />
  </svg>
)

// Online Status Dot
export const OnlineStatusDot = ({ online = true, size = 10 }) => (
  <motion.div
    style={{
      width: size,
      height: size,
      borderRadius: '50%',
      background: online 
        ? 'linear-gradient(135deg, #00D4AA, #00B894)' 
        : 'linear-gradient(135deg, #EF4444, #DC2626)',
      boxShadow: online 
        ? '0 0 10px rgba(0, 212, 170, 0.5)' 
        : '0 0 10px rgba(239, 68, 68, 0.5)',
    }}
    animate={online ? { scale: [1, 1.2, 1] } : {}}
    transition={{ duration: 2, repeat: Infinity }}
  />
)

// Loading Spinner
export const LoadingSpinner = ({ size = 24 }) => (
  <motion.svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    animate={{ rotate: 360 }}
    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
  >
    <defs>
      <linearGradient id="spinGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#667eea" />
        <stop offset="100%" stopColor="#764ba2" />
      </linearGradient>
    </defs>
    <circle cx="12" cy="12" r="10" stroke="#E2E8F0" strokeWidth="3" fill="none" />
    <path
      d="M12 2a10 10 0 0 1 10 10"
      stroke="url(#spinGrad)"
      strokeWidth="3"
      strokeLinecap="round"
      fill="none"
    />
  </motion.svg>
)

// Typing Indicator
export const TypingIndicator = () => (
  <div style={{ display: 'flex', gap: '4px', alignItems: 'center', padding: '8px 0' }}>
    {[0, 1, 2].map((i) => (
      <motion.div
        key={i}
        style={{
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
        }}
        animate={{ y: [0, -8, 0] }}
        transition={{
          duration: 0.6,
          repeat: Infinity,
          delay: i * 0.15,
        }}
      />
    ))}
  </div>
)

// Additional Missing Icons

// Medical Cross Icon
export const MedicalCrossIcon = ({ size = 24, color = "#00D4AA" }) => (
  <motion.svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    animate={{ scale: [1, 1.05, 1] }}
    transition={{ duration: 2, repeat: Infinity }}
  >
    <defs>
      <linearGradient id="crossGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#00D4AA" />
        <stop offset="100%" stopColor="#667eea" />
      </linearGradient>
    </defs>
    <rect x="9" y="2" width="6" height="20" rx="2" fill="url(#crossGrad)" />
    <rect x="2" y="9" width="20" height="6" rx="2" fill="url(#crossGrad)" />
  </motion.svg>
)

// Activity Pulse Icon (ECG/Heart Monitor)
export const ActivityPulseIcon = ({ size = 24, color = "#00D4AA" }) => (
  <motion.svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
  >
    <defs>
      <linearGradient id="pulseGrad" x1="0%" y1="0%" x2="100%" y2="0%">
        <stop offset="0%" stopColor="#00D4AA" />
        <stop offset="100%" stopColor="#667eea" />
      </linearGradient>
    </defs>
    <motion.path
      d="M2 12h4l2-6 3 12 2-6 2 3h7"
      stroke="url(#pulseGrad)"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      initial={{ pathLength: 0 }}
      animate={{ pathLength: 1 }}
      transition={{ duration: 2, repeat: Infinity }}
    />
  </motion.svg>
)

// User Icon
export const UserIcon = ({ size = 24, color = "#667eea" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="userGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#667eea" />
        <stop offset="100%" stopColor="#764ba2" />
      </linearGradient>
    </defs>
    <circle cx="12" cy="8" r="4" fill="url(#userGrad)" />
    <path d="M4 20c0-4 4-6 8-6s8 2 8 6" fill="url(#userGrad)" />
  </svg>
)

// Bot Icon
export const BotIcon = ({ size = 24, color = "#667eea" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="botGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#667eea" />
        <stop offset="100%" stopColor="#00D4AA" />
      </linearGradient>
    </defs>
    <rect x="4" y="8" width="16" height="12" rx="3" fill="url(#botGrad)" />
    <circle cx="12" cy="5" r="2" fill="url(#botGrad)" />
    <line x1="12" y1="7" x2="12" y2="8" stroke="url(#botGrad)" strokeWidth="2" />
    <circle cx="9" cy="13" r="1.5" fill="white" />
    <circle cx="15" cy="13" r="1.5" fill="white" />
    <path d="M9 17h6" stroke="white" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
)

// Volume On Icon
export const VolumeIcon = ({ size = 24, color = "#667eea" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" fill="currentColor" />
    <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
    <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
  </svg>
)

// Volume Off Icon
export const VolumeOffIcon = ({ size = 24, color = "#667eea" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" fill="currentColor" />
    <line x1="23" y1="9" x2="17" y2="15" />
    <line x1="17" y1="9" x2="23" y2="15" />
  </svg>
)

// Camera Icon
export const CameraIcon = ({ size = 24, color = "#667eea" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
    <circle cx="12" cy="13" r="4" />
  </svg>
)

// Alert Triangle Icon
export const AlertTriangleIcon = ({ size = 24, color = "#F59E0B" }) => (
  <motion.svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    animate={{ scale: [1, 1.05, 1] }}
    transition={{ duration: 1, repeat: Infinity }}
  >
    <defs>
      <linearGradient id="alertGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#F59E0B" />
        <stop offset="100%" stopColor="#EF4444" />
      </linearGradient>
    </defs>
    <path
      d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"
      fill="url(#alertGrad)"
    />
    <line x1="12" y1="9" x2="12" y2="13" stroke="white" strokeWidth="2" />
    <circle cx="12" cy="17" r="1" fill="white" />
  </motion.svg>
)

// Message Square Icon
export const MessageSquareIcon = ({ size = 24, color = "#667eea" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none">
    <defs>
      <linearGradient id="msgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#667eea" />
        <stop offset="100%" stopColor="#00D4AA" />
      </linearGradient>
    </defs>
    <path
      d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
      fill="url(#msgGrad)"
    />
  </svg>
)

// Lifebuoy Icon (Support)
export const LifebuoyIcon = ({ size = 24, color = "#00D4AA" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" stroke="#00D4AA" />
    <circle cx="12" cy="12" r="4" stroke="#00D4AA" />
    <line x1="4.93" y1="4.93" x2="9.17" y2="9.17" stroke="#00D4AA" />
    <line x1="14.83" y1="14.83" x2="19.07" y2="19.07" stroke="#00D4AA" />
    <line x1="14.83" y1="9.17" x2="19.07" y2="4.93" stroke="#00D4AA" />
    <line x1="4.93" y1="19.07" x2="9.17" y2="14.83" stroke="#00D4AA" />
  </svg>
)

// Heart Handshake Icon (Mental Health Support)
export const HeartHandshakeIcon = ({ size = 24, color = "#FF6B6B" }) => (
  <motion.svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    animate={{ scale: [1, 1.05, 1] }}
    transition={{ duration: 1.5, repeat: Infinity }}
  >
    <defs>
      <linearGradient id="heartHandGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#FF6B6B" />
        <stop offset="100%" stopColor="#A78BFA" />
      </linearGradient>
    </defs>
    <path
      d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"
      fill="url(#heartHandGrad)"
    />
    <path d="M12 5L9.04 7.96a2.17 2.17 0 0 0 0 3.08c.82.82 2.13.85 3 .07l2.07-1.9a2.82 2.82 0 0 1 3.79 0l2.96 2.66" stroke="white" strokeWidth="1.5" fill="none" />
  </motion.svg>
)

// Stop Circle Icon
export const StopCircleIcon = ({ size = 24, color = "#EF4444" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="12" cy="12" r="10" stroke="#EF4444" />
    <rect x="9" y="9" width="6" height="6" rx="1" fill="#EF4444" />
  </svg>
)

export default {
  HeartPulseIcon,
  DNAIcon,
  ShieldCheckIcon,
  WarningTriangleIcon,
  EmergencyCrossIcon,
  PillIcon,
  StethoscopeIcon,
  ClipboardMedicalIcon,
  BrainIcon,
  ThermometerIcon,
  VitalsIcon,
  AIBotIcon,
  UserAvatarIcon,
  MicrophoneIcon,
  CameraIconPremium,
  SendIcon,
  SpeakerIcon,
  PhoneIcon,
  DownloadIcon,
  TrashIcon,
  CloseIcon,
  StopIcon,
  LifeBuoyIcon,
  OnlineStatusDot,
  LoadingSpinner,
  TypingIndicator,
  MedicalCrossIcon,
  ActivityPulseIcon,
  UserIcon,
  BotIcon,
  VolumeIcon,
  VolumeOffIcon,
  CameraIcon,
  AlertTriangleIcon,
  MessageSquareIcon,
  LifebuoyIcon,
  HeartHandshakeIcon,
  StopCircleIcon,
}

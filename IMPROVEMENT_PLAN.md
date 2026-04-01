# 🚀 CMC Health — Project Improvement Plan

**Generated:** February 17, 2026  
**Based on:** Full codebase audit of backend, frontend, services, config, tests, and infrastructure

---

## Priority Legend

| Priority | Meaning | Effort |
|----------|---------|--------|
| 🔴 P0 | Critical — Security/data loss risk, fix immediately | Hours |
| 🟠 P1 | High — Major quality/reliability gap | 1–3 days |
| 🟡 P2 | Medium — Noticeable improvement, plan this sprint | 3–7 days |
| 🟢 P3 | Low — Nice-to-have, backlog | 1–2 weeks |

---

## 1. 🔴 SECURITY (P0 — Fix Immediately)

### 1.1 Hardcoded Secret Key
**File:** `backend/app/config.py:70`
```python
SECRET_KEY: str = "your-secret-key-change-in-production"
```
**Risk:** Anyone who reads the source code can forge JWT tokens and impersonate any user.

**Fix:** Generate a real secret and enforce it:
```python
import secrets
SECRET_KEY: str = os.getenv("SECRET_KEY") or secrets.token_hex(32)
```
Then set `SECRET_KEY` in `.env` with `openssl rand -hex 32`.

---

### 1.2 CORS Allows All Origins
**File:** `backend/app/main.py:60`
```python
allow_origins=["*"]  # Configure properly for production
```
**Risk:** Any website can make authenticated requests to your API (CSRF/credential theft).

**Fix:** Use environment-driven origin list:
```python
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, ...)
```

---

### 1.3 WhatsApp Webhook Has No Signature Verification
**File:** `backend/app/routes/whatsapp_routes.py` — `receive_message()`

**Risk:** Anyone who discovers your ngrok URL can send fake webhook payloads, causing the bot to message arbitrary users.

**Fix:** Verify `X-Hub-Signature-256` header on every POST:
```python
import hmac, hashlib

async def verify_meta_signature(request: Request) -> bool:
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = await request.body()
    app_secret = os.getenv("WHATSAPP_APP_SECRET", "")
    expected = "sha256=" + hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)
```

---

### 1.4 WhatsApp Token Expires Every 24 Hours
**Current:** Manual daily token refresh from Meta Dashboard.

**Fix:** Create a permanent System User token:
1. Go to Meta Business Settings → System Users
2. Create new system user with `whatsapp_business_messaging` permission
3. Generate a token → it never expires
4. Put it in `.env`

---

## 2. 🟠 RELIABILITY & DATA (P1 — This Week)

### 2.1 All State is In-Memory — Lost on Every Restart
**Files:** `whatsapp_routes.py`, `auth_routes.py`, `database.py`

**Problem:** These are all lost when the backend restarts:
- `user_sessions = {}` — WhatsApp conversations
- `processed_messages = set()` — Dedup tracking (can cause duplicate AI responses)
- `user_languages = {}` — Language preferences
- `_users_db = {}` — All registered users
- `_refresh_tokens = {}` — All login sessions

**Impact:** Every backend restart = all users lose their session, language, and login.

**Fix (Quick — Redis):**
```python
import redis.asyncio as aioredis

redis_client = aioredis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

# Replace: processed_messages = set()
async def is_duplicate(msg_id: str) -> bool:
    return not await redis_client.set(f"wa_msg:{msg_id}", "1", nx=True, ex=3600)

# Replace: user_sessions = {}
async def get_session(phone: str) -> dict:
    data = await redis_client.get(f"wa_session:{phone}")
    return json.loads(data) if data else None
```

**Fix (Full — MongoDB):**
- Use the already-configured MongoDB Atlas connection
- `database.py` already has the URL but falls back to in-memory

---

### 2.2 `processed_messages` Set Grows Unbounded
**File:** `whatsapp_routes.py:59`
```python
processed_messages = set()
```
**Problem:** Every incoming WhatsApp message ID is added, never removed. Over days/weeks this set grows indefinitely → memory leak.

**Fix:** Use a TTL-based structure:
```python
from collections import OrderedDict
import time

class TTLSet:
    def __init__(self, ttl_seconds=3600):
        self._data = OrderedDict()
        self._ttl = ttl_seconds

    def add(self, item):
        self._cleanup()
        self._data[item] = time.time()

    def __contains__(self, item):
        self._cleanup()
        return item in self._data

    def _cleanup(self):
        cutoff = time.time() - self._ttl
        while self._data and next(iter(self._data.values())) < cutoff:
            self._data.popitem(last=False)

processed_messages = TTLSet(ttl_seconds=3600)  # 1 hour dedup window
```

---

### 2.3 Background Task Errors Are Silently Swallowed
**File:** `whatsapp_routes.py:608`
```python
asyncio.create_task(process_messages())
```
**Problem:** If `process_messages()` raises an exception, it's silently lost — no log, no alert. User gets no reply with zero error visibility.

**Fix:**
```python
async def safe_process_messages():
    try:
        await process_messages()
    except Exception as e:
        logger.exception(f"Background WhatsApp processing failed: {e}")

asyncio.create_task(safe_process_messages())
```

---

### 2.4 No Request Validation on WhatsApp Webhook
**Problem:** The webhook endpoint blindly trusts all incoming JSON. Malformed payloads crash the handler.

**Fix:** Add Pydantic models for incoming webhook data and validate before processing.

---

## 3. 🟡 ARCHITECTURE & CODE QUALITY (P2 — This Sprint)

### 3.1 Monster Files Need Splitting
| File | Lines | Problem |
|------|-------|---------|
| `ai_service_v2.py` | **2,203** | Does everything: memory, reasoning, diagnosis, LLM calls, medication, translation |
| `App.jsx` | **3,268** | Single component handles all UI modes, state, API calls, audio, etc. |
| `whatsapp_routes.py` | **665** | Route handler does business logic, message formatting, media processing |

**Recommended splits:**

**`ai_service_v2.py` → 5 files:**
```
services/
├── ai/
│   ├── conversation_memory.py    # ConversationMemory class
│   ├── medical_reasoning.py      # MedicalReasoningEngine
│   ├── llm_client.py             # Ollama/Cerebras API calls
│   ├── response_builder.py       # AIResponse construction
│   └── service.py                # PowerfulAIService (orchestrator)
```

**`App.jsx` → 6 components:**
```
components/
├── ChatView.jsx           # Chat UI, messages, input
├── VitalsView.jsx         # Vitals dashboard
├── LanguageSelector.jsx   # Language picker
├── AudioRecorder.jsx      # Voice recording/playback
├── DiagnosisCard.jsx      # Diagnosis results display
└── AppShell.jsx           # Layout, routing, state provider
```

**`whatsapp_routes.py` → 3 files:**
```
routes/whatsapp_routes.py          # Just route definitions (thin)
services/whatsapp_service.py       # Message processing logic
services/whatsapp_formatter.py     # Response formatting for WhatsApp
```

---

### 3.2 Duplicate Symptom Mapping Code
**Problem:** `ai_service_v2.py` has the `PHRASE_TO_SYMPTOM` and `typo_map` dictionaries **duplicated** in `ConversationMemory.track_symptoms()` — once as the "Priority 1" phrase mapping (line ~210) and again as the fallback typo map (line ~285). They contain overlapping entries.

**Fix:** Extract to a single source of truth:
```python
# backend/app/data/symptom_mappings.py
PHRASE_TO_SYMPTOM = { ... }  # One canonical dictionary
TYPO_CORRECTIONS = { ... }   # One canonical dictionary
```
Import in both `ai_service_v2.py` and `symptom_normalizer.py`.

---

### 3.3 AI Orchestrator is Disabled
**File:** `conversation_routes.py:27`
```python
ORCHESTRATOR_AVAILABLE = False  # Force use of ai_service_v2
```
**Problem:** The more advanced `ai_orchestrator.py` (620 lines with RAG, safety guardrails, triage) is completely bypassed. Everything goes through `ai_service_v2.py` directly.

**Action:** Either:
- **Fix and enable** the orchestrator (it has RAG + Safety + Triage that `ai_service_v2` lacks), OR
- **Delete** the orchestrator code to reduce confusion

---

### 3.4 Backup Files in Production Code
**File:** `backend/app/services/ai_diagnosis.py.bak`

**Fix:** Remove `.bak` files from the repository. Use git history for old versions.

---

## 4. 🟡 TESTING (P2 — Critical Gap)

### 4.1 Almost Zero Test Coverage
**Current state:** `tests/test_api.py` has **5 basic tests** (64 lines). All use `assert status_code in [200, 500]` — allowing failures to pass.

**What's missing:**
- ❌ No unit tests for `ai_service_v2.py` (2,203 lines, 0 tests)
- ❌ No unit tests for diagnosis engine
- ❌ No tests for WhatsApp message parsing/formatting
- ❌ No tests for symptom normalization (1000+ mappings)
- ❌ No integration tests for the AI pipeline
- ❌ No frontend tests at all

**Recommended test plan:**

```
tests/
├── unit/
│   ├── test_symptom_normalizer.py      # Test all 1000+ symptom mappings
│   ├── test_diagnosis_engine.py        # Test condition matching accuracy
│   ├── test_urgency_classification.py  # Emergency keywords detection
│   ├── test_whatsapp_formatter.py      # Response formatting
│   ├── test_conversation_memory.py     # Session management
│   └── test_medication_lookup.py       # Drug RAG results
├── integration/
│   ├── test_ai_pipeline.py            # End-to-end symptom → diagnosis
│   ├── test_whatsapp_webhook.py       # Webhook receive → response
│   └── test_translation.py           # Multi-language responses
└── conftest.py                        # Shared fixtures
```

**Quick win — test the most critical path:**
```python
# tests/unit/test_urgency.py
def test_emergency_detection():
    """Chest pain MUST trigger emergency"""
    from app.services.ai_service_v2 import powerful_ai
    result = powerful_ai.reasoning_engine.analyze_urgency(
        symptoms=["chest pain"], vitals={}
    )
    assert result["urgency"] == "emergency"

def test_self_care_classification():
    """Common cold should be self-care"""
    result = powerful_ai.reasoning_engine.analyze_urgency(
        symptoms=["runny nose", "mild cough"], vitals={}
    )
    assert result["urgency"] == "self_care"
```

---

## 5. 🟡 PERFORMANCE (P2)

### 5.1 Whisper Model Loads on First Voice Message
**File:** `whatsapp_routes.py:74` — `get_whisper_model()`

**Problem:** First voice message takes 30-60 seconds while Whisper "medium" model loads. User thinks bot is broken.

**Fix:** Pre-load during startup:
```python
# In main.py lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing startup
    # Pre-load Whisper
    from app.routes.whatsapp_routes import get_whisper_model
    get_whisper_model()  # Load during startup, not first request
```

---

### 5.2 No Connection Pooling for HTTP Clients
**File:** `whatsapp_routes.py:270`
```python
async with httpx.AsyncClient() as client:  # New connection every message
```
**Problem:** Creates a new TCP connection + TLS handshake for every WhatsApp API call.

**Fix:** Use a shared client:
```python
# Module level
_http_client: httpx.AsyncClient = None

async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=30.0)
    return _http_client
```

---

### 5.3 No Caching for Diagnosis Results
**Problem:** Same symptoms always re-run the full TF-IDF pipeline + LLM call.

**Fix:** Cache diagnosis results (not LLM text) for identical symptom sets:
```python
from functools import lru_cache

@lru_cache(maxsize=500)
def cached_diagnosis(symptom_tuple: tuple) -> list:
    return diagnosis_engine.diagnose(list(symptom_tuple))
```

---

## 6. 🟡 FRONTEND IMPROVEMENTS (P2)

### 6.1 No Error Boundaries
**Problem:** If any component throws (e.g., WebGL fails on old phones), the entire app crashes to a white screen.

**Fix:** Add React Error Boundary:
```jsx
class ErrorBoundary extends React.Component {
    state = { hasError: false }
    static getDerivedStateFromError(error) { return { hasError: true } }
    render() {
        if (this.state.hasError) return <FallbackUI />
        return this.props.children
    }
}
```

---

### 6.2 No Loading/Skeleton States
**Problem:** When AI is processing (2-8 seconds), the user sees nothing — no feedback.

**Fix:** Add typing indicator / skeleton for AI responses.

---

### 6.3 Three.js Bundle Too Large
**Current:** `three` + `@react-three/fiber` + `@react-three/drei` = ~1.2MB gzipped

**Problem:** On rural 2G/3G connections (your target audience), this takes 30+ seconds to load.

**Options:**
1. **Lazy-load Three.js** — only load after initial render
2. **Use CSS animations** instead — 95% lighter for the same visual effect
3. **Progressive enhancement** — skip 3D on slow connections

```jsx
const WebGLBackground = React.lazy(() => import('./components/WebGLBackground'))

// Only load on fast connections
const connection = navigator.connection
const isFast = !connection || connection.effectiveType === '4g'

{isFast && (
    <Suspense fallback={<div className="gradient-bg" />}>
        <WebGLBackground />
    </Suspense>
)}
```

---

### 6.4 No Offline Support / PWA
**Problem:** Target users are in rural areas with intermittent connectivity. Currently the app is completely unusable offline.

**Fix:** Add PWA support:
- Service worker for caching static assets
- IndexedDB for storing previous diagnoses
- Offline-first message queue (sync when connected)

---

## 7. 🟢 DEVELOPER EXPERIENCE (P3)

### 7.1 Complete the TODOs in `main.py`
```python
# TODO: Initialize ML models          → Pre-load TF-IDF vectorizer
# TODO: Connect to MQTT broker        → Connect or remove from config
# TODO: Start Prometheus metrics server → Wire up existing prometheus_client
```

---

### 7.2 Add Pre-commit Hooks
```bash
pip install pre-commit
```
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    hooks: [{ id: black }]
  - repo: https://github.com/pycqa/isort
    hooks: [{ id: isort }]
  - repo: https://github.com/pycqa/flake8
    hooks: [{ id: flake8 }]
```

---

### 7.3 Add Type Hints Throughout
**Problem:** Most service functions lack type hints, making the code harder to reason about and Pylance/IDE support weaker.

**Example fix:**
```python
# Before
async def process_incoming_message(from_number, message_text, language="en"):

# After  
async def process_incoming_message(
    from_number: str,
    message_text: str,
    language: str = "en"
) -> str:
```

---

### 7.4 Structured Logging
**Problem:** Logs use emoji prefixes (`🔍`, `✅`, `💊`) which are fun but break log parsers (ELK, Grafana Loki).

**Fix:** Use structured JSON logging with fields:
```python
logger.info("symptoms_tracked", extra={
    "session_id": session_id,
    "symptoms": found_symptoms,
    "total_symptoms": len(all_symptoms),
    "source": "phrase_mapping"
})
```

---

### 7.5 Add API Versioning Strategy
**Current:** All routes use `/api/v1/`. Good start, but no plan for v2.

**Fix:** Document the versioning strategy and add deprecation headers when v2 is introduced.

---

## 8. 🟢 FEATURE ENHANCEMENTS (P3 — Roadmap)

### 8.1 WhatsApp Interactive Messages
**Current:** Plain text only.

**Upgrade:** Use WhatsApp's interactive message types:
- **Buttons** — "See Doctor" / "Home Remedy" / "More Details"
- **Lists** — Specialist selection, language selection
- **Templates** — Follow-up reminders

### 8.2 Conversation Analytics Dashboard
- Track: most common symptoms, peak hours, languages used, avg response time
- Use Prometheus metrics already in `requirements.txt`

### 8.3 Feedback Loop
- After each diagnosis, ask "Was this helpful? 👍/👎"
- Track accuracy over time
- Use feedback to improve prompts

### 8.4 Multi-turn Symptom Collection
- Current: AI tries to collect symptoms across messages, but logic is scattered
- Improve: Structured form-like flow: "Where does it hurt?" → "How long?" → "Any other symptoms?" → Diagnosis

### 8.5 Emergency Auto-escalation
- If urgency = "emergency", automatically:
  - Send location-based hospital list
  - Offer to call 108 (ambulance)
  - Notify emergency contact

---

## Summary: Action Priority Matrix

```
                          HIGH IMPACT
                              │
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    │  1.1 Fix secret key     │  2.1 Redis/MongoDB      │
    │  1.2 Lock CORS          │  3.1 Split monster files │
    │  1.3 Webhook signatures │  4.1 Test coverage      │
    │  1.4 Permanent WA token │  6.3 Lazy-load Three.js │
    │                         │                         │
    │      QUICK WINS ◄───────┼────────► PLANNED WORK   │
    │                         │                         │
    │  2.2 Fix memory leak    │  6.4 PWA/offline        │
    │  2.3 Error handling     │  8.1 Interactive msgs   │
    │  5.2 HTTP pooling       │  8.2 Analytics          │
    │  7.1 Complete TODOs     │  8.4 Multi-turn flow    │
    │                         │                         │
    └─────────────────────────┼─────────────────────────┘
                              │
                          LOW IMPACT
```

---

## Recommended Execution Order

| Week | Tasks | Expected Outcome |
|------|-------|-----------------|
| **Week 1** | 1.1, 1.2, 1.3, 1.4, 2.2, 2.3 | Secure & reliable |
| **Week 2** | 2.1 (Redis), 5.1, 5.2, 3.4 | Persistent sessions, faster responses |
| **Week 3** | 4.1 (core tests), 3.2, 7.3 | Testable, less code duplication |
| **Week 4** | 3.1 (split files), 6.1, 6.2 | Maintainable codebase |
| **Month 2** | 6.3, 6.4, 3.3, 7.2 | Production-ready frontend |
| **Month 3** | 8.1, 8.2, 8.3, 8.4 | Feature-complete product |

---

*This plan was generated from a full audit of the CMC Health codebase. Each issue references the exact file and line number where the problem exists.*

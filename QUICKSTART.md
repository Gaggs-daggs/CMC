# 🚀 Quick Start Guide - Multilingual Health AI

## Get Running in 3 Minutes

### Step 1: Start the System

```bash
cd /Users/gugank/CMC
./start.sh
```

This starts:
- MongoDB (database)
- Redis (cache)  
- MQTT (IoT broker)
- FastAPI backend
- Prometheus (metrics)
- Grafana (dashboards)

### Step 2: Access the API

Open your browser: **http://localhost:8000/docs**

You'll see interactive API documentation (Swagger UI).

### Step 3: Test It!

Click on **POST /api/v1/users** → Try it out → Execute

```json
{
  "phone": "+919876543210",
  "preferred_language": "hi",
  "age": 30,
  "gender": "male"
}
```

---

## 📱 Test Vitals Monitoring

### Option 1: IoT Simulator (Easiest)

```bash
cd /Users/gugank/CMC/iot/simulator
python3 vitals_simulator.py
```

Watch it submit:
- ✅ Normal vitals
- ⚠️ Fever detection
- 🚨 Emergency situation

### Option 2: Manual API Call

```bash
curl -X POST http://localhost:8000/api/v1/vitals \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "+919876543210",
    "vitals": {
      "heart_rate": 130,
      "spo2": 89,
      "temperature": 104.0
    }
  }'
```

---

## 🗣️ Test Multilingual Chat

### 1. Start a conversation (in Hindi)

```bash
curl -X POST http://localhost:8000/api/v1/conversation/start \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "+919876543210",
    "language": "hi"
  }'
```

**Response:**
```json
{
  "session_id": "abc-123...",
  "greeting": "नमस्ते! मैं आपका स्वास्थ्य सहायक हूं। कृपया अपने लक्षण बताएं।"
}
```

### 2. Send a message

Use the `session_id` from above:

```bash
curl -X POST http://localhost:8000/api/v1/conversation/message \
  -H 'Content-Type: application/json' \
  -d '{
    "session_id": "abc-123...",
    "message": "मुझे बुखार और सिर दर्द है",
    "language": "hi"
  }'
```

---

## 🎛️ Monitoring & Logs

### Grafana Dashboard
http://localhost:3000
- Username: `admin`
- Password: `admin`

### Backend Logs
```bash
docker-compose logs -f backend
```

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

---

## 🛑 Stop Everything

```bash
cd /Users/gugank/CMC
docker-compose down
```

---

## 📚 Documentation

| Resource | Location |
|----------|----------|
| **API Docs** | http://localhost:8000/docs |
| **Full README** | [README.md](file:///Users/gugank/CMC/README.md) |
| **Project Overview** | [docs/PROJECT_OVERVIEW.md](file:///Users/gugank/CMC/docs/PROJECT_OVERVIEW.md) |
| **Walkthrough** | Implementation walkthrough artifact |
| **Medical Knowledge** | [backend/data/medical_knowledge/knowledge_graph.json](file:///Users/gugank/CMC/backend/data/medical_knowledge/knowledge_graph.json) |

---

## 🔥 What Works Right Now

✅ User profiles with language preferences  
✅ Multilingual greetings (5 languages)  
✅ IoT vitals monitoring with **real-time alerts**  
✅ Conversation history storage  
✅ Medical knowledge graph (7 symptoms, 4 conditions)  
✅ Docker one-command deployment  
✅ Health check monitoring  

---

## 🚧 Coming Next (Phase 3)

🔜 Voice input with Whisper STT  
🔜 Symptom extraction with IndicBERT  
🔜 AI diagnosis engine  
🔜 Emotion detection from voice  
🔜 Multilingual TTS responses  

---

## ⚡ Troubleshooting

**MongoDB won't start?**
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d
```

**Port 8000 already in use?**
```bash
# Edit docker-compose.yml
# Change "8000:8000" to "8080:8000"
```

**Python not found?**
```bash
# Use python3 instead
python3 iot/simulator/vitals_simulator.py
```

---

**Questions?** Check the [walkthrough artifact](file:///Users/gugank/.gemini/antigravity/brain/e3b2a804-ae81-4d0d-80bc-674af0f6d6e8/walkthrough.md) for detailed documentation!

🎉 **You're ready to go! Start building the AI/ML components.** 🚀

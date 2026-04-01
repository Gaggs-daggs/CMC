# Google Fit Smartwatch Integration — Complete Setup Guide

## Overview
This connects your **Redmi Watch** (or any smartwatch) to your CMC Health website through Google Fit.

**Data flow:** `Redmi Watch → Mi Fitness → Apple Health → Google Fit → CMC Health Website`

You'll see **real heart rate, steps, sleep, calories** directly in your chat view.

---

## Step 1: Set Up Google Cloud Project (One-Time, 10 minutes)

### 1.1 Create a Google Cloud Project
1. Go to **[Google Cloud Console](https://console.cloud.google.com/)**
2. Click the project dropdown at the top → **"New Project"**
3. Name it: `CMC Health` → Click **Create**
4. Make sure `CMC Health` is selected as the active project

### 1.2 Enable the Fitness API
1. Go to **[APIs & Services → Library](https://console.cloud.google.com/apis/library)**
2. Search for **"Fitness API"**
3. Click **"Fitness API"** → Click **"Enable"**

### 1.3 Configure OAuth Consent Screen
1. Go to **[APIs & Services → OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)**
2. Choose **"External"** → Click **Create**
3. Fill in:
   - **App name:** `CMC Health`
   - **User support email:** Your Gmail
   - **Developer contact:** Your Gmail
4. Click **Save and Continue**
5. On **Scopes** page, click **"Add or Remove Scopes"** and add these:
   ```
   https://www.googleapis.com/auth/fitness.heart_rate.read
   https://www.googleapis.com/auth/fitness.activity.read
   https://www.googleapis.com/auth/fitness.body.read
   https://www.googleapis.com/auth/fitness.sleep.read
   https://www.googleapis.com/auth/fitness.oxygen_saturation.read
   https://www.googleapis.com/auth/fitness.blood_pressure.read
   https://www.googleapis.com/auth/fitness.body_temperature.read
   ```
6. Click **Save and Continue**
7. On **Test users** page, click **"Add Users"** → Add your Gmail address
8. Click **Save and Continue** → **Back to Dashboard**

### 1.4 Create OAuth2 Credentials
1. Go to **[APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials)**
2. Click **"+ Create Credentials"** → **"OAuth client ID"**
3. Application type: **"Web application"**
4. Name: `CMC Health Web Client`
5. **Authorized JavaScript origins:** Add:
   ```
   http://localhost:5173
   http://localhost:8000
   ```
6. **Authorized redirect URIs:** Add:
   ```
   http://localhost:8000/api/v1/googlefit/callback
   ```
7. Click **Create**
8. **COPY** the `Client ID` and `Client Secret` — you'll need these next!

---

## Step 2: Configure Your Backend (2 minutes)

### 2.1 Create/Edit the `.env` file

```bash
# In your terminal:
nano /Users/gugank/CMC/backend/.env
```

Add these lines (paste your actual Client ID and Secret):

```env
# Google Fit API Credentials
GOOGLE_FIT_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_FIT_CLIENT_SECRET=your-client-secret-here
GOOGLE_FIT_REDIRECT_URI=http://localhost:8000/api/v1/googlefit/callback
```

Save the file (`Ctrl+X → Y → Enter`).

### 2.2 Restart the Backend

```bash
# Kill existing server
lsof -ti :8000 | xargs kill -9

# Start from backend directory
cd /Users/gugank/CMC/backend
PYTHONPATH=/Users/gugank/CMC/backend /Users/gugank/CMC/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --reload-dir /Users/gugank/CMC/backend
```

---

## Step 3: Make Sure Your Watch Syncs to Google Fit

You already have the chain set up:
```
Redmi Watch → Mi Fitness app → Apple Health → Google Fit
```

To verify:
1. Open **Google Fit** app on your phone
2. Go to **Profile** → Check if heart rate, steps, sleep data appear
3. If not, open **Mi Fitness** app → Settings → **Third-party data** → Ensure **Health** is connected
4. Open **Apple Health** → Sharing → Ensure **Google Fit** is listed

---

## Step 4: Connect Google Fit on Your Website

1. Open your website: **http://localhost:5173**
2. Log in with your phone number
3. Start a chat session
4. You'll see a **"Smartwatch Vitals"** panel with a **"Connect"** button
5. Click **Connect** — it will open Google's consent screen
6. Sign in with your Google account and **Allow** all permissions
7. You'll be redirected back to your website
8. The vitals dashboard will appear with your **real heart rate, steps, sleep, calories**!

---

## What Data You'll See

| Vital | Source | Availability |
|-------|--------|-------------|
| Heart Rate (BPM) | Redmi Watch → Mi Fitness → Apple Health → Google Fit | Real-time, every sync |
| Steps | Redmi Watch → Mi Fitness → Apple Health → Google Fit | Daily + 7-day chart |
| Sleep | Redmi Watch → Mi Fitness → Apple Health → Google Fit | Last night (deep/REM/light) |
| Calories | Redmi Watch → Mi Fitness → Apple Health → Google Fit | Daily + 7-day chart |
| SpO2 | Mi Fitness (locked) | NOT available — Xiaomi doesn't export SpO2 |

---

## Architecture

```
┌──────────────┐    Bluetooth    ┌────────────────┐    HealthKit    ┌──────────────┐
│  Redmi Watch │  ──────────→  │  Mi Fitness App  │  ──────────→  │ Apple Health │
│  (Sensors)   │                │  (Zepp Life)     │                │  (iPhone)    │
└──────────────┘                └────────────────┘                └──────┬───────┘
                                                                          │
                                                                  Google Fit Sync
                                                                          │
                                                                          ▼
                              ┌─────────────────────────────────────────────────────┐
                              │                    Google Fit API                     │
                              │  REST: fitness.googleapis.com/fitness/v1/users/me    │
                              └─────────────────────┬───────────────────────────────┘
                                                    │
                                            OAuth2 + REST API
                                                    │
                                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  CMC Health Backend (FastAPI)                                                        │
│                                                                                      │
│  /api/v1/googlefit/auth-url     → Generates Google OAuth2 consent URL               │
│  /api/v1/googlefit/callback     → Handles OAuth2 callback, stores tokens            │
│  /api/v1/googlefit/vitals       → Fetches all vitals (HR, steps, sleep, calories)   │
│  /api/v1/googlefit/heart-rate   → Detailed heart rate with timeline                 │
│  /api/v1/googlefit/steps        → 7-day step count with daily breakdown             │
│  /api/v1/googlefit/sleep        → Sleep stages (deep, REM, light)                   │
│  /api/v1/googlefit/calories     → Calories burned with daily breakdown              │
│  /api/v1/googlefit/status       → Check if Google Fit is connected                  │
│  /api/v1/googlefit/disconnect   → Disconnect Google Fit                             │
└─────────────────────────────────────────────┬───────────────────────────────────────┘
                                              │
                                         REST API
                                              │
                                              ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│  CMC Health Frontend (React)                                                         │
│                                                                                      │
│  VitalsDashboard Component:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────────┐     │
│  │  ❤️ Heart Rate    👟 Steps     🌙 Sleep     🔥 Calories    🫁 SpO2        │     │
│  │  78 bpm           6,432        7.2 hrs       1,847 kcal     98%           │     │
│  │  [timeline chart] [bar chart]  [deep/REM]    [bar chart]    [status]      │     │
│  │                                                                            │     │
│  │  [LIVE] Google Fit · Last synced 5:30 PM                                  │     │
│  └─────────────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Files Created/Modified

### New Files:
- `backend/app/services/google_fit_service.py` — Google Fit API integration service
- `backend/app/routes/google_fit_routes.py` — OAuth2 flow + data endpoints
- `frontend/web/src/components/VitalsDashboard.jsx` — React vitals dashboard component

### Modified Files:
- `backend/app/main.py` — Added Google Fit router
- `backend/app/config.py` — Added Google Fit config settings
- `frontend/web/src/App.jsx` — Imported VitalsDashboard, added Google Fit vitals handler

---

## Troubleshooting

### "Google Fit not configured" error
→ You haven't created the `.env` file with `GOOGLE_FIT_CLIENT_ID` and `GOOGLE_FIT_CLIENT_SECRET`

### "Session expired" error  
→ The OAuth token expired. Click "Disconnect" then "Connect" again

### No data showing after connecting
→ Wait 5-10 minutes for Google Fit to sync from Apple Health
→ Open Google Fit app on phone and check if data appears there first

### SpO2 not showing
→ This is a Xiaomi limitation. Mi Fitness does NOT export SpO2 to Apple Health or Google Fit. Only HR, steps, sleep sync through.

### "redirect_uri_mismatch" error
→ The redirect URI in Google Cloud Console doesn't match. Make sure you added:
```
http://localhost:8000/api/v1/googlefit/callback
```

---

## For Production Deployment

When deploying to a real domain (e.g., `https://cmchealth.com`):

1. Update **Google Cloud Console** redirect URIs:
   ```
   https://your-domain.com/api/v1/googlefit/callback
   ```
2. Update `.env`:
   ```
   GOOGLE_FIT_REDIRECT_URI=https://your-domain.com/api/v1/googlefit/callback
   ```
3. Submit your Google Cloud OAuth app for **verification** (required for 100+ users)

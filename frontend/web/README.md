# Health AI Assistant - Frontend

React.js web interface for the Multilingual AI Symptom Checker.

## Features

- 🌍 **Multilingual Support**: Switch between 12 Indian languages
- 💬 **Real-time Chat**: Interactive chat interface with AI assistant
- 📊 **Vitals Dashboard**: Live monitoring of heart rate, SpO₂, temperature
- 🩺 **Diagnosis Display**: Visual urgency indicators (self-care/doctor/emergency)
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🎨 **Modern UI**: Dark theme with smooth animations

## Quick Start

```bash
cd /Users/gugank/CMC/frontend/web
npm install
npm run dev
```

Then open: http://localhost:5173

**Make sure the backend is running:**
```bash
cd /Users/gugank/CMC
./start.sh
```

## Usage

1. **Enter phone number** (e.g., +919876543210)
2. **Select language** (English, Hindi, Bengali, etc.)
3. **Start consultation**
4. **Describe symptoms** in your language
5. **View diagnosis** with urgency level and recommendations
6. **Monitor vitals** in real-time (click "Simulate Vitals" to test)

## Example Queries

- **English**: "I have fever and headache for 2 days"
- **Hindi**: "मुझे बुखार और सिर दर्द है"
- **Tamil**: "எனக்கு காய்ச்சல் மற்றும் தலைவலி உள்ளது"

## API Configuration

Backend URL is configured in `src/App.jsx`:
```javascript
const API_BASE = 'http://localhost:8000/api/v1'
```

Change this if your backend is running on a different port.

## Build for Production

```bash
npm run build
```

Output will be in `dist/` folder.

## Technologies

- **React 18** - UI framework
- **Vite** - Build tool
- **Vanilla CSS** - Styling (no Tailwind needed!)

## Screenshots

See the walkthrough artifact for screenshots and demo.

---

Built with ❤️ for accessible healthcare

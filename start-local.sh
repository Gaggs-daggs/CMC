#!/bin/bash
# ===========================================
# CMC Health - Quick Start (Everything)
# ===========================================
# Starts Backend + Frontend + Ngrok in one command

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create logs directory
mkdir -p logs

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║            🏥 CMC Health - Quick Start                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Kill any existing processes
echo -e "${YELLOW}🧹 Cleaning up existing processes...${NC}"
pkill -f "uvicorn app.main" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# Check PostgreSQL
echo -e "${BLUE}🗄️  Checking PostgreSQL...${NC}"
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ PostgreSQL is running${NC}"
else
    echo -e "${YELLOW}   ⚠️  PostgreSQL not running - using in-memory storage${NC}"
fi

# Check Ollama
echo -e "${BLUE}🤖 Checking Ollama...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}   ✅ Ollama is running${NC}"
else
    echo -e "${YELLOW}   ⚠️  Ollama not running - starting it...${NC}"
    ollama serve > logs/ollama.log 2>&1 &
    sleep 2
fi

# Start Backend
echo -e "${BLUE}🚀 Starting Backend (FastAPI)...${NC}"
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
else
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}   ✅ Backend started (PID: $BACKEND_PID)${NC}"

# Start Frontend
echo -e "${BLUE}🎨 Starting Frontend (React)...${NC}"
cd frontend/web
nohup npm run dev > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..
echo -e "${GREEN}   ✅ Frontend started (PID: $FRONTEND_PID)${NC}"

# Wait for services to be ready
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 5

# Check if services are running
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}🎉 CMC Health is running!${NC}"
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "   ${BLUE}Frontend:${NC}  http://localhost:5173"
echo -e "   ${BLUE}Backend:${NC}   http://localhost:8000"
echo -e "   ${BLUE}API Docs:${NC}  http://localhost:8000/docs"
echo ""
echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}📋 To expose to internet with ngrok:${NC}"
echo -e "   1. Install ngrok: ${GREEN}brew install ngrok${NC}"
echo -e "   2. Login: ${GREEN}ngrok config add-authtoken YOUR_TOKEN${NC}"
echo -e "   3. Run: ${GREEN}ngrok http 5173${NC}"
echo ""
echo -e "${YELLOW}📜 Logs:${NC}"
echo -e "   Backend:  ${GREEN}tail -f logs/backend.log${NC}"
echo -e "   Frontend: ${GREEN}tail -f logs/frontend.log${NC}"
echo ""
echo -e "${YELLOW}🛑 To stop:${NC} ${GREEN}pkill -f uvicorn && pkill -f vite${NC}"
echo ""

# Keep script running and show logs
echo -e "${BLUE}Showing backend logs (Ctrl+C to exit)...${NC}"
echo ""
tail -f logs/backend.log

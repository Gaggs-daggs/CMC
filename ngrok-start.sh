#!/bin/bash
# ===========================================
# CMC Health - Ngrok Tunnel Script
# ===========================================
# Exposes your local app to the internet for FREE
#
# Prerequisites:
#   1. Install ngrok: brew install ngrok
#   2. Sign up at ngrok.com (free)
#   3. Run: ngrok config add-authtoken YOUR_TOKEN

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         CMC Health - Ngrok Tunnel Setup                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED}❌ ngrok not found. Installing...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install ngrok
    else
        echo "Please install ngrok manually: https://ngrok.com/download"
        exit 1
    fi
fi

# Check if ngrok is authenticated
if ! ngrok config check &> /dev/null; then
    echo -e "${YELLOW}⚠️  ngrok not configured.${NC}"
    echo -e "1. Sign up at ${BLUE}https://ngrok.com${NC} (free)"
    echo -e "2. Get your authtoken from dashboard"
    echo -e "3. Run: ${GREEN}ngrok config add-authtoken YOUR_TOKEN${NC}"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    lsof -i :$1 > /dev/null 2>&1
}

# Start Backend if not running
if ! check_port 8000; then
    echo -e "${YELLOW}🚀 Starting backend server...${NC}"
    cd backend
    source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
    nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
    cd ..
    sleep 3
fi

# Start Frontend if not running
if ! check_port 5173; then
    echo -e "${YELLOW}🚀 Starting frontend server...${NC}"
    cd frontend/web
    nohup npm run dev > ../../logs/frontend.log 2>&1 &
    cd ../..
    sleep 3
fi

# Create logs directory
mkdir -p logs

echo -e "${GREEN}✅ Local servers running:${NC}"
echo -e "   Backend:  http://localhost:8000"
echo -e "   Frontend: http://localhost:5173"

echo ""
echo -e "${BLUE}🌐 Starting ngrok tunnels...${NC}"
echo ""

# Start ngrok with multiple tunnels
# Using ngrok.yml config for multiple tunnels
ngrok start --all --config ngrok.yml


#!/bin/bash
# ===========================================
# CMC Health - Production Deployment Script
# ===========================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════╗"
echo "║       CMC Health - Production Deployment                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${RED}⚠️  Please edit .env file with your production values before continuing.${NC}"
    echo -e "${RED}   Especially update: POSTGRES_PASSWORD and SECRET_KEY${NC}"
    exit 1
fi

# Load environment variables
source .env

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}📋 Checking prerequisites...${NC}"

if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command_exists docker-compose; then
    # Try docker compose (newer syntax)
    if ! docker compose version >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker Compose is not installed.${NC}"
        exit 1
    fi
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo -e "${GREEN}✅ Docker and Docker Compose are available${NC}"

# Parse command line arguments
ACTION=${1:-"up"}

case $ACTION in
    up|start)
        echo -e "\n${BLUE}🚀 Starting CMC Health production deployment...${NC}\n"
        
        # Build and start containers
        $COMPOSE_CMD -f docker-compose.prod.yml up -d --build
        
        echo -e "\n${GREEN}✅ Deployment complete!${NC}"
        echo -e "\n${BLUE}📊 Service Status:${NC}"
        $COMPOSE_CMD -f docker-compose.prod.yml ps
        
        echo -e "\n${BLUE}🔗 Access Points:${NC}"
        echo -e "   Frontend:  http://localhost:${HTTP_PORT:-80}"
        echo -e "   Backend:   http://localhost:${BACKEND_PORT:-8000}"
        echo -e "   API Docs:  http://localhost:${BACKEND_PORT:-8000}/docs"
        ;;
    
    down|stop)
        echo -e "\n${YELLOW}🛑 Stopping CMC Health services...${NC}\n"
        $COMPOSE_CMD -f docker-compose.prod.yml down
        echo -e "${GREEN}✅ Services stopped${NC}"
        ;;
    
    restart)
        echo -e "\n${YELLOW}🔄 Restarting CMC Health services...${NC}\n"
        $COMPOSE_CMD -f docker-compose.prod.yml restart
        echo -e "${GREEN}✅ Services restarted${NC}"
        ;;
    
    logs)
        echo -e "\n${BLUE}📜 Showing logs (Ctrl+C to exit)...${NC}\n"
        $COMPOSE_CMD -f docker-compose.prod.yml logs -f ${2:-}
        ;;
    
    status)
        echo -e "\n${BLUE}📊 Service Status:${NC}\n"
        $COMPOSE_CMD -f docker-compose.prod.yml ps
        ;;
    
    build)
        echo -e "\n${BLUE}🔨 Building containers...${NC}\n"
        $COMPOSE_CMD -f docker-compose.prod.yml build --no-cache
        echo -e "${GREEN}✅ Build complete${NC}"
        ;;
    
    clean)
        echo -e "\n${RED}🧹 Cleaning up (removing containers, volumes, and images)...${NC}\n"
        read -p "Are you sure? This will delete all data! (y/N) " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            $COMPOSE_CMD -f docker-compose.prod.yml down -v --rmi all
            echo -e "${GREEN}✅ Cleanup complete${NC}"
        else
            echo -e "${YELLOW}Cancelled${NC}"
        fi
        ;;
    
    db-backup)
        echo -e "\n${BLUE}💾 Backing up database...${NC}\n"
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        docker exec cmc_postgres pg_dump -U ${POSTGRES_USER:-postgres} ${POSTGRES_DB:-cmc_health} > "./backups/${BACKUP_FILE}"
        echo -e "${GREEN}✅ Database backed up to: backups/${BACKUP_FILE}${NC}"
        ;;
    
    db-restore)
        if [ -z "$2" ]; then
            echo -e "${RED}❌ Please provide backup file: ./deploy.sh db-restore <backup_file>${NC}"
            exit 1
        fi
        echo -e "\n${YELLOW}📥 Restoring database from $2...${NC}\n"
        docker exec -i cmc_postgres psql -U ${POSTGRES_USER:-postgres} ${POSTGRES_DB:-cmc_health} < "$2"
        echo -e "${GREEN}✅ Database restored${NC}"
        ;;
    
    shell)
        SERVICE=${2:-"backend"}
        echo -e "\n${BLUE}🐚 Opening shell in ${SERVICE}...${NC}\n"
        docker exec -it cmc_${SERVICE} /bin/sh
        ;;
    
    *)
        echo "Usage: $0 {up|down|restart|logs|status|build|clean|db-backup|db-restore|shell}"
        echo ""
        echo "Commands:"
        echo "  up, start     - Start all services"
        echo "  down, stop    - Stop all services"
        echo "  restart       - Restart all services"
        echo "  logs [svc]    - Show logs (optionally for specific service)"
        echo "  status        - Show service status"
        echo "  build         - Rebuild all containers"
        echo "  clean         - Remove all containers, volumes, and images"
        echo "  db-backup     - Backup PostgreSQL database"
        echo "  db-restore    - Restore database from backup file"
        echo "  shell [svc]   - Open shell in container (default: backend)"
        exit 1
        ;;
esac

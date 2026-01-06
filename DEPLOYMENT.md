# 🏥 CMC Health - Deployment Guide

## Quick Start (Local Docker)

```bash
# 1. Clone the repository
git clone https://github.com/Gaggs-daggs/CMC.git
cd CMC

# 2. Copy environment file and configure
cp .env.example .env
# Edit .env with your settings (especially passwords!)

# 3. Make deploy script executable
chmod +x deploy.sh

# 4. Start all services
./deploy.sh up
```

## 📦 Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Nginx     │────▶│   Frontend  │     │   MQTT      │
│  (Reverse   │     │   (React)   │     │ (Mosquitto) │
│   Proxy)    │     │   :3000     │     │   :1883     │
│    :80/443  │     └─────────────┘     └─────────────┘
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Backend   │────▶│ PostgreSQL  │     │    Redis    │
│  (FastAPI)  │     │   :5432     │     │   :6379     │
│   :8000     │     └─────────────┘     └─────────────┘
└─────────────┘
       │
       ▼
┌─────────────┐
│   Ollama    │
│  (AI/LLM)   │
│   :11434    │
└─────────────┘
```

## 🚀 Deployment Options

### Option 1: Docker Compose (Recommended)

Best for: VPS, Cloud VM, On-premise servers

```bash
# Production deployment
./deploy.sh up

# Check status
./deploy.sh status

# View logs
./deploy.sh logs

# Stop services
./deploy.sh down
```

### Option 2: AWS EC2

1. Launch an EC2 instance (recommended: t3.medium or larger)
2. Install Docker and Docker Compose:
   ```bash
   sudo yum update -y
   sudo yum install -y docker
   sudo service docker start
   sudo usermod -aG docker ec2-user
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```
3. Clone repo and deploy:
   ```bash
   git clone https://github.com/Gaggs-daggs/CMC.git
   cd CMC
   cp .env.example .env
   nano .env  # Edit configuration
   chmod +x deploy.sh
   ./deploy.sh up
   ```

### Option 3: DigitalOcean Droplet

1. Create a Droplet (recommended: 4GB RAM, 2 vCPUs)
2. Use Docker 1-Click Image or install manually
3. Follow same steps as AWS EC2

### Option 4: Google Cloud Platform (GCP)

1. Create a Compute Engine VM
2. Enable HTTP/HTTPS traffic
3. SSH into VM and follow deployment steps

### Option 5: Azure Container Instances

```bash
# Create resource group
az group create --name cmc-health --location eastus

# Deploy using docker-compose
az container create \
  --resource-group cmc-health \
  --name cmc-health-app \
  --image your-registry/cmc-backend \
  --dns-name-label cmc-health \
  --ports 80 443
```

## 🔒 SSL/HTTPS Setup

### Using Let's Encrypt (Recommended)

```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d yourdomain.com

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ./nginx/ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ./nginx/ssl/

# Update nginx.conf to enable HTTPS (uncomment HTTPS server block)
```

### Auto-renewal

```bash
# Add to crontab
0 0 1 * * certbot renew --quiet && docker restart cmc_nginx
```

## 🗄️ Database Management

### Backup Database

```bash
./deploy.sh db-backup
# Creates: backups/backup_YYYYMMDD_HHMMSS.sql
```

### Restore Database

```bash
./deploy.sh db-restore backups/backup_file.sql
```

### Connect to Database

```bash
# Via Docker
docker exec -it cmc_postgres psql -U postgres -d cmc_health

# Or using connection string
psql postgresql://postgres:your_password@localhost:5432/cmc_health
```

## 🤖 AI/Ollama Setup

The application requires Ollama for AI features. Options:

### Option A: Run Ollama on Host (Recommended)

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull required models
ollama pull medllama2
ollama pull llama3.2

# Ollama runs on http://localhost:11434
# Docker containers access via host.docker.internal
```

### Option B: Run Ollama in Docker

Add to docker-compose.prod.yml:
```yaml
ollama:
  image: ollama/ollama
  container_name: cmc_ollama
  volumes:
    - ollama_data:/root/.ollama
  ports:
    - "11434:11434"
  networks:
    - cmc_network
```

Then update OLLAMA_HOST in .env:
```
OLLAMA_HOST=http://ollama:11434
```

## 📊 Monitoring

### View Logs

```bash
# All services
./deploy.sh logs

# Specific service
./deploy.sh logs backend
./deploy.sh logs postgres
./deploy.sh logs nginx
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Check all containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| POSTGRES_DB | Database name | cmc_health |
| POSTGRES_USER | Database user | postgres |
| POSTGRES_PASSWORD | Database password | (required) |
| SECRET_KEY | App secret key | (required) |
| OLLAMA_HOST | Ollama API URL | http://host.docker.internal:11434 |
| LOG_LEVEL | Logging level | info |

### Ports

| Service | Internal | External |
|---------|----------|----------|
| Nginx | 80/443 | 80/443 |
| Frontend | 80 | 3000 |
| Backend | 8000 | 8000 |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |
| MQTT | 1883/9001 | 1883/9001 |

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs
docker logs cmc_backend

# Check container status
docker inspect cmc_backend
```

### Database connection issues

```bash
# Check if PostgreSQL is running
docker exec cmc_postgres pg_isready

# Check database logs
docker logs cmc_postgres
```

### Frontend not loading

```bash
# Rebuild frontend
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

### AI not responding

```bash
# Check Ollama is accessible
curl http://localhost:11434/api/tags

# Check if models are downloaded
ollama list
```

## 🔄 Updates

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
./deploy.sh build
./deploy.sh up
```

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/Gaggs-daggs/CMC/issues
- Documentation: See `/docs` folder

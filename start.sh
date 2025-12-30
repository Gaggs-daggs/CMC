#!/bin/bash

# Quick start script for Multilingual Health AI

echo "=================================="
echo "Multilingual Health AI - Quick Start"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker is installed"
echo ""

# Start services
echo "Starting services with Docker Compose..."
echo ""
docker-compose up -d

echo ""
echo "=================================="
echo "Services Status:"
echo "=================================="
docker-compose ps

echo ""
echo "=================================="
echo "Access Points:"
echo "=================================="
echo "📍 API Documentation: http://localhost:8000/docs"
echo "📍 API Health Check:  http://localhost:8000/api/v1/health"
echo "📍 MongoDB:           localhost:27017"
echo "📍 Redis:             localhost:6379"
echo "📍 MQTT Broker:       localhost:1883"
echo "📍 Grafana:           http://localhost:3000 (admin/admin)"
echo "📍 Prometheus:        http://localhost:9090"
echo ""

echo "=================================="
echo "Quick Test Commands:"
echo "=================================="
echo ""
echo "1. Create a user:"
echo "   curl -X POST http://localhost:8000/api/v1/users \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"phone\": \"+919876543210\", \"preferred_language\": \"hi\", \"age\": 30}'"
echo ""
echo "2. Run IoT simulator:"
echo "   cd iot/simulator && python vitals_simulator.py"
echo ""

echo "To stop services: docker-compose down"
echo "To view logs: docker-compose logs -f backend"
echo ""
echo "✓ Setup complete! Visit http://localhost:8000/docs to explore the API"
echo ""

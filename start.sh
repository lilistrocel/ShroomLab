#!/bin/bash

# ShroomLab Quick Start Script

echo "🍄 Starting ShroomLab Development Environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env exists, create from example if not
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env 2>/dev/null || echo "⚠️  Please create .env file manually"
fi

# Build and start all services
echo "🚀 Building and starting all services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check API Gateway
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API Gateway is running (http://localhost:8000)"
else
    echo "❌ API Gateway is not responding"
fi

# Check Frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running (http://localhost:3000)"
else
    echo "❌ Frontend is not responding"
fi

# Check InfluxDB
if curl -s http://localhost:8086/health > /dev/null; then
    echo "✅ InfluxDB is running (http://localhost:8086)"
else
    echo "❌ InfluxDB is not responding"
fi

echo ""
echo "🎉 ShroomLab is starting up!"
echo ""
echo "📊 Access Points:"
echo "   Frontend:        http://localhost:3000"
echo "   API Gateway:     http://localhost:8000"
echo "   API Docs:        http://localhost:8000/docs"
echo "   InfluxDB UI:     http://localhost:8086"
echo ""
echo "🔑 Default Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📝 To view logs: docker-compose logs -f [service-name]"
echo "🛑 To stop: docker-compose down"
echo "" 
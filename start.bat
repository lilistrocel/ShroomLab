@echo off
REM ShroomLab Quick Start Script for Windows

echo 🍄 Starting ShroomLab Development Environment...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if .env exists, create from example if not
if not exist .env (
    echo 📝 Creating .env file from template...
    if exist .env.example (
        copy .env.example .env >nul
    ) else (
        echo ⚠️  Please create .env file manually
    )
)

REM Build and start all services
echo 🚀 Building and starting all services...
docker-compose up --build -d

REM Wait for services to be ready
echo ⏳ Waiting for services to initialize...
timeout /t 30 /nobreak >nul

REM Check service health
echo 🔍 Checking service health...

REM Check API Gateway
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API Gateway is running ^(http://localhost:8000^)
) else (
    echo ❌ API Gateway is not responding
)

REM Check Frontend
curl -s http://localhost:3000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Frontend is running ^(http://localhost:3000^)
) else (
    echo ❌ Frontend is not responding
)

REM Check InfluxDB
curl -s http://localhost:8086/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ InfluxDB is running ^(http://localhost:8086^)
) else (
    echo ❌ InfluxDB is not responding
)

echo.
echo 🎉 ShroomLab is starting up!
echo.
echo 📊 Access Points:
echo    Frontend:        http://localhost:3000
echo    API Gateway:     http://localhost:8000
echo    API Docs:        http://localhost:8000/docs
echo    InfluxDB UI:     http://localhost:8086
echo.
echo 🔑 Default Login:
echo    Username: admin
echo    Password: admin123
echo.
echo 📝 To view logs: docker-compose logs -f [service-name]
echo 🛑 To stop: docker-compose down
echo.
pause
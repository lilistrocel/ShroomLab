# ShroomLab

A comprehensive mushroom farm management system with IoT integration, real-time monitoring, and business operations management.

## 🍄 Project Overview

ShroomLab is a modular API Hub and central management system designed for mushroom farm operations. It provides:

- **IoT & Sensor Control**: Real-time monitoring and control of farm sensors
- **Production Management**: Track inputs, outputs, and growing processes
- **Business Operations**: HR, Finance, Delivery, and Reporting modules
- **Real-time Dashboard**: Live data visualization and alerts
- **Multi-farm Support**: Manage multiple farm locations

## 🏗️ Architecture

### Microservices Architecture
- **API Gateway** (FastAPI): Central authentication and routing
- **IoT Service** (Python): Sensor data and device management
- **Business Service** (Python): HR, Finance, Production management
- **Analytics Service** (Python): Reports and data analysis
- **Frontend** (React/Next.js): Modern web interface

### Technology Stack
- **Backend**: Python with FastAPI
- **Frontend**: React with Next.js
- **Databases**: 
  - MySQL (relational data)
  - InfluxDB (time-series sensor data)
  - Redis (caching & sessions)
- **Message Queue**: MQTT for IoT communications
- **Infrastructure**: Docker & Docker Compose

## 🚀 Quick Start

### Prerequisites
**Development (Windows):**
- Docker Desktop for Windows
- Git for Windows
- Windows Terminal (recommended)

**Development (Linux/macOS):**
- Docker and Docker Compose
- Git

**Production (Ubuntu):**
- Ubuntu 20.04+ server
- Sudo privileges
- Internet connection

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ShroomLab
   ```

2. **Set up environment variables**
   ```bash
   # Linux/macOS
   cp .env.example .env
   
   # Windows
   copy .env.example .env
   ```

3. **Start all services**
   
   **Windows (Development):**
   ```cmd
   start.bat
   ```
   
   **Linux/macOS (Development):**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```
   
   **Manual start (Any OS):**
   ```bash
   docker-compose up -d
   ```

   **Ubuntu (Production Deployment):**
   ```bash
   chmod +x deploy-ubuntu.sh
   ./deploy-ubuntu.sh
   ```

4. **Access the application**
   - **Frontend**: http://localhost:3000
   - **API Gateway**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **InfluxDB UI**: http://localhost:8086
   - **MySQL**: localhost:3306

### Default Credentials
- **Username**: admin
- **Password**: admin123

## 📊 Services

### API Gateway (Port 8000)
- User authentication and authorization
- Farm management
- Central API routing
- WebSocket connections for real-time data

### IoT Service (Port 8001)
- Sensor data ingestion
- Device management
- MQTT message handling
- Real-time data streaming

### Business Service (Port 8002)
- Production cycle management
- HR and employee management
- Financial tracking
- Inventory management

### Analytics Service (Port 8003)
- Data analysis and reporting
- Dashboard metrics
- Performance analytics
- Predictive insights

### Frontend (Port 3000)
- Modern React-based web interface
- Real-time dashboards
- Mobile-responsive design
- Chart visualizations

## 🛠️ Development

### Project Structure
```
ShroomLab/
├── services/
│   ├── api-gateway/       # FastAPI main service
│   ├── iot-service/       # IoT and sensor management
│   ├── business-service/  # Business operations
│   └── analytics-service/ # Reports and analytics
├── frontend/              # React/Next.js web app
├── database/
│   └── mysql/init/       # Database initialization
├── config/
│   ├── nginx/            # Reverse proxy config
│   └── mosquitto/        # MQTT broker config
├── docker-compose.yml    # Main orchestration
└── DevLog.md            # Development tracking
```

### Adding New Features

1. Check the `DevLog.md` for current development phase
2. Choose the appropriate service for your feature
3. Follow the existing code patterns
4. Update API documentation
5. Add tests for new functionality

### Database Management

**MySQL (Relational Data)**
- User accounts and authentication
- Farm configurations
- Production cycles
- Business data

**InfluxDB (Time-series Data)**
- Sensor readings (temperature, humidity, etc.)
- Device status logs
- Performance metrics

**Redis (Caching)**
- Session management
- Real-time data caching
- Message queuing

## 📈 Monitoring

### Real-time Monitoring
- Sensor data visualization
- Alert notifications
- System health checks
- Performance metrics

### Available Dashboards
- Farm overview and status
- Sensor readings and trends
- Production cycle tracking
- Business performance metrics

## 🔧 Configuration

### Environment Variables
See `.env.example` for all available configuration options.

### Sensor Types Supported
- Temperature sensors
- Humidity sensors
- CO2 levels
- pH sensors
- Light sensors
- Motion detectors

### MQTT Topics
- `sensors/{farm_id}/{sensor_type}` - Sensor data
- `alerts/{farm_id}` - Alert notifications
- `commands/{device_id}` - Device commands

## 🚀 Deployment

### Development vs Production

**Windows Development:**
- Use `start.bat` for quick development setup
- Docker Desktop handles container management
- All services run on localhost

**Ubuntu Production:**
- Use `deploy-ubuntu.sh` for automated production setup
- Includes systemd service, firewall configuration, and backups
- Production-ready with proper security and monitoring

### Production Deployment Features
- Automatic Docker and Docker Compose installation
- Systemd service for auto-startup
- UFW firewall configuration
- Log rotation setup
- Automated backup script
- Production environment variables
- Persistent data volumes

### Scaling
The microservices architecture allows for horizontal scaling of individual components based on load.

## 📝 API Documentation

Once running, visit:
- **API Gateway Docs**: http://localhost:8000/docs
- **IoT Service Docs**: http://localhost:8001/docs
- **Business Service Docs**: http://localhost:8002/docs
- **Analytics Service Docs**: http://localhost:8003/docs

## 🤝 Contributing

1. Check the development status in `DevLog.md`
2. Create a feature branch
3. Follow the existing code style
4. Add tests for new features
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
1. Check the `DevLog.md` for current development status
2. Review API documentation
3. Check Docker logs: `docker-compose logs [service-name]`
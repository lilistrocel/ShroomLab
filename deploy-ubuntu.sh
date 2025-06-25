#!/bin/bash

# ShroomLab Ubuntu Production Deployment Script

set -e  # Exit on any error

echo "🍄 ShroomLab Production Deployment for Ubuntu"
echo "=============================================="

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  This script should not be run as root. Use a regular user with sudo privileges."
   exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed. Please log out and back in, then re-run this script."
    exit 0
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo "🐳 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create production environment file
if [ ! -f .env ]; then
    echo "📝 Creating production .env file..."
    cp .env.example .env
    
    # Generate a secure secret key
    SECRET_KEY=$(openssl rand -hex 32)
    sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" .env
    
    echo "⚠️  Please review and update the .env file with your production settings:"
    echo "   - Database passwords"
    echo "   - InfluxDB tokens"
    echo "   - Domain names"
    echo "   - SSL certificates"
    echo ""
    echo "Press Enter when ready to continue..."
    read
fi

# Create necessary directories
echo "📁 Creating directories..."
sudo mkdir -p /var/log/shroomlab
sudo mkdir -p /var/lib/shroomlab/mysql
sudo mkdir -p /var/lib/shroomlab/influxdb
sudo mkdir -p /var/lib/shroomlab/redis
sudo mkdir -p /var/lib/shroomlab/mqtt

# Set proper permissions
sudo chown -R $USER:$USER /var/lib/shroomlab
sudo chown -R $USER:$USER /var/log/shroomlab

# Configure firewall (UFW)
echo "🔥 Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 3306/tcp  # MySQL (if external access needed)
sudo ufw allow 8086/tcp  # InfluxDB (if external access needed)

# Create production Docker Compose override
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  api-gateway:
    restart: unless-stopped
    environment:
      - ENV=production
    volumes:
      - /var/log/shroomlab:/app/logs

  iot-service:
    restart: unless-stopped
    volumes:
      - /var/log/shroomlab:/app/logs

  business-service:
    restart: unless-stopped
    volumes:
      - /var/log/shroomlab:/app/logs

  analytics-service:
    restart: unless-stopped
    volumes:
      - /var/log/shroomlab:/app/logs

  frontend:
    restart: unless-stopped

  mysql:
    restart: unless-stopped
    volumes:
      - /var/lib/shroomlab/mysql:/var/lib/mysql
      - ./database/mysql/init:/docker-entrypoint-initdb.d

  influxdb:
    restart: unless-stopped
    volumes:
      - /var/lib/shroomlab/influxdb:/var/lib/influxdb2

  redis:
    restart: unless-stopped
    volumes:
      - /var/lib/shroomlab/redis:/data

  mqtt-broker:
    restart: unless-stopped
    volumes:
      - /var/lib/shroomlab/mqtt:/mosquitto/data

  nginx:
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"

EOF

# Create systemd service for auto-start
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/shroomlab.service > /dev/null << EOF
[Unit]
Description=ShroomLab Mushroom Farm Management System
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$(pwd)
ExecStart=/usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
User=$USER
Group=$USER

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable shroomlab.service

# Build and start the application
echo "🚀 Building and starting ShroomLab..."
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
sleep 60

# Check service health
echo "🔍 Checking service health..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ ShroomLab is running successfully!"
        break
    fi
    echo "⏳ Attempt $i/10 - Waiting for services..."
    sleep 10
done

# Setup log rotation
echo "📝 Setting up log rotation..."
sudo tee /etc/logrotate.d/shroomlab > /dev/null << 'EOF'
/var/log/shroomlab/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 1000 1000
    postrotate
        docker-compose -f /path/to/shroomlab/docker-compose.yml -f /path/to/shroomlab/docker-compose.prod.yml restart > /dev/null 2>&1 || true
    endscript
}
EOF

# Create backup script
echo "💾 Creating backup script..."
cat > backup.sh << 'EOF'
#!/bin/bash
# ShroomLab Backup Script

BACKUP_DIR="/var/backups/shroomlab"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup MySQL
docker exec shroomlab-mysql mysqldump -u root -p$MYSQL_ROOT_PASSWORD shroomlab > $BACKUP_DIR/mysql_$DATE.sql

# Backup InfluxDB
docker exec shroomlab-influxdb influx backup $BACKUP_DIR/influxdb_$DATE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -type d -name "influxdb_*" -mtime +7 -exec rm -rf {} +

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

echo ""
echo "🎉 ShroomLab Production Deployment Complete!"
echo ""
echo "📊 Access Points:"
echo "   Frontend:        http://$(hostname -I | awk '{print $1}'):3000"
echo "   API Gateway:     http://$(hostname -I | awk '{print $1}'):8000"
echo "   API Docs:        http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "🔧 Management Commands:"
echo "   Start:   sudo systemctl start shroomlab"
echo "   Stop:    sudo systemctl stop shroomlab"
echo "   Status:  sudo systemctl status shroomlab"
echo "   Logs:    docker-compose logs -f"
echo "   Backup:  ./backup.sh"
echo ""
echo "⚠️  Next Steps:"
echo "   1. Configure SSL certificates for HTTPS"
echo "   2. Set up domain name and DNS"
echo "   3. Configure automated backups (cron job)"
echo "   4. Set up monitoring and alerting"
echo "   5. Review and harden security settings"
echo "" 
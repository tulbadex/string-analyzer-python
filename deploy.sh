#!/bin/bash

# String Analyzer API Deployment Script for Ubuntu Server

echo "🚀 Starting String Analyzer API Deployment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
echo "🐍 Installing Python 3..."
sudo apt install -y python3 python3-pip python3-venv

# Install Nginx
echo "🌐 Installing Nginx..."
sudo apt install -y nginx

# Install Git (if not already installed)
sudo apt install -y git

# Clean up existing PHP files and setup directory
echo "🧹 Cleaning up existing files..."
sudo rm -rf /var/www/string-analyzer-api
sudo mkdir -p /var/www/string-analyzer-api
sudo chown -R $USER:$USER /var/www/string-analyzer-api

# Clone or pull from repository
echo "📥 Setting up repository..."
cd /var/www
if [ -d "string-analyzer-api/.git" ]; then
    echo "Repository exists, pulling latest changes..."
    cd string-analyzer-api
    git pull origin main
else
    echo "Cloning repository for first time..."
    git clone git@github.com:tulbadex/string-analyzer-python.git string-analyzer-api
    cd string-analyzer-api
fi

# Create virtual environment
echo "🔧 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service file
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/string-analyzer.service > /dev/null <<EOF
[Unit]
Description=String Analyzer FastAPI Application
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=/var/www/string-analyzer-api
Environment="PATH=/var/www/string-analyzer-api/venv/bin"
ExecStart=/var/www/string-analyzer-api/venv/bin/uvicorn main:api --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create Nginx configuration
echo "🔧 Configuring Nginx..."
sudo tee /etc/nginx/sites-available/string-analyzer > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/string-analyzer /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Start and enable services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable string-analyzer
sudo systemctl start string-analyzer
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check service status
echo "✅ Checking service status..."
sudo systemctl status string-analyzer --no-pager
sudo systemctl status nginx --no-pager

echo "🎉 Deployment completed!"
echo "📍 API should be available at: http://54.241.80.160/"
echo "📖 API documentation at: http://54.241.80.160/docs"

# Show logs command
echo "📋 To view logs, run: sudo journalctl -u string-analyzer -f"
#!/bin/bash

# Fraud Detection Model Deployment Script for AWS EC2
# This script automates the setup process

set -e

echo "================================"
echo "Fraud Detection Model Deployment"
echo "================================"
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo "Error: This script is for Ubuntu/Debian systems"
    exit 1
fi

# Step 1: Update system packages
echo "[1/7] Updating system packages..."
sudo apt update
sudo apt upgrade -y
echo "✓ System packages updated"
echo ""

# Step 2: Install Python and dependencies
echo "[2/7] Installing Python and dependencies..."
sudo apt install -y python3-pip python3-venv python3-dev
echo "✓ Python installed"
echo ""

# Step 3: Create project directory structure
echo "[3/7] Setting up project directory..."
PROJECT_DIR="$HOME/FroudDet_AWS"

if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
    echo "Created project directory: $PROJECT_DIR"
else
    echo "Project directory already exists"
fi

cd "$PROJECT_DIR"
echo "✓ Working directory: $(pwd)"
echo ""

# Step 4: Create Python virtual environment
echo "[4/7] Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Step 5: Install Python packages
echo "[5/7] Installing Python packages..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Python packages installed"
else
    echo "Warning: requirements.txt not found"
fi
echo ""

# Step 6: Create systemd service
echo "[6/7] Creating systemd service..."

SERVICE_CONTENT="[Unit]
Description=Fraud Detection Model API
After=network.target

[Service]
User=$(whoami)
WorkingDirectory=$PROJECT_DIR
Environment=\"PATH=$PROJECT_DIR/venv/bin\"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 --timeout 120 main:app
Restart=always

[Install]
WantedBy=multi-user.target"

echo "$SERVICE_CONTENT" | sudo tee /etc/systemd/system/fraud-detection.service > /dev/null
sudo systemctl daemon-reload
echo "✓ Systemd service created"
echo ""

# Step 7: Configure firewall
echo "[7/7] Configuring firewall..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 22/tcp
    sudo ufw allow 5000/tcp
    echo "✓ Firewall configured"
else
    echo "⚠ UFW not installed, skipping firewall configuration"
fi
echo ""

echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Copy the model file to $PROJECT_DIR:"
echo "   scp voting_classifier_model.pkl ubuntu@your_instance_ip:$PROJECT_DIR/"
echo ""
echo "2. Start the service:"
echo "   sudo systemctl start fraud-detection"
echo ""
echo "3. Enable auto-start:"
echo "   sudo systemctl enable fraud-detection"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status fraud-detection"
echo ""
echo "5. View logs:"
echo "   sudo journalctl -u fraud-detection -f"
echo ""
echo "6. Test the API:"
echo "   curl http://localhost:5000/health"
echo ""
echo "For more information, see AWS_DEPLOYMENT.md"

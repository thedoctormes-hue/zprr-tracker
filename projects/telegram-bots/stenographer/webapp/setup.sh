#!/bin/bash
# Stenographer WebApp Setup Script

set -e

echo "🚀 Setting up Stenographer WebApp..."

# Create directories
sudo mkdir -p /var/lib/stenographer/uploads
sudo mkdir -p /var/lib/stenographer/uploads/chunks

# Set permissions
sudo chown -R root:root /var/lib/stenographer

# Install Python deps
pip install -r /root/LabDoctorM/projects/telegram-bots/stenographer/webapp/requirements.txt

# Copy systemd service
sudo cp webapp.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable stenographer-webapp
sudo systemctl start stenographer-webapp

echo "✅ WebApp setup complete!"
echo "📝 Add to nginx: proxy_pass http://localhost:8000"
echo "🔗 WebApp URL: https://files.stenographerobot.com"
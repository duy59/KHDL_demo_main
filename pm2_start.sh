#!/bin/bash

echo "🚀 Starting Association Rule Mining with PM2..."

# Create logs directory
mkdir -p logs

# Activate virtual environment first
source venv/bin/activate

# Start with PM2
pm2 start ecosystem.config.js

# Show status
pm2 status

# Show logs
echo "📊 Application started! Check status with:"
echo "pm2 status"
echo "pm2 logs association-mining"
echo "pm2 stop association-mining"
echo "pm2 restart association-mining"
echo ""
echo "🌐 Access at: http://vuquangduy.online:9005"

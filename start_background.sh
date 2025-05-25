#!/bin/bash

echo "🚀 Starting Association Rule Mining in background..."

# Activate virtual environment
source venv/bin/activate

# Start with nohup
nohup python app.py > app.log 2>&1 &

# Get process ID
PID=$!
echo $PID > app.pid

echo "✅ Application started in background!"
echo "📊 Process ID: $PID"
echo "📝 Logs: tail -f app.log"
echo "🛑 Stop: kill $PID"
echo "🌐 Access at: http://vuquangduy.online:9005"

#!/bin/bash

echo "🛑 Stopping Association Rule Mining..."

if [ -f app.pid ]; then
    PID=$(cat app.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        echo "✅ Application stopped (PID: $PID)"
        rm app.pid
    else
        echo "❌ Process not running"
        rm app.pid
    fi
else
    echo "❌ PID file not found"
    # Try to kill by port
    PID=$(lsof -ti:9005)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo "✅ Killed process on port 9005 (PID: $PID)"
    else
        echo "❌ No process found on port 9005"
    fi
fi

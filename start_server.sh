#!/bin/bash

# Association Rule Mining Web App Startup Script
# Port: 9005
# Domain: vuquangduy.online

echo "🚀 Starting Association Rule Mining Web App..."
echo "📍 Domain: vuquangduy.online"
echo "🔌 Port: 9005"
echo "📅 Started at: $(date)"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python3."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Please install pip3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if all required files exist
required_files=("app.py" "clean_data.py" "apriori_test.py" "fpgrowth_test.py" "code_lib.py" "stockcode_description.csv")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done

echo "✅ All required files found"

# Create uploads directory if it doesn't exist
mkdir -p uploads
mkdir -p temp

# Set permissions
chmod 755 uploads
chmod 755 temp

echo "📁 Directories created and permissions set"

# Start the Flask application
echo "🌟 Starting Flask application on port 9005..."
echo "🌐 Access at: http://vuquangduy.online:9005"
echo "📊 Association Rule Mining Web Interface"
echo "----------------------------------------"

# Make sure we're still in virtual environment
source venv/bin/activate
python app.py

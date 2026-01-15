#!/bin/bash
# Quick start script for Yambda Music Analysis System

echo "=================================="
echo "Yambda Music Analysis System"
echo "=================================="
echo ""

# Check if data exists
if [ ! -f "data/yambda.db" ]; then
    echo "📊 No data found. Running data preprocessing and ML training..."
    python run.py
    if [ $? -ne 0 ]; then
        echo "❌ Error: Data processing failed"
        exit 1
    fi
    echo ""
fi

echo "🚀 Starting dashboard server..."
echo "📍 Dashboard will be available at: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app.py

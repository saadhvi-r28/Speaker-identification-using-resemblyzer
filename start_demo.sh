#!/bin/bash
# Start Resemblyzer Voice Security Demo (Standalone)

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🎙️  Resemblyzer Voice Security Demo"
echo "===================================="
echo ""

# Check if Flask API is already running
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Flask API already running on port 5001"
else
    echo "Starting Flask API with Resemblyzer..."
    cd "$PROJECT_DIR/api"
    source "$PROJECT_DIR/resemblyzer_starter/.venv/bin/activate"
    PYTHONPATH="$PROJECT_DIR" nohup python app_resemblyzer.py > resemblyzer_api.log 2>&1 &
    API_PID=$!
    echo "✅ Flask API started (PID: $API_PID)"
    cd "$PROJECT_DIR"
    sleep 3
fi

# Check if HTTP server is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  HTTP server already running on port 8000"
else
    echo "Starting demo frontend..."
    cd "$PROJECT_DIR/resemblyzer_starter/demo_frontend"
    nohup python3 -m http.server 8000 > http_server.log 2>&1 &
    HTTP_PID=$!
    echo "✅ Demo frontend started (PID: $HTTP_PID)"
    cd "$PROJECT_DIR"
    sleep 2
fi

echo ""
echo "===================================="
echo "🚀 Demo is ready!"
echo ""
echo "📍 Open in your browser:"
echo "   http://localhost:8000"
echo ""
echo "🔌 API running at:"
echo "   http://localhost:5001/api/health"
echo ""
echo "💡 Quick Test:"
echo "   1. Click 'Start Recording' and speak for 5 seconds"
echo "   2. Enter your name and ID, click 'Register Speaker'"
echo "   3. Record again and test 'Verify' or 'Identify'"
echo ""
echo "🛑 To stop:"
echo "   pkill -f 'app_resemblyzer.py'"
echo "   pkill -f 'http.server 8000'"
echo ""

# Open browser
if command -v open &> /dev/null; then
    sleep 1
    open http://localhost:8000
fi

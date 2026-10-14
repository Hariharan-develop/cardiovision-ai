#!/usr/bin/env bash
set -e

echo "==============================================================================="
echo "  CardioVision AI - Startup Script (Linux / macOS)"
echo "  IIT Mandi Multimodal AI Hackathon 2026 - Track A"
echo "==============================================================================="

# 1. Validate Python
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "[ERROR] Python 3 is not found on your system PATH."
        exit 1
    else
        PY_CMD="python"
    fi
else
    PY_CMD="python3"
fi

# 2. Check for port conflicts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

if lsof -Pi :8502 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "[WARNING] Port 8502 is already occupied. Attempting clean shutdown..."
    lsof -ti:8502 | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# 3. Verify models exist
if [ ! -f "models/cad_model.pkl" ] && [ ! -f "cad_model.pkl" ]; then
    echo "[ERROR] Model files missing! Expected models/cad_model.pkl"
    exit 1
fi

echo "[INFO] Starting CardioVision AI Server on http://127.0.0.1:8502/dashboard..."
echo "[INFO] Press Ctrl+C in this terminal to shut down the server."
echo "==============================================================================="

exec "$PY_CMD" api_server.py

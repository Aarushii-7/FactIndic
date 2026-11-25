#!/bin/bash
# FactIndic: Launch UI & Backend Server
# Serves the complete React frontend + FastAPI backend

cd /Users/aarushi/factIndic
source .venv/bin/activate

PORT=8000
if lsof -i :8000 >/dev/null 2>&1; then
    echo "Notice: Port 8000 is in use by another service (e.g. Docker container). Using port 8001."
    PORT=8001
fi

echo "=========================================================="
echo "STARTING FACTINDIC WEB APPLICATION"
echo "Frontend & API: http://localhost:$PORT"
echo "Interactive API Docs: http://localhost:$PORT/docs"
echo "=========================================================="

python3 -m uvicorn app:app --host 0.0.0.0 --port $PORT

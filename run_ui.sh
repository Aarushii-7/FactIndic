#!/bin/bash
# FactIndic: Launch UI & Backend Server
# Serves the complete React frontend + FastAPI backend on port 8000

cd /Users/aarushi/factIndic
source .venv/bin/activate

echo "=========================================================="
echo "STARTING FACTINDIC WEB APPLICATION"
echo "Frontend & API: http://localhost:8000"
echo "Interactive API Docs: http://localhost:8000/docs"
echo "=========================================================="

python3 -m uvicorn app:app --host 0.0.0.0 --port 8000

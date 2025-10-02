#!/bin/bash
echo "=== PropPulse AI Backend Startup ==="
echo "Python version:"
python3 --version
echo "Current directory:"
pwd
echo "Installing requirements..."
python3 -m pip install --upgrade pip
python3 -m pip install -r backend/requirements.txt
echo "Starting FastAPI server..."
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

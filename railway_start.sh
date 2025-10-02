#!/bin/bash
echo "=== PropPulse AI Backend Startup ==="

# Try to find Python executable
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "ERROR: Python not found!"
    exit 1
fi

echo "Using Python command: $PYTHON_CMD"
echo "Python version:"
$PYTHON_CMD --version
echo "Current directory:"
pwd

echo "Installing requirements..."
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r backend/requirements.txt

echo "Starting FastAPI server..."
cd backend
$PYTHON_CMD -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

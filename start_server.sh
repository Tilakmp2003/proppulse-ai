#!/bin/bash
set -e

echo "=== PropPulse AI Backend Startup ==="
echo "Available commands:"
which python3 2>/dev/null || echo "python3 not found"
which python 2>/dev/null || echo "python not found" 
which pip3 2>/dev/null || echo "pip3 not found"
which pip 2>/dev/null || echo "pip not found"

# Try different Python executables
if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
    PIP="pip3"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
    PIP="pip"
else
    echo "ERROR: No Python executable found!"
    ls -la /usr/bin/python* || echo "No python binaries in /usr/bin"
    exit 1
fi

echo "Using: $PYTHON"
$PYTHON --version

echo "Installing dependencies..."
$PIP install --upgrade pip
$PIP install -r backend/requirements.txt

echo "Starting server on port ${PORT:-8000}..."
cd backend
$PYTHON -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

#!/bin/bash
cd backend
uvicorn main:app --host 0.0.0.0 --port $PORT

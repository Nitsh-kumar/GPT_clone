#!/bin/bash
echo "Starting FastAPI Backend..."
cd Backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
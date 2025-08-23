#!/bin/bash
echo "Stopping backend (uvicorn main:app)..."
pkill -f "uvicorn main:app"
echo "Stopping frontend (npm run dev)..."
pkill -f "npm run dev"
echo "Servers stopped."

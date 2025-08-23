#!/bin/bash

# Run script for Information Retrieval project
# Usage: bash run.sh

set -e

# Backend setup
BACKEND_DIR="backend"
DATA_DIR="data"
VENV_DIR=".venv"
REQUIREMENTS_FILE="$BACKEND_DIR/requirements.txt"

# Frontend setup
FRONTEND_DIR="frontend"
PACKAGE_JSON="$FRONTEND_DIR/package.json"

# 1. Backend: Create and activate virtual environment, install requirements
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing Python requirements..."
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS_FILE"
else
    echo "Warning: $REQUIREMENTS_FILE not found. Skipping Python requirements install."
fi

# 2. Frontend: Install node modules if not present
if [ -f "$PACKAGE_JSON" ]; then
    if [ ! -d "$FRONTEND_DIR/node_modules" ]; then

# 5. Start crawler scheduler
echo "Starting crawler scheduler..."
source "$VENV_DIR/bin/activate"
nohup python schedule_crawler.py > crawler_scheduler.log 2>&1 &
SCHEDULER_PID=$!
        echo "Installing Node.js dependencies..."
        cd "$FRONTEND_DIR"
        npm install
        cd -
echo "Crawler Scheduler PID: $SCHEDULER_PID (logs: crawler_scheduler.log)"
    fi
else
    echo "Warning: $PACKAGE_JSON not found. Skipping npm install."
fi

# 3. Start backend (FastAPI)
echo "Starting backend server..."
cd "$BACKEND_DIR"
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd -

# 4. Start frontend (Next.js)
echo "Starting frontend server..."
cd "$FRONTEND_DIR"
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd -


# 5. Show status
echo "Backend PID: $BACKEND_PID (logs: backend.log)"
echo "Frontend PID: $FRONTEND_PID (logs: frontend.log)"
echo "Servers are starting. Access frontend at http://localhost:3000 and backend at http://localhost:8000"

# 6. Create stop.sh script to kill servers
cat << 'EOF' > stop.sh
#!/bin/bash
echo "Stopping backend (uvicorn main:app)..."
pkill -f "uvicorn main:app"
echo "Stopping frontend (npm run dev)..."
pkill -f "npm run dev"
echo "Servers stopped."
EOF
chmod +x stop.sh

echo "To stop the servers, run: ./stop.sh"

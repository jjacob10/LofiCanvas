#!/usr/bin/env bash

# Kill anything currently squatting on ports 3000 and 8000
kill -9 $(lsof -t -i :8000) 2>/dev/null
kill -9 $(lsof -t -i :3000) 2>/dev/null

echo "Starting Python Vibe Engine on :8000..."
python3 analyzer.py &
PYTHON_PID=$!

echo "Starting Node.js Gateway on :3000..."
node server.js &
NODE_PID=$!

# Trap Ctrl+C (SIGINT) and exit signals to cleanly kill child processes
cleanup() {
    echo -e "\nShutting down servers and clearing ports..."
    kill -9 $PYTHON_PID $NODE_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

echo "Both servers running! Press Ctrl+C in this terminal to stop both cleanly."
wait
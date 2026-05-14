#!/bin/bash

echo "Stopping CC-TPR Router..."
echo ""

PID=$(lsof -ti:3456 2>/dev/null || true)
if [ -n "$PID" ]; then
    echo "Killing process $PID on port 3456..."
    kill -TERM "$PID" 2>/dev/null || true
    sleep 2
    # Force kill if still running
    if kill -0 "$PID" 2>/dev/null; then
        kill -9 "$PID" 2>/dev/null || true
    fi
    echo "Done."
else
    echo "No process found on port 3456."
fi
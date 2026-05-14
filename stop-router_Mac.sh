#!/bin/bash

echo "Stopping CC-TPR Router..."
echo ""

if pkill -f "src.main" 2>/dev/null; then
    echo "Router stopped."
else
    echo "No running router found."
fi

#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "  CC-TPR Router - Startup"
echo "========================================"
echo ""

check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "[ERROR] Python 3 not found."
        echo "Install Python 3.12+ from https://www.python.org/downloads/"
        exit 1
    fi

    PYVER=$(python3 --version 2>&1 | awk '{print $2}')
    MAJOR=$(echo "$PYVER" | cut -d. -f1)
    MINOR=$(echo "$PYVER" | cut -d. -f2)

    if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 12 ]; }; then
        echo "[ERROR] Python 3.12+ required. Found: $PYVER"
        exit 1
    fi
    echo "      Python $PYVER - OK"
}

check_venv() {
    echo "[2/4] Checking virtual environment..."
    if [ ! -d ".venv" ]; then
        echo "      .venv not found - creating..."
        python3 -m venv .venv
        echo "      Installing dependencies..."
        .venv/bin/pip install -q -e ".[dev]"
        echo "      .venv created - OK"
    else
        echo "      .venv found - OK"
    fi
}

check_config() {
    echo "[3/4] Checking config..."
    if [ ! -f "config.yaml" ]; then
        echo "      WARNING: config.yaml not found!"
    else
        echo "      config.yaml found - OK"
    fi
    if [ ! -f ".env" ]; then
        echo "      WARNING: .env not found - API keys may be missing"
    else
        echo "      .env found - OK"
    fi
}

start_router() {
    echo "[4/4] Starting CC-TPR Router..."
    echo "      Listening on http://127.0.0.1:3456"
    echo "      Press Ctrl+C to stop"
    echo ""
    echo "========================================"
    echo ""
    .venv/bin/python -m src.main
}

check_python
echo ""
check_venv
echo ""
check_config
echo ""
start_router
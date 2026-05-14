#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

CLAUDE_DIR="$HOME/.claude"

echo "========================================"
echo "  CC-TPR Router - Startup"
echo "========================================"
echo ""

# --- Step 1: Check Python ---
echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo ""
    echo "  Python 3 not found."
    echo "  Install Python 3.12+ from https://www.python.org/downloads/"
    echo "  Then re-run this script."
    exit 1
fi

PYVER=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo "$PYVER" | cut -d. -f1)
MINOR=$(echo "$PYVER" | cut -d. -f2)

if [ "$MAJOR" -lt 3 ] || { [ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 12 ]; }; then
    echo "      Python 3.12+ required. Found: $PYVER"
    exit 1
fi
echo "      Python $PYVER - OK"
echo ""

# --- Step 2: Check venv ---
echo "[2/5] Checking virtual environment..."
if [ ! -d ".venv" ]; then
    echo "      .venv not found - creating..."
    python3 -m venv .venv
    echo "      Installing dependencies..."
    .venv/bin/pip install -q -e ".[dev]"
    echo "      .venv created - OK"
else
    echo "      .venv found - OK"
fi
echo ""

# --- Step 3: Check config ---
echo "[3/5] Checking config..."
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
echo ""

# --- Step 4: Setup statusline ---
echo "[4/5] Setting up statusline..."
mkdir -p "$CLAUDE_DIR"

if [ ! -f "$CLAUDE_DIR/smart-router-status.py" ]; then
    cp statusline/smart-router-status.py "$CLAUDE_DIR/smart-router-status.py"
    echo "      Copied smart-router-status.py to $CLAUDE_DIR"
else
    echo "      smart-router-status.py already installed - OK"
fi

SETTINGS="$CLAUDE_DIR/settings.json"
NEED_REGISTER=0

if [ -f "$SETTINGS" ]; then
    if ! python3 -c "import json,sys;d=json.load(open(sys.argv[1]));sys.exit(0 if 'statusLine' in d else 1)" "$SETTINGS" 2>/dev/null; then
        NEED_REGISTER=1
    fi
else
    NEED_REGISTER=1
fi

if [ "$NEED_REGISTER" -eq 1 ]; then
    echo ""
    echo "      Statusline not registered in Claude Code."
    echo "      Register now? [Y/n]"
    read -t 10 -r ANSWER
    ANSWER="${ANSWER:-Y}"
    if [ "$ANSWER" = "Y" ] || [ "$ANSWER" = "y" ] || [ -z "$ANSWER" ]; then
        if [ -f "$SETTINGS" ]; then
            cp "$SETTINGS" "$SETTINGS.bak"
            python3 -c "
import json, sys
s = json.load(open(sys.argv[1]))
s.setdefault('statusLine', {}).update({'command': 'python3 \"$CLAUDE_DIR/smart-router-status.py\"'})
json.dump(s, open(sys.argv[1], 'w'), indent=2)
" "$SETTINGS"
        else
            echo "{\"statusLine\": {\"command\": \"python3 $CLAUDE_DIR/smart-router-status.py\"}}" > "$SETTINGS"
        fi
        echo "      Registered! Restart Claude Code to activate statusline."
    else
        echo "      Skipped. You can register manually later."
    fi
fi
echo ""

# --- Step 5: Start router ---
echo "[5/5] Starting CC-TPR Router..."
echo "      Listening on http://127.0.0.1:3456"
echo "      Press Ctrl+C to stop"
echo ""
echo "========================================"
echo ""
.venv/bin/python -m src.main

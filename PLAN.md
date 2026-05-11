# CC-TPR — Build & Run Guide

**Purpose:** This guide is fool-proof. Follow each step in order. No guessing required.

---

## ONE-TIME SETUP (First time on any PC)

### Step 1: Verify Python Version

Open CMD and run:
```
python --version
```

**Must show:** `Python 3.13+`

### Step 2: Navigate to Project Folder

```
cd C:\Users\lenovo\sandbox\CC-TPR
```

### Step 3: Create Virtual Environment

```
python -m venv .venv
```

### Step 4: Install Dependencies

```
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

This installs all dependencies including dev tools (pytest, pyright, etc.)

### Step 5: Configure API Keys

Copy `.env.example` to `.env`:
```
copy .env.example .env
```

Edit `.env` and fill in your API keys:
```
MINIMAX_API_KEY=your_minimax_key_here
ZAI_API_KEY=your_zai_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here
OPENROUTER_API_KEY=your_openrouter_key_here
```

### Step 6: Verify Installation

```
.venv\Scripts\python.exe -m pip list
```

You should see: flask, requests, tiktoken, pyyaml, pytest, pyright

---

## DAILY RUN (Every time you use it)

### Step 1: Start the Router

**Double-click `start-router.bat`**

A CMD window will open and show:
```
CC-TPR Router starting on http://127.0.0.1:3456
 * Running on http://127.0.0.1:3456
```

Keep this window open.

### Step 2: Start Claude Code

Claude Code will automatically route through the router at `http://127.0.0.1:3456`

### Step 3: Use Claude Code Normally

All routing happens automatically.

### Step 4: Stop the Router

**Press Ctrl+C** in the router CMD window, OR close the CMD window.

---

## DEVELOPMENT COMMANDS

### Run Router Directly (without batch file)
```
.venv\Scripts\python.exe -m src.main
```

### Run Tests
```
pytest
```

### Type Check
```
pyright
```

### Format Code
```
ruff format src tests
```

### Lint
```
ruff check src tests
```

### Build Package
```
python -m build
```

---

## CONFIGURATION

### config.yaml — Routing Rules

```yaml
routing:
  models:
    haiku: "zai"       # haiku → ZAI → GLM-4.7
    sonnet: "minimax"   # sonnet → MiniMax → M2.7
    opus: "zai"         # opus → ZAI → GLM-5.1
  context_threshold: 165000  # Smart switch trigger
  smart_switch:
    enabled: true
    target_models: ["sonnet", "opus"]  # These models trigger smart switch
    target_provider: "deepseek"         # Route to DeepSeek when threshold exceeded
```

### Change Provider for a Model

Edit `config.yaml`, change the provider name. Valid providers: `minimax`, `zai`, `deepseek`, `openrouter`

### Change Smart Switch Threshold

Edit `config.yaml`, change `context_threshold` value (in tokens)

---

## PROVIDERS & MODELS

| Provider | Base URL | Models | Context |
|----------|----------|--------|---------|
| MiniMax | `https://api.minimax.io/anthropic` | M2.7 | 200k |
| ZAI | `https://api.z.ai/api/anthropic` | GLM-4.7, GLM-5.1 | 200k |
| DeepSeek | `https://api.deepseek.com/anthropic` | V4 Pro | **1M** |
| OpenRouter | `https://openrouter.ai/api` | Various | varies |

---

## STATUS LINE (Claude Code Integration)

The router status line shows the actual routed model in Claude Code's status bar.

### Setup

In Claude Code, edit `~/.claude/settings.json` and add:
```json
{
  "statusLine": {
    "type": "command",
    "command": "python /c/Users/lenovo/sandbox/CC-TPR/.venv/Scripts/python.exe /c/Users/lenovo/sandbox/CC-TPR/src/status.py",
    "refreshInterval": 2
  }
}
```

### Status Line Path Note

On Windows, Claude Code runs status line commands through Git Bash. Use forward slashes:
- **CORRECT:** `/c/Users/lenovo/sandbox/CC-TPR/...`
- **WRONG:** `C:\Users\lenovo\sandbox\CC-TPR\...`

---

## TROUBLESHOOTING

### "python: command not found"
Run Python directly: `py` instead of `python`, or use full path to Python executable

### Router won't start on port 3456
Something else is using the port. Edit `config.yaml` to change `server.port`

### API errors (401, 403)
Check your API keys in `.env`. Make sure you copied from `.env.example` not `.env.example` itself

### Circuit breaker keeps opening
3 consecutive failures → circuit opens for 2 minutes. Check provider status, then wait for auto-reset or restart router

### Status line not showing
1. Make sure router is running
2. Restart Claude Code completely (close and reopen)
3. Check path uses forward slashes `/c/Users/...` not backslashes

---

## BUILD FROM SOURCE (Publishing to GitHub)

### One-Time Setup

```bash
# Install build tools
.venv\Scripts\python.exe -m pip install build twine

# Create .env from .env.example (DONT commit .env with real keys!)
copy .env.example .env
```

### Build Package

```bash
.venv\Scripts\python.exe -m build
```

This creates `dist/` folder with `.whl` and `.tar.gz`

### Tag & Release

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions will build and create a release automatically.

---

## FILE MANIFEST

```
CC-TPR/
├── .github/workflows/ci.yml       # GitHub Actions CI
├── pyproject.toml                # Package config
├── pyrightconfig.json           # Type checker config
├── ruff.toml                    # Linter config
├── config.yaml                  # Router configuration
├── .env.example                 # API keys template (copy to .env)
├── README.md                     # This file
├── PLAN.md                      # Build guide
├── LICENSE                      # MIT License
├── start-router.bat             # Launch router
├── stop-router.bat              # Stop router
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── main.py                  # Flask app
│   ├── router.py               # Routing logic
│   ├── failover.py              # Circuit breaker
│   ├── tokenizer.py             # Token counting
│   ├── status.py                # Status tracker
│   └── providers/
│       ├── __init__.py
│       ├── base.py
│       ├── minimax.py
│       ├── zai.py
│       ├── deepseek.py
│       └── openrouter.py
└── tests/
    ├── __init__.py
    ├── test_router.py
    ├── test_failover.py
    ├── test_tokenizer.py
    └── test_status.py
```

---

**Questions?** Open an issue at the GitHub repo.
# CC-TPR — Claude Code Token Plan Router

Stop burning through your Claude Pro context window. CC-TPR routes your Claude Code requests across MiniMax M2.7, ZAI GLM-4.7/5.1, and DeepSeek V4 Pro — giving you **3x the usable context** of Claude Pro for only ~$30/month.

## The Math

| Setup | Cost/mo | Context Window | Who it's for |
|-------|---------|---------------|-------------|
| **Claude Pro** | $20 | 200k tokens | Everyone |
| **CC-TPR** | ~$30 | 200k → **1M tokens** | Power users |

**CC-TPR costs $10 more but gives you 5x the context window.** When your project exceeds 200k tokens, CC-TPR automatically switches to DeepSeek V4 Pro with a **1,000,000 token context window** — no code changes, no interruptions.

---

## How It Works

```
You: "haiku/sonnet" → CC-TPR → MiniMax M2.7 ($10/mo, 200k context)
You: "opus"         → CC-TPR → ZAI GLM-5.1 ($18/mo, 200k context)
You: (>165k tokens) → CC-TPR → DeepSeek V4 Pro ($2/mo, 1M context!)
```

### Smart Switch
When any single request exceeds **165,000 tokens**, CC-TPR automatically routes that request to **DeepSeek V4 Pro** — the only model with a 1M token context window at ~$2/month. Your conversation continues seamlessly. Once triggered, it stays on DeepSeek for that session.

### Circuit Breaker
If a provider goes down, CC-TPR fails over to OpenRouter automatically — you don't lose your session.

### Status Line
Claude Code's status bar shows the **actual model you're using** (not just "claude-sonnet"), plus a context usage percentage bar so you know when you're about to hit the limit.

---

## What You Get

- **haiku → MiniMax M2.7** — fast, cheap light tasks
- **sonnet → MiniMax M2.7** — same model, covers most daily coding
- **opus → ZAI GLM-5.1** — complex reasoning on ZAI's GLM-5.1
- **>165k tokens → DeepSeek V4 Pro** — 1M context for large codebases, long sessions
- **Automatic failover** — circuit breaker prevents session loss when a provider is down
- **Claude Code status line** — see exactly which model is active and your context %
- **Config-driven** — change any routing rule in `config.yaml`, no code changes

---

## Subscription Setup (~$30/month)

### 1. MiniMax — $10/month
Sign up at [minimax.io](https://www.minimax.io), subscribe to M2.7 plan.
- API base: `https://api.minimax.io/anthropic`
- Model: `MiniMax-M2.7`
- Context: 200,000 tokens

### 2. ZAI — $18/month
Sign up at [z.ai](https://z.ai), subscribe to GLM plan.
- API base: `https://api.z.ai/api/anthropic`
- Models: `glm-4.7` (haiku/opus routing), `glm-5.1` (opus)
- Context: 200,000 tokens

### 3. DeepSeek V4 Pro — ~$2/month
Sign up at [deepseek.com](https://deepseek.com), add credit.
- API base: `https://api.deepseek.com/anthropic`
- Model: `deepseek-v4-pro`
- Context: **1,000,000 tokens**

DeepSeek is used **only when a single request exceeds 165k tokens**. At typical usage, cost is minimal — ~$2-5/month.

### 4. OpenRouter — pay-as-you-go (fallback only)
Sign up at [openrouter.ai](https://openrouter.ai) — only charged when a primary provider fails. Usually $0/month.

---

## Quick Start

### One-Time Setup

```bash
# Clone or navigate to CC-TPR
cd CC-TPR

# Create virtual environment
python -m venv .venv

# Install dependencies
.venv\Scripts\python.exe -m pip install -e ".[dev]"

# Create .env file
copy .env.example .env
```

Edit `.env` and fill in your API keys:
```
MINIMAX_API_KEY=your_minimax_key
ZAI_API_KEY=your_zai_key
DEEPSEEK_API_KEY=your_deepseek_key
OPENROUTER_API_KEY=your_openrouter_key
```

### Daily Use

**Double-click `start-router.bat`** — a CMD window opens with the router running.

Start Claude Code. All requests route automatically through CC-TPR.

Press Ctrl+C or close the CMD window to stop.

---

## Routing Table

| Claude Code Model | Provider | Actual Model | Context Window | Monthly Cost |
|-------------------|----------|--------------|---------------|--------------|
| haiku | MiniMax | M2.7 | 200k | $10 |
| sonnet | MiniMax | M2.7 | 200k | $10 |
| opus | ZAI | GLM-5.1 | 200k | $18 |
| sonnet/opus (>165k tokens) | DeepSeek | V4 Pro | **1M** | ~$2 |

**Note:** haiku and sonnet both route to the same MiniMax M2.7 model — both Claude Code tiers get equivalent power through CC-TPR. opus goes to ZAI GLM-5.1 for heavier workloads.

---

## Configuration

All routing is config-driven in `config.yaml`:

```yaml
routing:
  models:
    haiku: "minimax"    # haiku → MiniMax M2.7
    sonnet: "minimax"   # sonnet → MiniMax M2.7
    opus: "zai"          # opus → ZAI GLM-5.1
  context_threshold: 165000   # trigger DeepSeek switch at this token count
  smart_switch:
    enabled: true
    target_models: ["sonnet", "opus"]  # which models trigger the switch
    target_provider: "deepseek"        # route to DeepSeek V4 Pro
```

Change `context_threshold` to trigger the DeepSeek switch earlier or later.

---

## Project Structure

```
CC-TPR/
├── src/
│   ├── main.py              # Flask app — /v1/messages proxy, /health, /status
│   ├── router.py            # Routing logic + smart switch
│   ├── failover.py          # Circuit breaker (auto-resets after 2min cooldown)
│   ├── tokenizer.py         # cl100k_base token counting
│   ├── status.py            # StatusTracker singleton (thread-safe)
│   ├── providers/           # Provider implementations
│   │   ├── minimax.py       # MiniMax M2.7
│   │   ├── zai.py           # ZAI GLM-4.7 / GLM-5.1
│   │   ├── deepseek.py      # DeepSeek V4 Pro (1M context)
│   │   └── openrouter.py    # Fallback only
│   ├── converters/          # Format converters (kept for reference)
│   └── utils/
│       ├── config.py        # YAML config loader
│       └── logger.py        # Logging setup
├── tests/                   # 28 unit tests
├── config.yaml              # Routing configuration
├── .env.example             # API keys template
├── start-router.bat         # Double-click launcher
├── stop-router.bat         # Stop router
└── README.md
```

---

## For Developers

```bash
# Run tests
pytest

# Type check
pyright

# Lint
ruff check src tests

# Build package
python -m build
```

---

## Why This Beats Claude Pro Alone

1. **5x context window** — 200k vs 1M tokens. Work on entire codebases without hitting walls.
2. **Cheaper per-token** — MiniMax M2.7 and ZAI GLM models cost far less per token than Claude.
3. **No interruptions** — automatic failover means no lost sessions when a provider has issues.
4. **Transparent** — status line shows exactly what model is running and your context %.
5. **Config-driven** — retune routing without touching code.

---

## License

MIT
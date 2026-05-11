# CC-TPR

A smart router for Claude Code that routes requests to the best available model provider based on model type and context window usage.

**Routing Rules:**
- `haiku` → Minimax M2.7
- `sonnet` → Minimax M2.7 → DeepSeek V4 Pro (>165k context)
- `opus` → GLM5.1 → DeepSeek V4 Pro (>165k context)

**Fallback:** OpenRouter (same model routing as above)

Automatically switches `sonnet` or `opus` to DeepSeek V4 Pro (1M context) when context exceeds 165k tokens.

## Features

- **Smart routing**: Route haiku/sonnet/opus to different providers automatically
- **Context‑aware switching**: Automatically route to DeepSeek V4 Pro (1M context) when context exceeds 165k tokens
- **Fallback via OpenRouter**: Seamless failover using the same model routing rules
- **Circuit breaker**: Automatic failover when a provider experiences repeated failures
- **Claude Code status line**: Shows actual routed model and context usage bar
- **Flask-based**: Lightweight proxy server with SSE streaming support
- **Designed to work with**:
  - **Minimax Token Plan** (highly efficient)
  - **ZAI (GLM) Token Plan** (highly capable)
  - **Deepseek API** (for 1M context)
  - **Openrouter API** (for fallback)
- Works with all Anthropic‑compatible endpoints

> **⚠️ Important – Required Plans & Recommendations**
>
> To use this router, you will need **at least a Minimax Token Plan** (for haiku/sonnet) **and a ZAI (GLM) Token Plan** (for opus).  
> If you don't have them yet, sign up here:
> - **Minimax Coding Plan**: [https://platform.minimax.io/subscribe/token-plan?code=VaYpkbSg4M](https://platform.minimax.io/subscribe/token-plan?code=VaYpkbSg4M)
> - **GLM Coding Plan**: [https://z.ai/subscribe?ic=ER6MB4WO5C](https://z.ai/subscribe?ic=ER6MB4WO5C)
>
> For projects that go beyond the 165k token context window, we **recommend purchasing credits** for either:
> - **DeepSeek V4 Pro** (1M context, 0.435/m input tokens, 0.87/m output tokens)
> - **Mimo V2.5 Pro** (1M context, 1.00/m input tokens, 3.00/m output tokens)

## Requirements

- Python 3.13+
- Built on Windows

## Quick Start

1. **Double-click `start-router.bat`** — this opens a CMD window with the router running
2. **Start Claude Code** — it will automatically route through the router
3. **Close the CMD window** or press Ctrl+C to stop the router

## Configuration

Edit `config.yaml` to change:
- Which provider each model routes to
- The smart switch threshold (default: 165,000 tokens)
- Provider base URLs and timeouts

Edit `.env` (create from `.env.example`) to set your API keys:
```
MINIMAX_API_KEY=your_key_here
ZAI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

## For Development

```bash
# Create venv
python -m venv .venv

# Activate venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"

# Run tests
pytest

# Type check
pyright

# Run router directly
python -m src.main
```

## License

MIT
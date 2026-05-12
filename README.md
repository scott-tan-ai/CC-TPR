# CC-TPR — Claude Code Token Plan Router

A smart **Token Plan Router for Claude Code** that routes requests to the best available model provider based on model type and context window usage. Routes Haiku & Sonnet → MiniMax M2.7 & Opus → ZAI GLM-5.1, and automatically switches Sonnet & Opus to DeepSeek V4 Pro when context approaches 200k tokens.

### If you want 10x the usability of Claude Pro for just $10 more (total under $30), don't skip this repo.


#### Why I Use MiniMax M2.7 to replace Claude Sonnet

**Coding**  
**M2.7 scores 78% on SWE-bench Verified, versus Sonnet 4.6's 55%.** That is a big gap in actually shipping working fixes. **On SWE-Pro, M2.7 manages 56.22%, effectively matching Opus-level performance,** while Sonnet scores lower. On VIBE-Pro, which measures end-to-end project delivery rather than isolated patches, the two models are essentially tied (both around 55-56%).

**Agentic and Tool Use**  
M2.7 scores 46.3% on Toolathon, a strong result for native tool use, and reaches 62.7% on MM Claw, a multi-step agent benchmark. It has been **shown to run over 100 rounds of self-optimization on its own code, improving it by around 30%,** which is a capability Sonnet 4.6 was never explicitly designed to do.

**Honesty**  
**M2.7 has a lower hallucination rate than Sonnet 4.6 on complex reasoning prompts (34% vs 46%),** meaning it is less likely to invent confident-sounding falsehoods.

Note: The MiniMax Starter plan is a text and code plan. It does not include image, video, or speech generation beyond a short music trial. If you need those, you would need a higher tier. But purely as a text and code workhorse, the Starter plan ($10) gives you 1,500 requests per 5-hour rolling window for $10/month, which for my use case is plenty enough that I hardly hit any limit while going through 650 million tokens over 30 days.

If you do not have Minimax Coding Plan you may sign up via the referral code below, this helps us to keep the development of this router alive at $0 cost to you.
[https://platform.minimax.io/subscribe/token-plan?code=VaYpkbSg4M](https://platform.minimax.io/subscribe/token-plan?code=VaYpkbSg4M)

#### Why I Use Z.AI GLM-5.1 to replace Claude Opus

**Coding**  
GLM-5.1 currently **holds the top spot on SWE-Bench Pro (58.4%),** which is the hardest, most realistic coding benchmark available. **Opus 4.6 scores 57.3%.** On an overall coding evaluation, **GLM-5.1 reaches 94.6% of Opus 4.6's capability.** For almost all practical coding tasks, this difference is invisible.

**Tool Use and Autonomy**  
**GLM-5.1 scores 69.0 on Terminal-Bench 2.0, compared to Opus 4.6's 65.4.** It also ranks first on the CyberGym cybersecurity benchmark with 68.7%. **GLM-5.1 is documented to run autonomously for over 8 hours and 1,200+ steps in a closed planning, execution, and refinement loop.** It has demonstrated a 6.9x performance improvement through self-guided optimization on a real database workload.

**Real-world Reasoning**  
On broad knowledge tests like **MMLU, both models are in the same 90%+ tier.** On competition math **(AIME 2026), GLM-5.1 scores 95.3 to Opus's ~88%.** The only area where Opus holds a clear lead is graduate-level science (GPQA Diamond: 91.3 vs 86.2), which is rarely the bottleneck in everyday development work.

The Z.AI Lite plan gives you roughly 80 prompts every 5 hours and 400 prompts per week for $18/month. Which is roughly 3x of what you get with Claude Pro at $20/month.

If you do not have GLM Coding Plan you may sign up via the referral code below, this helps us to keep the development of this router alive at $0 cost to you.
[https://z.ai/subscribe?ic=ER6MB4WO5C](https://z.ai/subscribe?ic=ER6MB4WO5C)

### Cost Comparison and Flexibility

| Model | API Output Price (per 1M output tokens) |
|-------|----------------------------------|
| Claude Sonnet | ~$15.00 |
| MiniMax M2.7 | ~$1.20 |
| Claude Opus | ~$25.00 |
| Z.AI GLM-5.1 | ~$3.10 |

If you ever exceed your plan limits, you can always upgrade MiniMax Token Plan, GLM Token Plan or both to the next tier, increasing the limit of a specific model at minimal cost, or pay as you go. On the pay-as-you-go side, M2.7 is about 12.5x cheaper than Sonnet, and GLM-5.1 is about 5.7x cheaper than Opus.

### Bottom Line

For $20/month, Claude Pro gives you access to 3 models with strong safety and integrated features, but you are paying a premium where the raw coding benchmarks no longer justify the price gap. For $28/month, the MiniMax + Z.AI combo gives you a coding workhorse that beats Sonnet on several key metrics, plus an Opus-class planning and coding model that actually leads on the hardest engineering benchmark today. You also gain the flexibility to scale your subscriptions upward or tap API usage at dramatically lower rates.

If the context you are working with approaches the 200k limit of M2.7 and GLM-5.1, the router will automatically switch to Deepseek V4 Pro (via Deepseek API) for both sonnet and opus to keep the AI running. As the context seldom exceeds 200k, this feature should not kick in often and you are able to pay minimally as you go with Deepseek instead of relying on another monthly subscription.

### Features of CC-TPR

- Allows you to use Claude Code with multiple token plan providers.
- Smart Context-aware switching: Automatically route to DeepSeek V4 Pro (1M context) when context approaches 200k tokens
- Fallback via OpenRouter: Seamless failover using the same model routing rules
- Circuit breaker: Automatic failover when a provider experiences repeated failures
- **Claude Code status line: Shows actual routed model and context usage bar**
- Flask-based: Lightweight proxy server with SSE streaming support
- **Designed to work with:**
  - **Minimax Token Plan (highly efficient)**
  - **ZAI (GLM) Token Plan (highly capable)**
  - **Deepseek API (for 1M context)**
  - **Openrouter API (for fallback)**
- Works with all Anthropic-compatible endpoints

### Important – Required Plans & Recommendations

To use this router, we recommend using a Minimax Token Plan (for Haiku & Sonnet) and a ZAI GLM Token Plan (for Opus). 

If you do not have them you may sign up via the referral code below, this helps us to keep the development of this router alive at $0 cost to you.

- Minimax Coding Plan: [https://platform.minimax.io/subscribe/token-plan?code=VaYpkbSg4M](https://platform.minimax.io/subscribe/token-plan?code=VaYpkbSg4M)
- GLM Coding Plan: [https://z.ai/subscribe?ic=ER6MB4WO5C](https://z.ai/subscribe?ic=ER6MB4WO5C)

For projects that occasionally exceed the 200k token context window, we recommend purchasing credits for DeepSeek V4 Pro (1M context) on a pay-as-you-go basis.

### Requirements

- Python 3.13+
- Windows (batch launcher designed for Windows)

### Quick Start

1. Double-click ‘start-router.bat’ - this opens a CMD window with the router running
2. Start Claude Code - it will automatically route through the router

When you are done, close the CMD window or press Ctrl+C to stop the router

### Configuration

Edit config.yaml to change:
- Which provider each model routes to
- The smart routing threshold for Sonnet & Opus (default: 165,000 tokens)
- Provider base URLs and timeouts

Edit .env (create from .env.example) to set your API keys:
```
MINIMAX_API_KEY=your_key_here
ZAI_API_KEY=your_key_here
DEEPSEEK_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
```

### For Development

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

### License

MIT

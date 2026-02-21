# BalatroLLM Reference

Source: https://github.com/coder/balatrollm

BalatroLLM is the reference LLM bot that plays Balatro via the BalatroBot API. It produces run artifacts consumed by BalatroBench.

## Prerequisites

- BalatroBot running (`uvx balatrobot serve`)
- uv v0.9.21+
- LLM API key (OpenAI-compatible provider)
- LLM must support tool use / function calling

## Architecture

```
BalatroBot (game) <--> BalatroClient (JSON-RPC) <--> Bot (game loop) <--> LLMClient (OpenAI API)
                                                      |
                                                StrategyManager (Jinja2 templates)
                                                      |
                                                Collector (run data recording)
```

Key source files in `src/balatrollm/`:
- `bot.py` — Core game loop and decision orchestration
- `client.py` — Async JSON-RPC 2.0 client
- `llm.py` — Async OpenAI client (240s timeout, 3 retries, exponential backoff)
- `executor.py` — Parallel task execution with port pooling
- `strategy.py` — Jinja2 template manager
- `collector.py` — Run data collection and statistics
- `config.py` — Configuration management

## Game Loop

```python
while True:
    match current_state:
        case "SELECTING_HAND" | "SHOP" | "SMODS_BOOSTER_OPENED":
            response = await self._get_llm_response(gamestate)
            gamestate = await self._execute_tool_call(response)
        case "ROUND_EVAL":
            gamestate = await self._balatro.call("cash_out")  # always
        case "BLIND_SELECT":
            gamestate = await self._balatro.call("select")    # always (skip not used)
        case "GAME_OVER":
            break
```

**LLM decides in**: SELECTING_HAND, SHOP, SMODS_BOOSTER_OPENED
**Automated**: ROUND_EVAL (always cash out), BLIND_SELECT (always select)

## Decision Pipeline

For each LLM decision point:

1. **Render prompt** from three Jinja2 templates:
   - `STRATEGY.md.jinja` — ~730 lines of strategic guidance (rules, scoring, hand types, joker effects, economy)
   - `GAMESTATE.md.jinja` — Dynamic current state rendering
   - `MEMORY.md.jinja` — Last 10 actions with reasoning + error context

2. **Send to LLM** as single user message with three content blocks (strategy gets cache_control)

3. **Tools provided** per game state (OpenAI function calling format, each requires `reasoning` param)

4. **Execute first tool call** via BalatroBot JSON-RPC

5. **Error handling**:
   - No valid tool call = "error call", retry up to 3 consecutive
   - Valid call but API rejection = "failed call", retry up to 3 consecutive
   - 3 consecutive errors/failures = abort run

## Strategy System

Strategies live in `src/balatrollm/strategies/{name}/`:

```
manifest.json         # Metadata: name, description, author, version, tags
STRATEGY.md.jinja     # Core strategic guidance
GAMESTATE.md.jinja    # Game state renderer
MEMORY.md.jinja       # Action history and error tracking
TOOLS.json            # Tool definitions per game state
```

Built-in strategies: `default`, `aggressive`, `conservative`

## Tools Per State

### SELECTING_HAND (5 tools)
- `play(cards: int[], reasoning: str)` — Play 1-5 cards
- `discard(cards: int[], reasoning: str)` — Discard to draw new
- `rearrange(hand|jokers|consumables: int[], reasoning: str)` — Reorder
- `sell(joker|consumable: int, reasoning: str)` — Sell for money
- `use(consumable: int, cards?: int[], reasoning: str)` — Use consumable

### SHOP (6 tools)
- `buy(card|voucher|pack: int, reasoning: str)` — Buy from shop
- `reroll(reasoning: str)` — Reroll items
- `next_round(reasoning: str)` — Leave shop
- `sell(joker|consumable: int, reasoning: str)` — Sell
- `use(consumable: int, cards?: int[], reasoning: str)` — Use consumable
- `rearrange(jokers|consumables: int[], reasoning: str)` — Reorder

### BLIND_SELECT (2 tools)
- `select(reasoning: str)` — Play the blind
- `skip(reasoning: str)` — Skip for tag reward

### SMODS_BOOSTER_OPENED (1 tool)
- `pack(card?: int, targets?: int[], skip?: bool, reasoning: str)` — Pick or skip

## CLI Configuration

```bash
balatrollm [CONFIG_YAML] [OPTIONS]
```

| Flag | Env Var | Default |
|---|---|---|
| `--model` | `BALATROLLM_MODEL` | required |
| `--seed` | `BALATROLLM_SEED` | `AAAAAAA` |
| `--deck` | `BALATROLLM_DECK` | `RED` |
| `--stake` | `BALATROLLM_STAKE` | `WHITE` |
| `--strategy` | `BALATROLLM_STRATEGY` | `default` |
| `--parallel` | `BALATROLLM_PARALLEL` | `1` |
| `--base-url` | `BALATROLLM_BASE_URL` | `https://openrouter.ai/api/v1` |
| `--api-key` | `BALATROLLM_API_KEY` | None |

All list params accept multiple values — cartesian product of all combos generates tasks.

### YAML Config Example

```yaml
model: anthropic/claude-sonnet-4
seed: AAAAAAA
deck: RED
stake: WHITE
strategy: default
model_config:
  temperature: 0.7
  max_tokens: 4096
```

## BalatroBench Scoring

Primary metric: **average final round reached**

Also tracked:
- Tool call reliability (valid %, invalid %, failed %)
- Token efficiency (input/output per tool call)
- Speed (seconds per tool call)
- Cost (milli-dollars per tool call)

### Finish Reasons

| Reason | Description |
|---|---|
| `won` | Game won |
| `lost` | Game over |
| `llm_abort` | LLM timeout/client error |
| `connection_abort` | Connection error |
| `consecutive_error_calls` | 3 consecutive invalid LLM responses |
| `consecutive_failed_calls` | 3 consecutive failed tool calls |
| `unexpected_error` | Unexpected exception |

## Minimal Bot Example

From BalatroBot docs — simplest possible bot (no LLM):

```python
import requests

URL = "http://127.0.0.1:12346"

def rpc(method, params={}):
    resp = requests.post(URL, json={
        "jsonrpc": "2.0", "method": method, "params": params, "id": 1,
    })
    data = resp.json()
    if "error" in data:
        raise Exception(data["error"]["message"])
    return data["result"]

def play_game():
    rpc("menu")
    state = rpc("start", {"deck": "RED", "stake": "WHITE"})
    while state["state"] != "GAME_OVER":
        match state["state"]:
            case "BLIND_SELECT":
                state = rpc("select")
            case "SELECTING_HAND":
                n = min(5, len(state["hand"]["cards"]))
                state = rpc("play", {"cards": list(range(n))})
            case "ROUND_EVAL":
                state = rpc("cash_out")
            case "SHOP":
                state = rpc("next_round")
            case _:
                state = rpc("gamestate")
    return state["won"]
```

# multbot

> **Status: Work in Progress**

An LLM-powered bot that plays [Balatro](https://www.playbalatro.com/) via the [BalatroBot](https://github.com/coder/balatrobot) JSON-RPC API.

## How it works

multbot connects to a running Balatro instance (with the BalatroBot mod) and uses an LLM to make gameplay decisions: selecting hands, discarding, buying from the shop, and opening booster packs.

- Game state is encoded into compact text representations for the LLM
- Tool definitions are generated per game state (hand selection, shop, boosters)
- The bot runs an async game loop, polling for state changes and dispatching LLM calls

## Prerequisites

- [Balatro](https://store.steampowered.com/app/2379780/Balatro/) v1.0.1+
- [BalatroBot](https://github.com/coder/balatrobot) mod installed
- An OpenAI-compatible LLM server (e.g. llama.cpp, vLLM, OpenAI API)
- Python 3.12+ with [uv](https://github.com/astral-sh/uv)

## Setup

```bash
# Install dependencies
uv sync

# Terminal 1: Start BalatroBot
uvx balatrobot serve

# Terminal 2: Start your LLM server

# Terminal 3: Run the bot
uv run multbot --verbose
```

## Project structure

```
src/multbot/
  bot.py        # Async game loop, LLM integration
  client.py     # BalatroBot JSON-RPC client
  collector.py  # BalatroBench-compatible run data collector
  prompt.py     # System prompt generation
  state.py      # Game state encoding
  tools.py      # Tool definitions per game state
```

## Testing

```bash
uv run pytest -v
```

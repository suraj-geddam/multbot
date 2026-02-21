# multbot

An LLM-powered bot that plays Balatro via the BalatroBot JSON-RPC API, benchmarked on BalatroBench.

## Reference Docs

- `docs/balatrobot-api.md` — Full BalatroBot API (methods, game states, schemas, enums)
- `docs/balatrollm-reference.md` — Reference bot architecture, strategy system, BalatroBench scoring

## Key External Repos

- [BalatroBot](https://github.com/coder/balatrobot) — Game mod exposing JSON-RPC 2.0 API on `localhost:12346`
- [BalatroLLM](https://github.com/coder/balatrollm) — Reference LLM bot (Python/Jinja2)
- [BalatroBench](https://github.com/coder/balatrobench) — Benchmark leaderboard

## Quick Context

- Bot connects to BalatroBot via HTTP POST (JSON-RPC 2.0)
- Game state machine: MENU → BLIND_SELECT → SELECTING_HAND → ROUND_EVAL → SHOP → loop
- LLM decides in: SELECTING_HAND, SHOP, SMODS_BOOSTER_OPENED
- Card/joker/consumable references use 0-based indices into gamestate arrays
- BalatroBench scores by: average final round, tool call reliability, token efficiency, cost

## Stack

- Python (uv for env management)
- Balatro v1.0.1+ with BalatroBot mod

## Conventions

- TBD (will be filled in after architecture planning)

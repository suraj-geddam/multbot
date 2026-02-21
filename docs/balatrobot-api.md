# BalatroBot API Reference

Source: https://github.com/coder/balatrobot

BalatroBot is a Lua mod for Balatro that exposes a JSON-RPC 2.0 HTTP API on `http://127.0.0.1:12346`.

## Prerequisites

| Dependency | Version | Purpose |
|---|---|---|
| Balatro | v1.0.1+ | The game (Steam) |
| Lovely Injector | v0.8.0+ | Lua mod injector |
| Steamodded | v1.0.0-beta-1221a+ | Mod loader framework |
| uv | v0.9.21+ | Python package manager |

## Running

```bash
uvx balatrobot serve
```

Verify:
```bash
curl -X POST http://127.0.0.1:12346 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"health","id":1}'
```

### Serve Options

| Option | Env Var | Default | Description |
|---|---|---|---|
| `--host` | `BALATROBOT_HOST` | `127.0.0.1` | Listen address |
| `--port` | `BALATROBOT_PORT` | `12346` | Listen port |
| `--fast` | `BALATROBOT_FAST` | `false` | Fast mode |
| `--headless` | `BALATROBOT_HEADLESS` | `false` | No window |
| `--gamespeed` | `BALATROBOT_GAMESPEED` | `4` | Speed multiplier |
| `--fps-cap` | `BALATROBOT_FPS_CAP` | `60` | FPS cap |
| `--audio` | `BALATROBOT_AUDIO` | `false` | Enable audio |
| `--debug` | `BALATROBOT_DEBUG` | `false` | Debug mode |

## Protocol

**Transport**: HTTP POST to `http://127.0.0.1:12346`

Request:
```json
{"jsonrpc": "2.0", "method": "method_name", "params": {...}, "id": 1}
```

Success response:
```json
{"jsonrpc": "2.0", "result": {...}, "id": 1}
```

Error response:
```json
{"jsonrpc": "2.0", "error": {"code": -32001, "message": "...", "data": {"name": "..."}}, "id": 1}
```

### Error Codes

| Code | Name | Description |
|---|---|---|
| `-32000` | `INTERNAL_ERROR` | Server-side failure |
| `-32001` | `BAD_REQUEST` | Invalid parameters |
| `-32002` | `INVALID_STATE` | Action not allowed in current state |
| `-32003` | `NOT_ALLOWED` | Game rules prevent action |

## Game States

```
MENU -> BLIND_SELECT -> SELECTING_HAND -> ROUND_EVAL -> SHOP -> BLIND_SELECT -> ...
                                                                     |
                                                              SMODS_BOOSTER_OPENED
                                                                     |
                                                              (back to SHOP)

When game ends: GAME_OVER
```

| State | Description |
|---|---|
| `MENU` | Main menu |
| `BLIND_SELECT` | Choose blind to play or skip |
| `SELECTING_HAND` | Select cards to play or discard |
| `ROUND_EVAL` | Round complete, ready to cash out |
| `SHOP` | Shopping phase |
| `SMODS_BOOSTER_OPENED` | Booster pack opened (sub-state of SHOP) |
| `GAME_OVER` | Game ended (check `won` field) |

## API Methods

### System

| Method | State | Description |
|---|---|---|
| `health` | Any | Returns `{"status": "ok"}` |
| `gamestate` | Any | Returns full GameState |
| `rpc.discover` | Any | Returns OpenRPC spec |

### Game Flow

**`start`** — Start new run
- State: `MENU`
- Params: `deck` (str, required), `stake` (str, required), `seed` (str, optional)

**`menu`** — Return to main menu
- State: Any

**`select`** — Select current blind
- State: `BLIND_SELECT`

**`skip`** — Skip blind (Small/Big only, not Boss)
- State: `BLIND_SELECT`

**`play`** — Play cards as poker hand
- State: `SELECTING_HAND`
- Params: `cards` (int[], 1-5 card indices, 0-based)

**`discard`** — Discard cards to draw new
- State: `SELECTING_HAND`
- Params: `cards` (int[])

**`cash_out`** — Collect round rewards
- State: `ROUND_EVAL`

**`next_round`** — Leave shop
- State: `SHOP`

### Shop

**`buy`** — Buy from shop
- State: `SHOP`
- Params: exactly one of `card` (int), `voucher` (int), `pack` (int)

**`sell`** — Sell joker or consumable
- State: `SHOP` or `SELECTING_HAND`
- Params: exactly one of `joker` (int), `consumable` (int)

**`reroll`** — Reroll shop items (costs money)
- State: `SHOP`

**`pack`** — Select from opened booster or skip
- State: `SMODS_BOOSTER_OPENED`
- Params: exactly one of `card` (int), `targets` (int[]), `skip` (bool)

### Card Management

**`use`** — Use consumable (Tarot, Planet, Spectral)
- State: `SELECTING_HAND` or `SHOP`
- Params: `consumable` (int), `cards` (int[], optional targets)

**`rearrange`** — Reorder cards
- State: `SELECTING_HAND`, `SHOP`, `SMODS_BOOSTER_OPENED`
- Params: exactly one of `hand` (int[]), `jokers` (int[]), `consumables` (int[])

### Debug/Testing

**`add`** — Add card: params `key`, optional `seal`, `edition`, `enhancement`, `eternal`, `perishable`, `rental`

**`set`** — Set values: params any of `money`, `chips`, `ante`, `round`, `hands`, `discards`, `shop` (bool)

**`save`** / **`load`** — Save/load state: params `path` (str)

**`screenshot`** — Take screenshot: params `path` (str)

## GameState Schema

```
GameState {
  state: string          // Current game state
  round_num: int
  ante_num: int          // Current ante (1-8)
  money: int
  deck: string           // RED, BLUE, etc.
  stake: string          // WHITE, RED, etc.
  seed: string
  won: boolean
  used_vouchers: dict    // name -> effect description

  hands: dict            // hand type name -> Hand info
  round: Round
  blinds: Blinds

  jokers: Area           // Joker slots
  consumables: Area
  cards: Area            // Deck cards
  hand: Area             // Current hand

  shop: Area
  vouchers: Area
  packs: Area
  pack: Area             // Opened pack contents
}
```

### Area
```
Area {
  count: int
  limit: int
  highlighted_limit: int
  cards: Card[]
}
```

### Card
```
Card {
  id: int
  key: string            // e.g. "H_A", "j_joker", "c_fool"
  set: string            // DEFAULT, ENHANCED, JOKER, TAROT, PLANET, SPECTRAL, VOUCHER, BOOSTER
  label: string          // Display name
  value: {
    suit: string         // H, D, C, S
    rank: string         // 2-9, T, J, Q, K, A
    effect: string       // For jokers/consumables
  }
  modifier: {
    seal: string|null    // RED, BLUE, GOLD, PURPLE
    edition: string|null // FOIL, HOLO, POLYCHROME, NEGATIVE
    enhancement: string|null // BONUS, MULT, WILD, GLASS, STEEL, STONE, GOLD, LUCKY
    eternal: boolean
    perishable: int|null
    rental: boolean
  }
  state: {
    debuff: boolean
    hidden: boolean
    highlight: boolean
  }
  cost: {
    sell: int
    buy: int
  }
}
```

### Round
```
Round {
  hands_left: int
  hands_played: int
  discards_left: int
  discards_used: int
  reroll_cost: int
  chips: int             // Score this round
}
```

### Blind
```
Blind {
  type: string           // SMALL, BIG, BOSS
  status: string         // SELECT, CURRENT, UPCOMING, DEFEATED, SKIPPED
  name: string
  effect: string
  score: int             // Required score
  tag_name: string
  tag_effect: string
}
```

### Hand (poker hand info)
```
Hand {
  order: int
  level: int
  chips: int             // Base chips
  mult: int              // Base mult
  played: int
  played_this_round: int
  example: array
}
```

## Enums

**Decks**: RED, BLUE, YELLOW, GREEN, BLACK, MAGIC, NEBULA, GHOST, ABANDONED, CHECKERED, ZODIAC, PAINTED, ANAGLYPH, PLASMA, ERRATIC

**Stakes**: WHITE, RED, GREEN, BLACK, BLUE, PURPLE, ORANGE, GOLD

**Suits**: H (Hearts), D (Diamonds), C (Clubs), S (Spades)

**Ranks**: 2-9, T (Ten), J, Q, K, A

**Card key format**: `{Suit}_{Rank}` — e.g. `H_A` = Ace of Hearts, `S_T` = Ten of Spades

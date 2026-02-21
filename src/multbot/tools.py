from __future__ import annotations


def _tool(name: str, description: str, properties: dict, required: list[str]) -> dict:
    """Helper to build an OpenAI function tool definition."""
    properties["reasoning"] = {
        "type": "string",
        "description": "Your strategic reasoning for this action.",
    }
    required = [*required, "reasoning"]
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


_CARDS_PARAM = {
    "type": "array",
    "items": {"type": "integer"},
    "description": "Card indices (0-based).",
}

SELECTING_HAND_TOOLS = [
    _tool("play", "Play 1-5 cards from your hand as a poker hand.", {
        "cards": {**_CARDS_PARAM, "description": "Card indices to play (1-5 cards)."},
    }, ["cards"]),
    _tool("discard", "Discard cards to draw new ones. Costs one discard.", {
        "cards": {**_CARDS_PARAM, "description": "Card indices to discard."},
    }, ["cards"]),
    _tool("sell", "Sell a joker or consumable for money.", {
        "joker": {"type": "integer", "description": "Joker index to sell."},
        "consumable": {"type": "integer", "description": "Consumable index to sell."},
    }, []),
    _tool("use", "Use a consumable card (Tarot, Planet, Spectral).", {
        "consumable": {"type": "integer", "description": "Consumable index to use."},
        "cards": {**_CARDS_PARAM, "description": "Target card indices (if needed)."},
    }, ["consumable"]),
    _tool("rearrange", "Reorder cards in hand, jokers, or consumables. Left-to-right order matters for jokers.", {
        "hand": {**_CARDS_PARAM, "description": "New hand order (all indices)."},
        "jokers": {**_CARDS_PARAM, "description": "New joker order (all indices)."},
        "consumables": {**_CARDS_PARAM, "description": "New consumable order (all indices)."},
    }, []),
]

SHOP_TOOLS = [
    _tool("buy", "Buy a card, voucher, or booster pack from the shop.", {
        "card": {"type": "integer", "description": "Shop card index to buy."},
        "voucher": {"type": "integer", "description": "Voucher index to buy."},
        "pack": {"type": "integer", "description": "Booster pack index to buy."},
    }, []),
    _tool("reroll", "Reroll shop items. Costs money (see reroll cost).", {}, []),
    _tool("next_round", "Leave the shop and advance to the next blind.", {}, []),
    _tool("sell", "Sell a joker or consumable for money.", {
        "joker": {"type": "integer", "description": "Joker index to sell."},
        "consumable": {"type": "integer", "description": "Consumable index to sell."},
    }, []),
    _tool("use", "Use a consumable card (Tarot, Planet, Spectral).", {
        "consumable": {"type": "integer", "description": "Consumable index to use."},
        "cards": {**_CARDS_PARAM, "description": "Target card indices (if needed)."},
    }, ["consumable"]),
    _tool("rearrange", "Reorder jokers or consumables. Left-to-right order matters for jokers.", {
        "jokers": {**_CARDS_PARAM, "description": "New joker order (all indices)."},
        "consumables": {**_CARDS_PARAM, "description": "New consumable order (all indices)."},
    }, []),
]

BOOSTER_TOOLS = [
    _tool("pack", "Select a card from the opened booster pack, or skip.", {
        "card": {"type": "integer", "description": "Card index to pick from pack."},
        "targets": {**_CARDS_PARAM, "description": "Target card indices (for tarots)."},
        "skip": {"type": "boolean", "description": "Set true to skip this pack."},
    }, []),
]


def get_tools(state: str) -> list[dict]:
    """Return OpenAI tool definitions for the given game state."""
    match state:
        case "SELECTING_HAND":
            return SELECTING_HAND_TOOLS
        case "SHOP":
            return SHOP_TOOLS
        case "SMODS_BOOSTER_OPENED":
            return BOOSTER_TOOLS
        case _:
            return []

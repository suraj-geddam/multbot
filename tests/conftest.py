"""Shared pytest fixtures with realistic BalatroBot game states."""

from __future__ import annotations

import pytest


def _make_card(
    *,
    id: int,
    key: str,
    set: str = "DEFAULT",
    label: str,
    suit: str = "",
    rank: str = "",
    effect: str = "",
    seal: str | None = None,
    edition: str | None = None,
    enhancement: str | None = None,
    eternal: bool = False,
    perishable: int | None = None,
    rental: bool = False,
    debuff: bool = False,
    hidden: bool = False,
    highlight: bool = False,
    sell: int = 0,
    buy: int = 0,
) -> dict:
    """Build a full Card dict matching the BalatroBot API schema."""
    return {
        "id": id,
        "key": key,
        "set": set,
        "label": label,
        "value": {
            "suit": suit,
            "rank": rank,
            "effect": effect,
        },
        "modifier": {
            "seal": seal,
            "edition": edition,
            "enhancement": enhancement,
            "eternal": eternal,
            "perishable": perishable,
            "rental": rental,
        },
        "state": {
            "debuff": debuff,
            "hidden": hidden,
            "highlight": highlight,
        },
        "cost": {
            "sell": sell,
            "buy": buy,
        },
    }


def _make_hand(
    *,
    order: int,
    level: int = 1,
    chips: int,
    mult: int,
    played: int = 0,
    played_this_round: int = 0,
    example: list | None = None,
) -> dict:
    return {
        "order": order,
        "level": level,
        "chips": chips,
        "mult": mult,
        "played": played,
        "played_this_round": played_this_round,
        "example": example or [],
    }


@pytest.fixture()
def selecting_hand_state() -> dict:
    """A SELECTING_HAND state: ante 2, round 4, 8 hand cards, jokers, consumables."""
    return {
        "state": "SELECTING_HAND",
        "round_num": 4,
        "ante_num": 2,
        "money": 12,
        "deck": "RED",
        "stake": "WHITE",
        "seed": "ABC123",
        "won": False,
        "used_vouchers": {},
        "hands": {
            "High Card": _make_hand(order=1, chips=5, mult=1),
            "Pair": _make_hand(order=2, level=2, chips=20, mult=2, played=5),
            "Two Pair": _make_hand(order=3, chips=20, mult=2),
            "Three of a Kind": _make_hand(order=4, chips=30, mult=3),
            "Straight": _make_hand(order=5, chips=30, mult=4),
            "Flush": _make_hand(order=6, chips=35, mult=4),
            "Full House": _make_hand(order=7, chips=40, mult=4),
            "Four of a Kind": _make_hand(order=8, chips=60, mult=7),
            "Straight Flush": _make_hand(order=9, chips=100, mult=8),
            "Royal Flush": _make_hand(order=10, chips=100, mult=8),
        },
        "round": {
            "hands_left": 3,
            "hands_played": 1,
            "discards_left": 2,
            "discards_used": 1,
            "reroll_cost": 5,
            "chips": 0,
        },
        "blinds": {
            "small": {
                "type": "SMALL",
                "status": "DEFEATED",
                "name": "Small Blind",
                "effect": "",
                "score": 200,
                "tag_name": "",
                "tag_effect": "",
            },
            "big": {
                "type": "BIG",
                "status": "CURRENT",
                "name": "Big Blind",
                "effect": "",
                "score": 450,
                "tag_name": "",
                "tag_effect": "",
            },
            "boss": {
                "type": "BOSS",
                "status": "UPCOMING",
                "name": "The Hook",
                "effect": "Discards 2 random cards per hand played",
                "score": 900,
                "tag_name": "",
                "tag_effect": "",
            },
        },
        "jokers": {
            "count": 3,
            "limit": 5,
            "highlighted_limit": 0,
            "cards": [
                _make_card(
                    id=100,
                    key="j_joker",
                    set="JOKER",
                    label="Joker",
                    effect="+4 Mult",
                    sell=1,
                ),
                _make_card(
                    id=101,
                    key="j_greedy_joker",
                    set="JOKER",
                    label="Greedy Joker",
                    effect="Played cards with Diamond suit give +3 Mult when scored",
                    sell=2,
                ),
                _make_card(
                    id=102,
                    key="j_ice_cream",
                    set="JOKER",
                    label="Ice Cream",
                    effect="+100 Chips, -5 Chips for every hand played",
                    sell=3,
                ),
            ],
        },
        "consumables": {
            "count": 1,
            "limit": 2,
            "highlighted_limit": 0,
            "cards": [
                _make_card(
                    id=200,
                    key="c_fool",
                    set="TAROT",
                    label="The Fool",
                    effect="Creates a copy of the last Tarot or Planet card used",
                    sell=1,
                ),
            ],
        },
        "cards": {
            "count": 44,
            "limit": 52,
            "highlighted_limit": 0,
            "cards": [],
        },
        "hand": {
            "count": 8,
            "limit": 8,
            "highlighted_limit": 5,
            "cards": [
                _make_card(id=1, key="H_A", label="Ace of Hearts", suit="H", rank="A"),
                _make_card(
                    id=2, key="S_K", label="King of Spades", suit="S", rank="K",
                    seal="GOLD",
                ),
                _make_card(id=3, key="D_T", label="10 of Diamonds", suit="D", rank="T"),
                _make_card(id=4, key="C_7", label="7 of Clubs", suit="C", rank="7"),
                _make_card(id=5, key="H_Q", label="Queen of Hearts", suit="H", rank="Q"),
                _make_card(id=6, key="S_3", label="3 of Spades", suit="S", rank="3"),
                _make_card(
                    id=7, key="D_J", label="Jack of Diamonds", suit="D", rank="J",
                    edition="FOIL",
                ),
                _make_card(id=8, key="C_9", label="9 of Clubs", suit="C", rank="9"),
            ],
        },
        "shop": {"count": 0, "limit": 2, "highlighted_limit": 0, "cards": []},
        "vouchers": {"count": 0, "limit": 0, "highlighted_limit": 0, "cards": []},
        "packs": {"count": 0, "limit": 2, "highlighted_limit": 0, "cards": []},
        "pack": {"count": 0, "limit": 0, "highlighted_limit": 0, "cards": []},
    }


@pytest.fixture()
def shop_state() -> dict:
    """A SHOP state with shop items, vouchers, packs, and reroll cost."""
    return {
        "state": "SHOP",
        "round_num": 3,
        "ante_num": 2,
        "money": 18,
        "deck": "RED",
        "stake": "WHITE",
        "seed": "ABC123",
        "won": False,
        "used_vouchers": {},
        "hands": {
            "High Card": _make_hand(order=1, chips=5, mult=1),
            "Pair": _make_hand(order=2, chips=10, mult=2, played=3),
        },
        "round": {
            "hands_left": 0,
            "hands_played": 4,
            "discards_left": 0,
            "discards_used": 3,
            "reroll_cost": 5,
            "chips": 500,
        },
        "blinds": {
            "small": {
                "type": "SMALL",
                "status": "DEFEATED",
                "name": "Small Blind",
                "effect": "",
                "score": 200,
                "tag_name": "",
                "tag_effect": "",
            },
            "big": {
                "type": "BIG",
                "status": "DEFEATED",
                "name": "Big Blind",
                "effect": "",
                "score": 450,
                "tag_name": "",
                "tag_effect": "",
            },
            "boss": {
                "type": "BOSS",
                "status": "UPCOMING",
                "name": "The Hook",
                "effect": "Discards 2 random cards per hand played",
                "score": 900,
                "tag_name": "",
                "tag_effect": "",
            },
        },
        "jokers": {
            "count": 2,
            "limit": 5,
            "highlighted_limit": 0,
            "cards": [
                _make_card(
                    id=100,
                    key="j_joker",
                    set="JOKER",
                    label="Joker",
                    effect="+4 Mult",
                    sell=1,
                ),
                _make_card(
                    id=101,
                    key="j_greedy_joker",
                    set="JOKER",
                    label="Greedy Joker",
                    effect="Played cards with Diamond suit give +3 Mult when scored",
                    sell=2,
                ),
            ],
        },
        "consumables": {
            "count": 0,
            "limit": 2,
            "highlighted_limit": 0,
            "cards": [],
        },
        "cards": {
            "count": 44,
            "limit": 52,
            "highlighted_limit": 0,
            "cards": [],
        },
        "hand": {"count": 0, "limit": 8, "highlighted_limit": 5, "cards": []},
        "shop": {
            "count": 2,
            "limit": 2,
            "highlighted_limit": 0,
            "cards": [
                _make_card(
                    id=300,
                    key="j_hack",
                    set="JOKER",
                    label="Hack",
                    effect="Retrigger each played 2, 3, 4, or 5",
                    buy=5,
                    sell=3,
                ),
                _make_card(
                    id=301,
                    key="c_hermit",
                    set="TAROT",
                    label="The Hermit",
                    effect="Doubles money (max $20)",
                    buy=3,
                    sell=1,
                ),
            ],
        },
        "vouchers": {
            "count": 1,
            "limit": 1,
            "highlighted_limit": 0,
            "cards": [
                _make_card(
                    id=400,
                    key="v_overstock",
                    set="VOUCHER",
                    label="Overstock",
                    effect="+1 card slot in shop",
                    buy=10,
                    sell=0,
                ),
            ],
        },
        "packs": {
            "count": 2,
            "limit": 2,
            "highlighted_limit": 0,
            "cards": [
                _make_card(
                    id=500,
                    key="p_arcana_normal_1",
                    set="BOOSTER",
                    label="Arcana Pack",
                    buy=4,
                    sell=0,
                ),
                _make_card(
                    id=501,
                    key="p_standard_normal_1",
                    set="BOOSTER",
                    label="Standard Pack",
                    buy=4,
                    sell=0,
                ),
            ],
        },
        "pack": {"count": 0, "limit": 0, "highlighted_limit": 0, "cards": []},
    }


@pytest.fixture()
def booster_state() -> dict:
    """A SMODS_BOOSTER_OPENED state with pack contents to choose from."""
    return {
        "state": "SMODS_BOOSTER_OPENED",
        "round_num": 3,
        "ante_num": 2,
        "money": 14,
        "deck": "RED",
        "stake": "WHITE",
        "seed": "ABC123",
        "won": False,
        "used_vouchers": {},
        "hands": {
            "High Card": _make_hand(order=1, chips=5, mult=1),
            "Pair": _make_hand(order=2, chips=10, mult=2),
        },
        "round": {
            "hands_left": 0,
            "hands_played": 4,
            "discards_left": 0,
            "discards_used": 3,
            "reroll_cost": 5,
            "chips": 0,
        },
        "blinds": {
            "small": {
                "type": "SMALL",
                "status": "DEFEATED",
                "name": "Small Blind",
                "effect": "",
                "score": 200,
                "tag_name": "",
                "tag_effect": "",
            },
            "big": {
                "type": "BIG",
                "status": "DEFEATED",
                "name": "Big Blind",
                "effect": "",
                "score": 450,
                "tag_name": "",
                "tag_effect": "",
            },
            "boss": {
                "type": "BOSS",
                "status": "UPCOMING",
                "name": "The Hook",
                "effect": "Discards 2 random cards per hand played",
                "score": 900,
                "tag_name": "",
                "tag_effect": "",
            },
        },
        "jokers": {
            "count": 2,
            "limit": 5,
            "highlighted_limit": 0,
            "cards": [
                _make_card(
                    id=100,
                    key="j_joker",
                    set="JOKER",
                    label="Joker",
                    effect="+4 Mult",
                    sell=1,
                ),
                _make_card(
                    id=101,
                    key="j_greedy_joker",
                    set="JOKER",
                    label="Greedy Joker",
                    effect="Played cards with Diamond suit give +3 Mult when scored",
                    sell=2,
                ),
            ],
        },
        "consumables": {
            "count": 1,
            "limit": 2,
            "highlighted_limit": 0,
            "cards": [
                _make_card(
                    id=200,
                    key="c_fool",
                    set="TAROT",
                    label="The Fool",
                    effect="Creates a copy of the last Tarot or Planet card used",
                    sell=1,
                ),
            ],
        },
        "cards": {
            "count": 44,
            "limit": 52,
            "highlighted_limit": 0,
            "cards": [],
        },
        "hand": {"count": 0, "limit": 8, "highlighted_limit": 5, "cards": []},
        "shop": {"count": 0, "limit": 2, "highlighted_limit": 0, "cards": []},
        "vouchers": {"count": 0, "limit": 0, "highlighted_limit": 0, "cards": []},
        "packs": {"count": 0, "limit": 2, "highlighted_limit": 0, "cards": []},
        "pack": {
            "count": 3,
            "limit": 3,
            "highlighted_limit": 1,
            "cards": [
                _make_card(
                    id=600,
                    key="c_tower",
                    set="TAROT",
                    label="The Tower",
                    effect="Enhances 1 selected card into a Stone Card",
                    sell=0,
                ),
                _make_card(
                    id=601,
                    key="c_lovers",
                    set="TAROT",
                    label="The Lovers",
                    effect="Enhances 1 selected card into a Wild Card",
                    sell=0,
                ),
                _make_card(
                    id=602,
                    key="c_magician",
                    set="TAROT",
                    label="The Magician",
                    effect="Enhances 1 selected card into a Lucky Card",
                    sell=0,
                ),
            ],
        },
    }

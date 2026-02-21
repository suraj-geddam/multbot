from __future__ import annotations


def encode_gamestate(gs: dict) -> str:
    """Encode a BalatroBot gamestate dict into compact text for the LLM."""
    lines: list[str] = []
    state = gs["state"]

    lines.append(f"STATE: {state}")
    lines.append(f"ANTE: {gs['ante_num']}/8 | ROUND: {gs['round_num']}")
    lines.append(f"MONEY: ${gs['money']}")

    # Blind + round info for active play states
    if state in ("SELECTING_HAND", "ROUND_EVAL"):
        blind = _current_blind(gs.get("blinds", {}))
        if blind:
            lines.append(f"BLIND: {blind['name']} {blind['score']}pts")
            if blind.get("effect"):
                lines.append(f"BLIND EFFECT: {blind['effect']}")
        r = gs.get("round", {})
        lines.append(f"HANDS: {r.get('hands_left', 0)} left | DISCARDS: {r.get('discards_left', 0)} left")

    # Blind selection overview
    if state == "BLIND_SELECT":
        lines.append("")
        lines.append("BLINDS:")
        for blind in _iter_blinds(gs.get("blinds", {})):
            tag = ""
            if blind.get("tag_name"):
                tag = f" [Tag: {blind['tag_name']} - {blind.get('tag_effect', '')}]"
            effect = f" ({blind['effect']})" if blind.get("effect") else ""
            lines.append(f"  {blind['type']}: {blind['name']} {blind['score']}pts{effect}{tag} [{blind['status']}]")

    # Hand cards (SELECTING_HAND only)
    if state == "SELECTING_HAND":
        hand = gs.get("hand", {})
        cards = hand.get("cards", [])
        if cards:
            lines.append("")
            card_strs = [f"{i}:{c['key']}" for i, c in enumerate(cards)]
            lines.append(f"HAND: {' '.join(card_strs)}")
            _append_modifiers(lines, cards)

    # Jokers (always shown if present)
    _append_area(lines, gs.get("jokers", {}), "JOKERS")

    # Consumables (always shown if present)
    _append_area(lines, gs.get("consumables", {}), "CONSUMABLES")

    # Shop contents
    if state == "SHOP":
        _append_shop(lines, gs)

    # Booster pack contents
    if state == "SMODS_BOOSTER_OPENED":
        pack = gs.get("pack", {})
        if pack.get("cards"):
            lines.append("")
            lines.append("PACK CONTENTS:")
            for i, c in enumerate(pack["cards"]):
                effect = c.get("value", {}).get("effect", "")
                label = f"{c['label']} - {effect}" if effect else c["label"]
                lines.append(f"  {i}: {label}")

    # Hand levels (show leveled-up or played hands)
    _append_hand_levels(lines, gs.get("hands", {}))

    return "\n".join(lines)


def _current_blind(blinds: dict) -> dict | None:
    for v in blinds.values():
        if isinstance(v, dict) and v.get("status") == "CURRENT":
            return v
    return None


def _iter_blinds(blinds: dict):
    for key in ("small", "big", "boss"):
        if key in blinds and isinstance(blinds[key], dict):
            yield blinds[key]


def _append_modifiers(lines: list[str], cards: list[dict]):
    mods = []
    for i, c in enumerate(cards):
        mod = c.get("modifier", {})
        if not mod:
            continue
        parts = []
        if mod.get("seal"):
            parts.append(f"seal={mod['seal']}")
        if mod.get("edition"):
            parts.append(f"edition={mod['edition']}")
        if mod.get("enhancement"):
            parts.append(f"enhance={mod['enhancement']}")
        if mod.get("eternal"):
            parts.append("eternal")
        if mod.get("rental"):
            parts.append("rental")
        if parts:
            mods.append(f"{i}:{','.join(parts)}")
    if mods:
        lines.append(f"MODIFIERS: {' '.join(mods)}")


def _append_area(lines: list[str], area: dict, label: str):
    cards = area.get("cards", [])
    if not cards:
        return
    lines.append("")
    lines.append(f"{label} ({area.get('count', len(cards))}/{area.get('limit', '?')}):")
    for i, c in enumerate(cards):
        effect = c.get("value", {}).get("effect", "")
        lines.append(f"  {i}: {c['label']} - {effect}")


def _append_shop(lines: list[str], gs: dict):
    r = gs.get("round", {})
    shop = gs.get("shop", {})
    if shop.get("cards"):
        lines.append("")
        lines.append(f"SHOP (reroll: ${r.get('reroll_cost', '?')}):")
        for i, c in enumerate(shop["cards"]):
            effect = c.get("value", {}).get("effect", "")
            label = f"{c['label']} - {effect}" if effect else c["label"]
            lines.append(f"  {i}: {label} (${c['cost']['buy']})")

    vouchers = gs.get("vouchers", {})
    if vouchers.get("cards"):
        lines.append("VOUCHERS:")
        for i, v in enumerate(vouchers["cards"]):
            effect = v.get("value", {}).get("effect", "")
            lines.append(f"  {i}: {v['label']} - {effect} (${v['cost']['buy']})")

    packs = gs.get("packs", {})
    if packs.get("cards"):
        lines.append("PACKS:")
        for i, p in enumerate(packs["cards"]):
            lines.append(f"  {i}: {p['label']} (${p['cost']['buy']})")


def _append_hand_levels(lines: list[str], hands: dict):
    if not hands:
        return
    parts = []
    for name, info in hands.items():
        if info.get("level", 1) > 1 or info.get("played", 0) > 0:
            parts.append(f"{name} Lv{info['level']} ({info['chips']}+{info['mult']}x)")
    if parts:
        lines.append("")
        lines.append(f"HAND LEVELS: {' | '.join(parts)}")

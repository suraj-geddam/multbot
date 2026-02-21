from multbot.state import encode_gamestate


def test_selecting_hand_contains_core_info(selecting_hand_state):
    text = encode_gamestate(selecting_hand_state)
    assert "STATE: SELECTING_HAND" in text
    assert "ANTE: 2/8" in text
    assert "MONEY: $12" in text
    assert "HANDS: 3 left" in text
    assert "DISCARDS: 2 left" in text


def test_selecting_hand_encodes_cards_compact(selecting_hand_state):
    text = encode_gamestate(selecting_hand_state)
    # Cards use key format with index prefix
    assert "0:H_A" in text
    assert "1:S_K" in text
    assert "7:C_9" in text


def test_selecting_hand_shows_modifiers(selecting_hand_state):
    text = encode_gamestate(selecting_hand_state)
    assert "seal=GOLD" in text
    assert "edition=FOIL" in text


def test_selecting_hand_shows_joker_effects(selecting_hand_state):
    text = encode_gamestate(selecting_hand_state)
    assert "Joker - +4 Mult" in text
    assert "Greedy Joker - Played cards with Diamond suit give +3 Mult" in text


def test_selecting_hand_shows_consumables(selecting_hand_state):
    text = encode_gamestate(selecting_hand_state)
    assert "The Fool" in text


def test_selecting_hand_shows_leveled_hands(selecting_hand_state):
    text = encode_gamestate(selecting_hand_state)
    assert "Pair Lv2" in text


def test_shop_shows_items_and_prices(shop_state):
    text = encode_gamestate(shop_state)
    assert "STATE: SHOP" in text
    assert "SHOP" in text
    assert "$" in text  # prices shown


def test_shop_shows_vouchers(shop_state):
    text = encode_gamestate(shop_state)
    assert "VOUCHERS:" in text


def test_booster_shows_pack_contents(booster_state):
    text = encode_gamestate(booster_state)
    assert "STATE: SMODS_BOOSTER_OPENED" in text
    assert "PACK CONTENTS:" in text


def test_no_hand_in_shop(shop_state):
    text = encode_gamestate(shop_state)
    # Shop state should not show HAND: section
    assert "\nHAND:" not in text

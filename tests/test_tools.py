from multbot.tools import get_tools


def test_selecting_hand_has_five_tools():
    tools = get_tools("SELECTING_HAND")
    names = [t["function"]["name"] for t in tools]
    assert names == ["play", "discard", "sell", "use", "rearrange"]


def test_shop_has_six_tools():
    tools = get_tools("SHOP")
    names = [t["function"]["name"] for t in tools]
    assert names == ["buy", "reroll", "next_round", "sell", "use", "rearrange"]


def test_booster_has_one_tool():
    tools = get_tools("SMODS_BOOSTER_OPENED")
    names = [t["function"]["name"] for t in tools]
    assert names == ["pack"]


def test_unknown_state_returns_empty():
    assert get_tools("MENU") == []
    assert get_tools("GAME_OVER") == []


def test_all_tools_have_reasoning_param():
    for state in ("SELECTING_HAND", "SHOP", "SMODS_BOOSTER_OPENED"):
        for tool in get_tools(state):
            params = tool["function"]["parameters"]
            assert "reasoning" in params["properties"]
            assert "reasoning" in params["required"]


def test_tools_are_valid_openai_format():
    for state in ("SELECTING_HAND", "SHOP", "SMODS_BOOSTER_OPENED"):
        for tool in get_tools(state):
            assert tool["type"] == "function"
            fn = tool["function"]
            assert "name" in fn
            assert "description" in fn
            assert fn["parameters"]["type"] == "object"

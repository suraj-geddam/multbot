from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from openai import AsyncOpenAI

from .client import BalatroClient, BalatroError
from .collector import Collector
from .prompt import SYSTEM_PROMPT
from .state import encode_gamestate
from .tools import get_tools

logger = logging.getLogger(__name__)

MAX_CONSECUTIVE_FAILURES = 3


class Bot:
    def __init__(
        self,
        balatro_host: str = "127.0.0.1",
        balatro_port: int = 12346,
        llm_base_url: str = "http://localhost:8080/v1",
        llm_api_key: str = "not-needed",
        llm_model: str = "local",
        output_dir: str = "runs",
    ):
        self._balatro = BalatroClient(balatro_host, balatro_port)
        self._llm = AsyncOpenAI(base_url=llm_base_url, api_key=llm_api_key)
        self._model = llm_model
        self._output_dir = Path(output_dir)

    async def run(
        self, deck: str = "RED", stake: str = "WHITE", seed: str | None = None,
    ):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        seed_str = seed or "random"
        run_dir = self._output_dir / self._model / f"{timestamp}_{deck}_{stake}_{seed_str}"
        collector = Collector(run_dir)

        gamestate: dict = {}
        finish_reason = "unexpected_error"

        try:
            await self._balatro.call("menu")
            params: dict = {"deck": deck, "stake": stake}
            if seed:
                params["seed"] = seed
            gamestate = await self._balatro.call("start", params)
            logger.info(f"Game started: deck={deck} stake={stake} seed={seed_str}")

            consecutive_failures = 0

            while gamestate["state"] != "GAME_OVER":
                state = gamestate["state"]
                logger.debug(f"State: {state} | Ante {gamestate.get('ante_num')}, Round {gamestate.get('round_num')}, ${gamestate.get('money')}")

                match state:
                    case "BLIND_SELECT":
                        gamestate = await self._balatro.call("select")

                    case "ROUND_EVAL":
                        gamestate = await self._balatro.call("cash_out")

                    case "SELECTING_HAND" | "SHOP" | "SMODS_BOOSTER_OPENED":
                        gamestate, success = await self._llm_step(gamestate, collector)
                        if success:
                            consecutive_failures = 0
                        else:
                            consecutive_failures += 1
                            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                                finish_reason = "consecutive_failed_calls"
                                logger.error(f"Aborting: {MAX_CONSECUTIVE_FAILURES} consecutive failures")
                                break

                    case _:
                        logger.warning(f"Unknown state '{state}', refreshing")
                        gamestate = await self._balatro.call("gamestate")

            if finish_reason == "unexpected_error":
                finish_reason = "won" if gamestate.get("won") else "lost"

        except Exception:
            logger.exception("Bot crashed")
            finish_reason = "unexpected_error"

        finally:
            collector.finalize(gamestate, finish_reason)
            await self._balatro.close()

        logger.info(f"Game over: {finish_reason}")
        return collector.stats

    async def _llm_step(
        self, gamestate: dict, collector: Collector,
    ) -> tuple[dict, bool]:
        state_text = encode_gamestate(gamestate)
        tools = get_tools(gamestate["state"])

        request_body = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": state_text},
            ],
            "tools": tools,
            "tool_choice": "required",
        }

        # Call LLM
        try:
            response = await self._llm.chat.completions.create(**request_body)
            response_dict = response.model_dump()
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            collector.record_error(request_body, {"error": str(e)}, gamestate)
            return gamestate, False

        # Extract tool call
        choice = response.choices[0] if response.choices else None
        if not choice or not choice.message.tool_calls:
            logger.warning("LLM returned no tool call")
            collector.record_error(request_body, response_dict, gamestate)
            return gamestate, False

        tool_call = choice.message.tool_calls[0]
        method = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid tool call JSON: {e}")
            collector.record_error(request_body, response_dict, gamestate)
            return gamestate, False

        reasoning = args.pop("reasoning", "")
        logger.info(f"LLM -> {method}({args}) | {reasoning[:80]}")

        # Execute RPC
        try:
            new_gamestate = await self._balatro.call(method, args if args else None)
            collector.record_call(request_body, response_dict, gamestate, success=True)
            return new_gamestate, True
        except BalatroError as e:
            logger.warning(f"RPC rejected: {method}({args}): {e}")
            collector.record_failed(request_body, response_dict, gamestate)
            return gamestate, False

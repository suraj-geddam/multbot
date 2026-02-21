from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class RunStats:
    run_won: bool = False
    run_completed: bool = False
    final_ante: int = 0
    final_round: int = 0
    finish_reason: str = ""
    calls_total: int = 0
    calls_success: int = 0
    calls_error: int = 0
    calls_failed: int = 0
    tokens_in_total: int = 0
    tokens_out_total: int = 0
    time_total_ms: int = 0


class Collector:
    """Records LLM calls and game states for BalatroBench."""

    def __init__(self, output_dir: Path):
        self._dir = output_dir
        self._dir.mkdir(parents=True, exist_ok=True)
        (self._dir / "gamestates").mkdir(exist_ok=True)
        self._requests_f = open(self._dir / "requests.jsonl", "w")
        self._responses_f = open(self._dir / "responses.jsonl", "w")
        self._call_idx = 0
        self._start_time = time.monotonic_ns()
        self.stats = RunStats()

    def record_call(
        self, request: dict, response: dict, gamestate: dict, *, success: bool,
    ):
        custom_id = f"req-{self._call_idx}"
        self._requests_f.write(json.dumps({
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": request,
        }) + "\n")
        self._requests_f.flush()

        self._responses_f.write(json.dumps({
            "custom_id": custom_id,
            "response": {"status_code": 200, "body": response},
        }) + "\n")
        self._responses_f.flush()

        gs_path = self._dir / "gamestates" / f"{self._call_idx:04d}.json"
        gs_path.write_text(json.dumps(gamestate))

        self.stats.calls_total += 1
        if success:
            self.stats.calls_success += 1

        usage = response.get("usage", {})
        self.stats.tokens_in_total += usage.get("prompt_tokens", 0)
        self.stats.tokens_out_total += usage.get("completion_tokens", 0)

        self._call_idx += 1

    def record_error(self, request: dict, response: dict, gamestate: dict):
        self.record_call(request, response, gamestate, success=False)
        self.stats.calls_error += 1

    def record_failed(self, request: dict, response: dict, gamestate: dict):
        self.record_call(request, response, gamestate, success=False)
        self.stats.calls_failed += 1

    def finalize(self, gamestate: dict, finish_reason: str):
        elapsed = (time.monotonic_ns() - self._start_time) // 1_000_000
        self.stats.time_total_ms = elapsed
        self.stats.final_ante = gamestate.get("ante_num", 0)
        self.stats.final_round = gamestate.get("round_num", 0)
        self.stats.run_won = gamestate.get("won", False)
        self.stats.run_completed = True
        self.stats.finish_reason = finish_reason
        (self._dir / "stats.json").write_text(json.dumps(asdict(self.stats), indent=2))
        self.close()

    def close(self):
        if not self._requests_f.closed:
            self._requests_f.close()
        if not self._responses_f.closed:
            self._responses_f.close()

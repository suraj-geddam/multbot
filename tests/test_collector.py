import json
from pathlib import Path

from multbot.collector import Collector


def test_creates_output_directory(tmp_path):
    run_dir = tmp_path / "test_run"
    collector = Collector(run_dir)
    assert run_dir.exists()
    assert (run_dir / "gamestates").is_dir()
    collector.close()


def test_record_call_writes_jsonl(tmp_path):
    collector = Collector(tmp_path / "run")
    collector.record_call(
        request={"model": "test", "messages": []},
        response={"choices": [], "usage": {"prompt_tokens": 10, "completion_tokens": 5}},
        gamestate={"state": "SELECTING_HAND", "ante_num": 1, "round_num": 1},
        success=True,
    )
    collector.close()

    requests = (tmp_path / "run" / "requests.jsonl").read_text().strip().split("\n")
    assert len(requests) == 1
    req = json.loads(requests[0])
    assert req["custom_id"] == "req-0"
    assert req["body"]["model"] == "test"

    responses = (tmp_path / "run" / "responses.jsonl").read_text().strip().split("\n")
    assert len(responses) == 1

    gs_files = list((tmp_path / "run" / "gamestates").iterdir())
    assert len(gs_files) == 1


def test_finalize_writes_stats(tmp_path):
    collector = Collector(tmp_path / "run")
    collector.record_call(
        request={}, response={"usage": {"prompt_tokens": 100, "completion_tokens": 50}},
        gamestate={"state": "SHOP"}, success=True,
    )
    collector.finalize(
        gamestate={"ante_num": 3, "round_num": 7, "won": False},
        finish_reason="lost",
    )

    stats = json.loads((tmp_path / "run" / "stats.json").read_text())
    assert stats["final_ante"] == 3
    assert stats["final_round"] == 7
    assert stats["run_won"] is False
    assert stats["finish_reason"] == "lost"
    assert stats["calls_total"] == 1
    assert stats["calls_success"] == 1
    assert stats["tokens_in_total"] == 100
    assert stats["tokens_out_total"] == 50


def test_tracks_errors_and_failures(tmp_path):
    collector = Collector(tmp_path / "run")
    collector.record_call({}, {"usage": {}}, {}, success=True)
    collector.record_error({}, {"error": "no tool call"}, {})
    collector.record_failed({}, {"usage": {}}, {})
    collector.finalize({}, "lost")

    stats = json.loads((tmp_path / "run" / "stats.json").read_text())
    assert stats["calls_total"] == 3
    assert stats["calls_success"] == 1
    assert stats["calls_error"] == 1
    assert stats["calls_failed"] == 1

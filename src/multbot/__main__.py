from __future__ import annotations

import argparse
import asyncio
import logging

from .bot import Bot


def main():
    parser = argparse.ArgumentParser(
        prog="multbot",
        description="LLM-powered Balatro bot for BalatroBench",
    )
    parser.add_argument("--deck", default="RED", help="Deck to use (default: RED)")
    parser.add_argument("--stake", default="WHITE", help="Stake level (default: WHITE)")
    parser.add_argument("--seed", default=None, help="Game seed (default: random)")
    parser.add_argument("--model", default="local", help="LLM model name (default: local)")
    parser.add_argument("--llm-url", default="http://localhost:8080/v1", help="LLM base URL")
    parser.add_argument("--llm-key", default="not-needed", help="LLM API key")
    parser.add_argument("--host", default="127.0.0.1", help="BalatroBot host")
    parser.add_argument("--port", type=int, default=12346, help="BalatroBot port")
    parser.add_argument("--output", default="runs", help="Output directory (default: runs)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    bot = Bot(
        balatro_host=args.host,
        balatro_port=args.port,
        llm_base_url=args.llm_url,
        llm_api_key=args.llm_key,
        llm_model=args.model,
        output_dir=args.output,
    )

    stats = asyncio.run(bot.run(deck=args.deck, stake=args.stake, seed=args.seed))

    print(f"\n{'='*40}")
    print(f"Result: {stats.finish_reason}")
    print(f"Won: {stats.run_won}")
    print(f"Final ante: {stats.final_ante}, round: {stats.final_round}")
    print(f"LLM calls: {stats.calls_total} (ok:{stats.calls_success} err:{stats.calls_error} fail:{stats.calls_failed})")
    print(f"Tokens: {stats.tokens_in_total} in / {stats.tokens_out_total} out")
    print(f"Time: {stats.time_total_ms / 1000:.1f}s")


if __name__ == "__main__":
    main()

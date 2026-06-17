"""CLI entry point for airllm-benchmark."""
from __future__ import annotations

import argparse
import sys

from airllm_benchmark.shared.constants import VALID_METHODS
from airllm_benchmark.shared.version import VERSION


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="airllm-benchmark",
        description="Benchmark Ollama, HuggingFace baseline, and AirLLM inference.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument(
        "--method",
        choices=list(VALID_METHODS),
        default="all",
        help="Inference method to benchmark (default: all)",
    )
    parser.add_argument(
        "--prompt",
        default="Explain quantum entanglement in one sentence.",
        help="Prompt to send to the model",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=20,
        help="Maximum new tokens to generate (default: 20)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for results JSON (overrides RESULTS_DIR env var)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    print(f"airllm-benchmark v{VERSION}")
    print(f"Method : {args.method}")
    print(f"Prompt : {args.prompt!r}")
    print(f"Tokens : {args.max_tokens}")
    print("Not yet implemented — see TODO.md for implementation phases.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

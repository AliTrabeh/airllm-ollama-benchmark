"""CLI entry point for airllm-benchmark."""
from __future__ import annotations

import argparse
import sys

from airllm_benchmark.models.benchmark_result import BenchmarkResult
from airllm_benchmark.sdk.sdk import BenchmarkSDK
from airllm_benchmark.services.results_service import ResultsService
from airllm_benchmark.shared.config import load_config
from airllm_benchmark.shared.constants import VALID_METHODS
from airllm_benchmark.shared.hardware_profiler import HardwareProfiler, model_gb_from_name
from airllm_benchmark.shared.version import VERSION


def _print_hardware_summary(config: dict, method: str) -> None:
    profiler = HardwareProfiler()
    print(profiler.to_markdown())
    model_ids = []
    if method in ("hf_baseline", "all"):
        model_ids.append(config.get("model_id", ""))
    if method in ("airllm", "all"):
        model_ids.append(config.get("airllm_model_id", ""))
    for model_id in model_ids:
        model_gb = model_gb_from_name(model_id) if model_id else None
        if model_gb:
            rec = profiler.recommend_quantization(model_gb)
            print(f"Recommended quantization for {model_id} (~{model_gb:.1f} GB @ FP16): {rec}")
    print()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="airllm-benchmark",
        description="Benchmark Ollama, HuggingFace baseline, and AirLLM inference.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    parser.add_argument(
        "--method", choices=list(VALID_METHODS), default="all",
        help="Inference method to benchmark (default: all)",
    )
    parser.add_argument(
        "--prompt", default="Explain quantum entanglement in one sentence.",
        help="Prompt to send to the model",
    )
    parser.add_argument("--max-tokens", type=int, default=20,
                        help="Maximum new tokens to generate (default: 20)")
    parser.add_argument("--output-dir", default=None,
                        help="Directory for results JSON (overrides RESULTS_DIR env var)")
    parser.add_argument("--verbose", action="store_true",
                        help="Print detailed progress output")
    return parser.parse_args(argv)


def _run_single(
    sdk: BenchmarkSDK, config: dict, method: str, prompt: str, max_tokens: int
) -> BenchmarkResult:
    dispatch = {
        "ollama":      (sdk.run_ollama,      config.get("ollama_model", "tinyllama")),
        "hf_baseline": (sdk.run_hf_baseline, config.get("model_id", "gpt2")),
        "airllm":      (sdk.run_airllm,      config.get("airllm_model_id", "gpt2")),
    }
    fn, model = dispatch[method]
    return fn(prompt, model, max_tokens)


def _print_result(result: BenchmarkResult, *, verbose: bool = False) -> None:
    if verbose:
        import json  # noqa: PLC0415
        print(json.dumps(result.to_dict(), indent=2))
    else:
        status = "OK" if result.is_success else f"FAILED — {result.error}"
        print(f"  Status  : {status}")
        print(f"  Latency : {result.latency_s:.2f}s")
        print(f"  Tokens  : {result.tokens_generated}  ({result.tokens_per_second:.1f} tok/s)")
        print(f"  RAM     : {result.ram_peak_mb:.0f} MB peak")
        print(f"  Cost    : {result.cost_estimate}")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    config = load_config()
    if args.output_dir:
        config["results_dir"] = args.output_dir

    sdk = BenchmarkSDK(config=config)
    results_svc = ResultsService(config=config)

    print(f"airllm-benchmark v{VERSION}  |  method={args.method}  |  tokens={args.max_tokens}")
    _print_hardware_summary(config, args.method)

    try:
        if args.method == "all":
            report = sdk.run_all(args.prompt, args.max_tokens)
            for r in report.results:
                results_svc.save_result(r)
            path = results_svc.save_comparison(report)
            print(report.to_markdown())
            print(f"\nSaved -> {path}")
        else:
            result = _run_single(sdk, config, args.method, args.prompt, args.max_tokens)
            path = results_svc.save_result(result)
            _print_result(result, verbose=args.verbose)
            print(f"\nSaved -> {path}")
    except (ValueError, RuntimeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

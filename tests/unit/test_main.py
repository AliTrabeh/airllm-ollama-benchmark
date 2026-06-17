"""Tests for main.py CLI entry point."""
import pytest

from airllm_benchmark.main import main, parse_args


def test_parse_args_defaults() -> None:
    args = parse_args([])
    assert args.method == "all"
    assert args.max_tokens == 20
    assert not args.verbose


def test_parse_args_method_ollama() -> None:
    args = parse_args(["--method", "ollama"])
    assert args.method == "ollama"


def test_parse_args_method_airllm() -> None:
    args = parse_args(["--method", "airllm"])
    assert args.method == "airllm"


def test_parse_args_max_tokens() -> None:
    args = parse_args(["--max-tokens", "50"])
    assert args.max_tokens == 50


def test_parse_args_verbose() -> None:
    args = parse_args(["--verbose"])
    assert args.verbose


def test_parse_args_invalid_method() -> None:
    with pytest.raises(SystemExit):
        parse_args(["--method", "invalid"])


def test_main_returns_zero() -> None:
    assert main([]) == 0


def test_main_ollama_returns_zero() -> None:
    assert main(["--method", "ollama"]) == 0

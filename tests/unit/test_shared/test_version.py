"""Tests for shared/version.py and package __version__."""
import airllm_benchmark
from airllm_benchmark.shared.version import VERSION


def test_version_string() -> None:
    assert VERSION == "1.00"


def test_package_version_matches() -> None:
    assert airllm_benchmark.__version__ == VERSION

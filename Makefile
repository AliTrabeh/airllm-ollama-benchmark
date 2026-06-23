.PHONY: lint test run-ollama run-hf run-airllm run-all clean

lint:
	uv run ruff check src/ tests/

test:
	uv run pytest tests/unit -q

run-ollama:
	uv run airllm-benchmark --method ollama --verbose

run-hf:
	uv run airllm-benchmark --method hf_baseline --verbose

run-airllm:
	uv run airllm-benchmark --method airllm --verbose

run-all:
	uv run airllm-benchmark --method all

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache htmlcov .coverage

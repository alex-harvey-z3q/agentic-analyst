.PHONY: lint test clean

lint:
	ruff check .

test:
	pytest -q tests

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache

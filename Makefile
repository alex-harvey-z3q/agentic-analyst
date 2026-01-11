.PHONY: index lint test clean

index:
	@echo "Building retrieval index (this may take a while)..."
	python -m src.index_build

lint:
	ruff check .

test:
	pytest -q tests

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache

.PHONY: install train run test lint docker

install:
	python -m pip install -e '.[dev]'
train:
	python scripts/train.py
run:
	uvicorn app.main:app --reload
test:
	pytest -q
lint:
	ruff check .
docker:
	docker build -t glycotwin .

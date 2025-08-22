tests:
	pytest src

test-cov:
	pytest --cov-report=html --cov=. src

test-cov-profiler:
	python3 -m cProfile -o profile -m pytest --cov-report=html --cov=. src -vvv

pc-config:
	pre-commit autoupdate && pre-commit install --install-hooks

pc-after-commit:
	pre-commit run --from-ref origin/main --to-ref HEAD

pc-run-all:
	pre-commit run --all-files

pc-run:
	pre-commit run

build-env:
	docker-compose down && docker-compose up -d && docker-compose logs -f app

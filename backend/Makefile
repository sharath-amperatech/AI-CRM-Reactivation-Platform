.PHONY: install dev worker beat migrate migration downgrade lint format test \
        docker-up docker-down docker-logs docker-reset clean help

# ── Dev setup ─────────────────────────────────────────────────
install:
	uv sync --all-extras

dev:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

# ── Workers ───────────────────────────────────────────────────
worker:
	celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4 \
	  -Q default,workflows,embeddings,notifications

beat:
	celery -A app.tasks.celery_app beat --loglevel=info

flower:
	celery -A app.tasks.celery_app flower --port=5555

# ── Database / Migrations ─────────────────────────────────────
migrate:
	alembic upgrade head

migration:
	@test -n "$(name)" || (echo "Usage: make migration name=<description>" && exit 1)
	alembic revision --autogenerate -m "$(name)"

downgrade:
	alembic downgrade -1

db-reset:
	alembic downgrade base && alembic upgrade head

# ── Code quality ──────────────────────────────────────────────
lint:
	ruff check app/ tests/
	mypy app/

format:
	ruff format app/ tests/
	ruff check --fix app/ tests/

# ── Tests ─────────────────────────────────────────────────────
test:
	pytest -v --tb=short

test-cov:
	pytest -v --cov=app --cov-report=html --cov-report=term-missing

# ── Docker ───────────────────────────────────────────────────
docker-up:
	docker compose up -d

docker-up-obs:
	docker compose --profile observability up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f $(svc)

docker-reset:
	docker compose down -v && docker compose up -d

# ── Cleanup ───────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .coverage htmlcov .mypy_cache .ruff_cache .pytest_cache

help:
	@echo "ReactivIQ Backend Makefile"
	@echo ""
	@echo "  make install        Install all dependencies (uv sync)"
	@echo "  make dev            Run FastAPI dev server with hot reload"
	@echo "  make worker         Run Celery worker"
	@echo "  make beat           Run Celery Beat scheduler"
	@echo "  make migrate        Apply all pending Alembic migrations"
	@echo "  make migration name=<desc>  Create new migration"
	@echo "  make lint           Run ruff + mypy"
	@echo "  make format         Auto-format with ruff"
	@echo "  make test           Run pytest"
	@echo "  make docker-up      Start all Docker services"
	@echo "  make docker-down    Stop all Docker services"

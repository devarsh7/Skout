.PHONY: install dev backend frontend mcp seed test lint format

install:
	python -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	@echo "\n✅ Installed. Activate: source .venv/bin/activate"

backend:
	uvicorn backend.main:app --reload --port 8000

frontend:
	streamlit run frontend/streamlit_app.py

mcp:
	python -m backend.mcp_server.server

seed:
	python scripts/seed_demo_creators.py

dev:
	@bash scripts/run_dev.sh

test:
	pytest tests/ -v

lint:
	ruff check backend/ frontend/ scripts/ tests/

format:
	ruff format backend/ frontend/ scripts/ tests/

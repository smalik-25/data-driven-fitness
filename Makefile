.PHONY: install ingest build build-prod analyze export-public dashboard airflow test lint clean

install:        ## install Python deps into the active venv
	pip install -r requirements.txt

ingest:         ## run all source extractors -> data/raw/ (Phase 1)
	python -m ingestion.run_ingestion

build:          ## run dbt against the local DuckDB (dev) target
	cd dbt_project && dbt build --target dev --profiles-dir .

build-prod:     ## promote de-identified marts to BigQuery (prod) target (Phase 6)
	cd dbt_project && dbt build --target prod --profiles-dir .

analyze:        ## run the analysis scripts (Phase 4)
	python -m analysis.energy_balance
	python -m analysis.regional_hypertrophy
	python -m analysis.protein_lean
	python -m analysis.recovery_load
	python -m analysis.volume_efficiency
	python -m analysis.measurement_uncertainty

export-public:  ## export de-identified marts -> committed dashboard/sources/ddf/public.duckdb
	python scripts/export_public_db.py

dashboard: export-public  ## run the Evidence.dev site locally (Phase 5)
	cd dashboard && npm run sources && npm run dev

airflow:        ## bring up local Airflow (Dockerized) (Phase 6)
	docker compose -f airflow/docker-compose.yaml up

test:           ## dbt tests + pytest
	cd dbt_project && dbt test --target dev --profiles-dir . || true
	pytest -q

lint:
	ruff check .

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache

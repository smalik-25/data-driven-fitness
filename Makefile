.PHONY: install ingest build analyze dashboard test lint clean

install:        ## install Python deps into the active venv
	pip install -r requirements.txt

ingest:         ## run all source extractors -> data/raw/ (Phase 1)
	python -m ingestion.run_ingestion

build:          ## run dbt against the local DuckDB (dev) target
	cd dbt_project && dbt build --target dev

build-prod:     ## promote de-identified marts to BigQuery (prod) target (Phase 6)
	cd dbt_project && dbt build --target prod

analyze:        ## run the analysis scripts (Phase 4)
	python -m analysis.energy_balance
	python -m analysis.regional_hypertrophy
	python -m analysis.protein_lean
	python -m analysis.recovery_load
	python -m analysis.volume_efficiency
	python -m analysis.measurement_uncertainty

dashboard:      ## run the Evidence.dev site locally (Phase 5)
	cd dashboard && npm run dev

test:           ## dbt tests + pytest
	cd dbt_project && dbt test --target dev || true
	pytest -q

lint:
	ruff check .

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .ruff_cache

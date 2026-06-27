# Airflow orchestration

One DAG, `data_driven_fitness`, runs the whole pipeline weekly:

```
ingest → dbt_build → dbt_test → analyze → dashboard_build
```

Each task is a thin `BashOperator` that calls the project's own CLI entrypoints,
so the real logic stays in the tested modules and the DAG graph reads as the
pipeline lineage in the Airflow UI.

## Run locally

```bash
# from the repo root
docker compose -f airflow/docker-compose.yaml up airflow-init   # first run only
docker compose -f airflow/docker-compose.yaml up
```

Open http://localhost:8080 (airflow / airflow), enable the `data_driven_fitness`
DAG, and trigger it. The repo is mounted at `/opt/airflow/project`; Python deps
are installed into the workers on boot via `_PIP_ADDITIONAL_REQUIREMENTS`.

## Notes & caveats

- **The `dashboard_build` task needs Node**, which isn't in the base Airflow
  image. For a fully containerized run, bake a custom image with Node + the
  Evidence deps; otherwise run `npm run build` on the host and treat that task as
  a placeholder. This tradeoff is called out rather than hidden.
- **Raw data** must be present under `data/raw/` (or re-ingested by the `ingest`
  task). It is never committed — mount it locally.
- **dbt enhancement:** `dbt_build` is a single BashOperator. Swapping it for an
  `astronomer-cosmos` `DbtTaskGroup` renders each model as its own task for
  model-level lineage — a deliberate next step, not done here to keep the image
  light.
- Validate the DAG parses with `airflow dags list` (or `python dags/ddf_pipeline.py`
  inside the container) before triggering.

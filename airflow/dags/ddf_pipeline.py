"""Data Driven Fitness — end-to-end pipeline DAG.

Chains the whole project as one weekly run, with explicit task dependencies so the
DAG graph reads as the pipeline lineage in the Airflow UI:

    ingest  ->  dbt_build  ->  dbt_test  ->  analyze  ->  dashboard_build

Each stage is a BashOperator invoking the project's own CLI entrypoints, so the
tasks stay thin and the real logic lives in the tested modules (ingestion/,
dbt_project/, analysis/, dashboard/). The repo is mounted at PROJECT_DIR inside
the Airflow container (see airflow/README.md); DDF_BRONZE points dbt's staging
reads at the bronze Parquet.

dbt note: this uses BashOperator for simplicity and portability. To render each
dbt model as its own Airflow task (model-level lineage), swap dbt_build for an
astronomer-cosmos DbtTaskGroup — a documented Phase-2 enhancement.
"""

from __future__ import annotations

import os

import pendulum
from airflow.models.dag import DAG
from airflow.operators.bash import BashOperator

# Repo root inside the container. Override via the PROJECT_DIR env var.
PROJECT_DIR = os.environ.get("PROJECT_DIR", "/opt/airflow/project")

COMMON_ENV = {
    "PROJECT_DIR": PROJECT_DIR,
    "PYTHONPATH": PROJECT_DIR,
    "DDF_BRONZE": f"{PROJECT_DIR}/data/raw",
}

default_args = {
    "owner": "sam",
    "retries": 1,
    "retry_delay": pendulum.duration(minutes=2),
}

with DAG(
    dag_id="data_driven_fitness",
    description="ingest -> dbt -> analyze -> dashboard",
    schedule="@weekly",
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    default_args=default_args,
    tags=["ddf", "portfolio"],
) as dag:
    # 1 — Ingest local sources to bronze Parquet (NHANES stays opt-in/offline).
    ingest = BashOperator(
        task_id="ingest",
        bash_command=f"cd {PROJECT_DIR} && python -m ingestion.run_ingestion",
        env=COMMON_ENV,
        append_env=True,
    )

    # 2 — Build the warehouse (silver + gold marts) on the DuckDB dev target.
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            f"cd {PROJECT_DIR}/dbt_project && dbt build --target dev --profiles-dir ."
        ),
        env=COMMON_ENV,
        append_env=True,
    )

    # 3 — Run the data-quality tests as a discrete, visible gate.
    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=(
            f"cd {PROJECT_DIR}/dbt_project && dbt test --target dev --profiles-dir ."
        ),
        env=COMMON_ENV,
        append_env=True,
    )

    # 4 — Run the analysis scripts (writes figures + results).
    analyze = BashOperator(
        task_id="analyze",
        bash_command=(
            f"cd {PROJECT_DIR} && "
            "python -m analysis.energy_balance && "
            "python -m analysis.regional_hypertrophy && "
            "python -m analysis.protein_lean && "
            "python -m analysis.recovery_load && "
            "python -m analysis.volume_efficiency && "
            "python -m analysis.measurement_uncertainty"
        ),
        env=COMMON_ENV,
        append_env=True,
    )

    # 5 — Refresh and build the Evidence static site from the marts.
    dashboard_build = BashOperator(
        task_id="dashboard_build",
        bash_command=(
            f"cd {PROJECT_DIR}/dashboard && npm ci && npm run sources && npm run build"
        ),
        env=COMMON_ENV,
        append_env=True,
    )

    ingest >> dbt_build >> dbt_test >> analyze >> dashboard_build

{#
  Centralizes how staging models read the Phase-1 bronze Parquet.

  In the dev (DuckDB) target this expands to read_parquet() over the local files.
  In prod (BigQuery) the bronze layer would instead be loaded tables, so staging
  models are the single place that would need to swap source — keep raw reads out
  of silver/marts.
#}
{% macro read_bronze(relpath) %}
    read_parquet('{{ var("bronze_dir") }}/{{ relpath }}')
{% endmacro %}

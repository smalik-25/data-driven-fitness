"""Ingestion layer: source-specific extractors that land raw data as Parquet.

Each module exposes a dataclass record shape and a client/parser with a public
generator method. Ingestion is fully decoupled from modeling.
"""

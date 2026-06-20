# Document Fetch Worker

**Type:** deterministic

## Purpose

Download, fetch, and normalize source material into clean machine-readable payloads.

## Inputs

- URL list from source discovery

## Outputs

- Raw text
- Clean text
- Section blocks
- Tables
- Metadata

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Deterministic — no LLM calls, reproducible with fixed seeds

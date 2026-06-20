# Reliability Worker

**Type:** deterministic

## Purpose

Audit annotation reliability and training-label health using Krippendorff's Alpha.

## Inputs

- Annotation tables

## Outputs

- Reliability report with alpha scores by label family
- Alert flags

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Deterministic — no LLM calls, reproducible with fixed seeds

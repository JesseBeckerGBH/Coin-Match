# Benchmark Runner Worker

**Type:** deterministic

## Purpose

Execute offline tests for candidate methods against frozen evaluation datasets.

## Inputs

- Experiment spec
- Dataset pointers
- Training/evaluation code

## Outputs

- Metrics (top1_accuracy, top5_recall, MRR, ECE, manual_review_rate, etc.)
- Run logs

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Deterministic — no LLM calls, reproducible with fixed seeds

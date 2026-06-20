# Calibration Worker

**Type:** deterministic

## Purpose

Turn raw model scores into trustworthy probabilities using temperature scaling.

## Inputs

- Raw logits or similarity scores
- Ground-truth outcomes

## Outputs

- Calibrated score mapping
- Confidence thresholds
- Review-routing policy

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Deterministic — no LLM calls, reproducible with fixed seeds

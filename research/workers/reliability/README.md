# Reliability Worker

**Type:** deterministic

## Purpose

Audit annotation reliability and training-label health using Krippendorff's Alpha.

## Contract

- Input: Structured payload from orchestrator
- Output: WorkerResult envelope (see `docs/architecture/worker-contracts.md`)

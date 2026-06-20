# Calibration Worker

**Type:** deterministic

## Purpose

Turn raw model scores into trustworthy probabilities using temperature scaling.

## Contract

- Input: Structured payload from orchestrator
- Output: WorkerResult envelope (see `docs/architecture/worker-contracts.md`)

# Benchmark Runner Worker

**Type:** deterministic

## Purpose

Execute offline tests for candidate methods against frozen evaluation datasets.

## Contract

- Input: Structured payload from orchestrator
- Output: WorkerResult envelope (see `docs/architecture/worker-contracts.md`)

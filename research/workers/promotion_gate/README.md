# Promotion Gate Worker

**Type:** hybrid

## Purpose

Decide whether a candidate method moves from research into staging or production.

## Inputs

- Benchmark results
- Reliability report
- Calibration report
- Engineering cost estimate

## Outputs

- Decision: promote / stage-only / watchlist / reject

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Uses LLM for reasoning — include prompt from `research/prompts/`

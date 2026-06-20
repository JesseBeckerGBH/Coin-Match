# Experiment Design Worker

**Type:** agentic

## Purpose

Translate a promising method into a concrete benchmark plan with hypothesis, baseline, metrics, and pass/fail thresholds.

## Inputs

- Candidate card
- Relevance data
- Data readiness data

## Outputs

- Experiment spec (objective, hypothesis, baseline, variant, metrics, thresholds)

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Uses LLM for reasoning — include prompt from `research/prompts/`

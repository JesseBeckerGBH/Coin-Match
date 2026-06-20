# Data Requirements Worker

**Type:** hybrid

## Purpose

Determine whether CoinMatch has the right data to test the method realistically.

## Inputs

- Candidate card
- Dataset inventory

## Outputs

- Data readiness assessment with missing_assets and recommended_next_action

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Uses LLM for reasoning — include prompt from `research/prompts/`

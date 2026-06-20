# Reporting Worker

**Type:** hybrid

## Purpose

Produce weekly and monthly research summaries for leadership review.

## Inputs

- Candidate database
- Benchmark outcomes
- Promotion decisions

## Outputs

- Weekly digest
- Monthly method leaderboard
- Archived decisions log

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Uses LLM for reasoning — include prompt from `research/prompts/`

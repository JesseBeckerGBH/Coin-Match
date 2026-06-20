# Relevance Worker

**Type:** agentic

## Purpose

Map each candidate method to one or more CoinMatch platform jobs (image retrieval, multimodal identification, grade estimation, confidence calibration, etc.).

## Inputs

- Candidate math cards

## Outputs

- Relevance-tagged candidate set with primary_job and recommended_phase

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Uses LLM for reasoning — include prompt from `research/prompts/`

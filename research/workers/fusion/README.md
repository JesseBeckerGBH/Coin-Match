# Fusion Worker

**Type:** hybrid

## Purpose

Combine evidence from image embeddings, OCR text, metadata, and physical measurements using Bayesian probabilistic fusion.

## Inputs

- Candidate match scores from multiple subsystems

## Outputs

- Final posterior ranking
- Evidence contribution record

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Uses LLM for reasoning — include prompt from `research/prompts/`

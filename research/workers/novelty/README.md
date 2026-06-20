# Novelty Worker

**Type:** hybrid

## Purpose

Distinguish truly new math from new applications of legacy math.

## Inputs

- Candidate cards
- Historical candidate database

## Outputs

- Novelty classification (genuinely_new, new_application, known)

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Uses LLM for reasoning — include prompt from `research/prompts/`

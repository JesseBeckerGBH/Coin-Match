# Ticket Writer Worker

**Type:** agentic

## Purpose

Convert approved experiments or promotions into GitHub-ready implementation tickets with epics, issues, and acceptance criteria.

## Inputs

- Experiment and promotion outputs

## Outputs

- Epic title
- Issue titles and descriptions
- Acceptance criteria

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Uses LLM for reasoning — include prompt from `research/prompts/`

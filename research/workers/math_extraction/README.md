# Math Extraction Worker

**Type:** agentic

## Purpose

Detect formulas, mathematical methods, loss functions, scoring rules, calibration methods, reliability methods, ranking methods, and optimization objectives within documents.

## Inputs

- Normalized documents

## Outputs

- Candidate math cards (method_name, math_family, formula_text, use_case, etc.)

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Uses LLM for reasoning — include prompt from `research/prompts/`

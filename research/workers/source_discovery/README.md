# Source Discovery Worker

**Type:** hybrid

## Purpose

Find new candidate material from arXiv, journals, GitHub, blogs, CV papers, statistics sources, and numismatic sources.

## Inputs

- Topic list
- Seed domains
- Search templates
- Date windows

## Outputs

- Document URLs
- Metadata records
- Freshness score
- Domain trust score

## Implementation Notes

- Returns a `WorkerResult` envelope (see `docs/architecture/worker-contracts.md`)
- Uses LLM for reasoning — include prompt from `research/prompts/`

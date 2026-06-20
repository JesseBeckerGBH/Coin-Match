# Research Engine Architecture

## Overview

The CoinMatch Research Engine is a 14-worker pipeline that continuously finds new mathematical methods relevant to coin identification, matching, grading, valuation, and confidence scoring — then tests them before any production adoption.

## Design Principles

1. **Orchestrator + Workers** — Central coordinator dispatches to specialized workers
2. **Deterministic benchmarks** — No method enters production without beating baseline on measurable metrics
3. **Structured handoffs** — Every worker uses the same input/output envelope
4. **Separate discovery from judgment** — Finding methods and evaluating them are different jobs

## Worker Map

| # | Worker | Type | Purpose |
|---|--------|------|---------|
| 1 | Source Discovery | hybrid | Find new papers, repos, blogs |
| 2 | Document Fetch | deterministic | Download and normalize content |
| 3 | Math Extraction | agentic | Extract formulas and methods |
| 4 | Relevance | agentic | Map methods to CoinMatch jobs |
| 5 | Novelty | hybrid | Classify new vs. known methods |
| 6 | Data Requirements | hybrid | Check if we can test this method |
| 7 | Experiment Design | agentic | Create benchmark plans |
| 8 | Benchmark Runner | deterministic | Execute offline tests |
| 9 | Reliability | deterministic + LLM | Audit label quality (Krippendorff's α) |
| 10 | Calibration | deterministic | Turn scores into probabilities |
| 11 | Fusion | hybrid | Combine evidence streams (Bayesian) |
| 12 | Promotion Gate | hybrid | Decide promote/reject |
| 13 | Ticket Writer | agentic | Generate GitHub issues |
| 14 | Reporting | hybrid | Weekly/monthly digests |

## High-Level Flow

```
Discover sources → Parse documents → Extract math candidates
  → Score relevance → Check novelty → Assess data readiness
    → Design experiments → Run benchmarks
      → Audit reliability → Calibrate confidence
        → Fuse evidence → Promotion gate
          → Write tickets / Generate reports
```

## Scoring Model

Candidate score: S = 0.25R + 0.20N + 0.20D + 0.20B + 0.15E

- R = relevance score
- N = novelty score
- D = data readiness score
- B = benchmark potential score
- E = explainability score

A method only proceeds if it passes both a score threshold AND a benchmark threshold.

## Core Math Stack

| Method | Role |
|--------|------|
| Triplet loss | Learn coin-specific embedding geometry |
| Cosine similarity | Fast similarity retrieval |
| Bayesian posterior updating | Fuse image + metadata evidence |
| Softmax with temperature | Calibrated probabilities for UX |
| Krippendorff's Alpha | Validate annotation reliability |

## Implementation Phases

### Phase 1: Skeleton
- Source registry, scheduler, document ingestion
- Candidate extraction schema, candidate database

### Phase 2: Research Intelligence
- Math extraction, relevance, novelty workers
- Data requirements, experiment design workers

### Phase 3: Benchmark Engine
- Frozen evaluation dataset
- Triplet-loss + cosine retrieval baselines
- Bayesian reranker, calibration, reliability scoring

### Phase 4: Promotion & Operations
- Promotion gate, ticket writer, weekly reporting
- Dashboard views, GitHub issue automation

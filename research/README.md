# CoinMatch Research Engine

A math discovery and evaluation pipeline that continuously finds candidate methods, scores whether they are relevant to CoinMatch, prototypes them in a sandbox, and only promotes them into production after they beat baseline on measurable metrics.

## Quick Start

```bash
pip install -r requirements.txt
python -m research.orchestrator.main    # Run discovery cycle
python -m research.db.migrations create # Create DB tables
```

## Structure

```
research/
  orchestrator/    # Central coordinator
  workers/         # 14 specialized workers
  prompts/         # LLM prompt templates
  db/              # Database models and migrations
  data/            # Raw and processed research data
  experiments/     # Experiment configs and results
  benchmarks/      # Benchmark datasets and scripts
```

## Phases

1. **Skeleton** — Source registry, scheduler, document ingestion, candidate DB
2. **Research Intelligence** — Math extraction, relevance, novelty, experiment design
3. **Benchmark Engine** — Frozen eval set, baselines, Bayesian reranker, calibration
4. **Promotion & Ops** — Promotion gate, ticket writer, reporting, dashboards

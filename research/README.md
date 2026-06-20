# CoinMatch Research Engine

A math discovery and evaluation pipeline that continuously finds candidate methods, scores whether they are relevant to CoinMatch, prototypes them in a sandbox, and only promotes them into production ranking or matching logic after they beat baseline on measurable metrics.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the orchestrator (discovery cycle)
python -m research.orchestrator.main

# Run a specific worker
python -m research.workers.source_discovery.service
```

## Architecture

See `docs/architecture/research-engine.md` for the full design.

## Structure

```
research/
├── orchestrator/       # Central coordinator
│   ├── main.py         # Entry point
│   └── scheduler.py    # Job scheduling
├── workers/            # 14 specialized workers
│   ├── source_discovery/
│   ├── document_fetch/
│   ├── math_extraction/
│   ├── relevance/
│   ├── novelty/
│   ├── data_requirements/
│   ├── experiment_design/
│   ├── benchmark_runner/
│   ├── reliability/
│   ├── calibration/
│   ├── fusion/
│   ├── promotion_gate/
│   ├── ticket_writer/
│   └── reporting/
├── prompts/            # LLM prompt templates
├── db/                 # Database models and migrations
├── data/               # Raw and processed research data
├── experiments/        # Experiment configs and results
├── benchmarks/         # Benchmark datasets and scripts
└── requirements.txt
```

## Implementation Phases

1. **Skeleton** — Source registry, scheduler, document ingestion, candidate DB
2. **Research Intelligence** — Math extraction, relevance, novelty, experiment design
3. **Benchmark Engine** — Frozen eval set, baselines, Bayesian reranker, calibration
4. **Promotion & Ops** — Promotion gate, ticket writer, reporting, dashboards

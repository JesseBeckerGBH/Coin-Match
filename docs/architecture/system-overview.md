# CoinMatch System Overview

## Domains

| Domain | Tech | Purpose |
|--------|------|---------|
| `frontend/` | Next.js, Tailwind | Collector/dealer dashboard UI |
| `backend/` | FastAPI, SQLAlchemy | REST API, auth, billing, matching logic |
| `engine/` | Python | Grading, matching, scraping workers |
| `research/` | Python, FastAPI | Math discovery & evaluation pipeline |
| `shared/` | Python | Cross-cutting config, types, constants |
| `docs/` | Markdown | Product, architecture, operations docs |

## Data Flow

```
User uploads coin image
  -> Frontend sends to Backend API
    -> Backend calls Engine (grading + matching)
      -> Engine uses embeddings + similarity scoring
        -> Results ranked by Bayesian posterior
          -> Calibrated confidence returned to user
```

## Research Engine

The research engine is a separate pipeline that continuously discovers, evaluates, and promotes new mathematical methods into the production matching system. See `research/README.md` and `docs/architecture/research-engine.md` for details.

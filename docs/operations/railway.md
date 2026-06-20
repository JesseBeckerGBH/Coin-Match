# Railway Deployment Notes

## Services

| Service | Stack | Start Command |
|---------|-------|---------------|
| Backend | FastAPI + Uvicorn | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Frontend | Next.js | `npm start` |
| Engine | Python workers | Scheduled jobs |
| Research | Python + FastAPI | Scheduled + API |

## Environment Variables

Each service reads from `.env` (see `.env.example` files in each domain). Shared config is defined in `shared/config/env_schema.py`.

## Health Checks

- Backend: `GET /health`
- Frontend: `GET /`
- Research: `GET /research/health`

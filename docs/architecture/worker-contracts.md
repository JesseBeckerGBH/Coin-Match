# Research Worker Contracts

All workers in the research engine follow a shared input/output contract.

## WorkerResult Envelope

```json
{
  "worker_name": "string",
  "status": "success | error",
  "input_ref": "uuid or null — reference to input record",
  "output_ref": "uuid or null — reference to output record",
  "payload": {},
  "errors": [],
  "metrics": {
    "duration_ms": 0,
    "tokens_used": 0
  }
}
```

## Rules

- Workers MUST be idempotent where practical
- Workers MUST NOT have side effects beyond writing to the research database
- All worker outputs MUST include the `worker_name` field
- Errors MUST be structured (not raw exception strings)
- Metrics SHOULD include duration and token usage for agentic workers

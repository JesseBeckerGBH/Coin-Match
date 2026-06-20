# Research Database Schema

## Tables

### research_documents

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | primary key |
| url | text | canonical URL |
| title | text | normalized title |
| source_type | text | paper, blog, repo, benchmark, guide |
| published_at | timestamp | source publication date |
| discovered_at | timestamp | ingestion time |
| clean_text | text | normalized content |
| trust_score | float | 0-1, source trust estimate |
| novelty_score | float | 0-1, source novelty estimate |

### math_candidates

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | primary key |
| document_id | uuid | FK → research_documents |
| method_name | text | extracted method name |
| math_family | text | ranking, reliability, retrieval, etc. |
| use_case | text | mapped CoinMatch job |
| formula_text | text | optional LaTeX or plain text |
| relevance_score | float | CoinMatch fit score |
| data_readiness_score | float | testability score |
| novelty_class | text | new, new_application, known |
| status | text | discovered, scored, queued, benchmarked, promoted, rejected |
| created_at | timestamp | |

### experiment_runs

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | primary key |
| candidate_id | uuid | FK → math_candidates |
| baseline_name | text | comparison baseline method |
| variant_name | text | candidate variant being tested |
| started_at | timestamp | |
| finished_at | timestamp | |
| metrics_json | jsonb | full metric payload |
| passed | boolean | did it beat baseline? |

### promotion_decisions

| Column | Type | Notes |
|--------|------|-------|
| id | uuid | primary key |
| candidate_id | uuid | FK → math_candidates |
| decision | text | promote, stage-only, watchlist, reject |
| rationale | text | summarized reasons |
| benchmark_strength | float | 0-1 |
| deployment_risk | float | 0-1 |
| created_at | timestamp | |

## Indexes

- `math_candidates(status)` — for queue queries
- `math_candidates(document_id)` — for joins
- `experiment_runs(candidate_id)` — for result lookups
- `promotion_decisions(candidate_id)` — for decision history

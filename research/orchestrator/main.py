"""
CoinMatch Research Orchestrator

Central coordinator that manages the discovery → extraction → evaluation → promotion pipeline.
"""
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from research.workers.source_discovery.service import run as discover_sources
from research.workers.document_fetch.service import run as fetch_documents
from research.workers.math_extraction.service import run as extract_math
from research.workers.relevance.service import run as score_relevance
from research.workers.novelty.service import run as check_novelty
from research.workers.data_requirements.service import run as check_data
from research.workers.experiment_design.service import run as design_experiment
from research.workers.promotion_gate.service import run as check_promotion

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("orchestrator")


SCORING_WEIGHTS = {
    "relevance": 0.25,
    "novelty": 0.20,
    "data_readiness": 0.20,
    "benchmark_potential": 0.20,
    "explainability": 0.15,
}

PROMOTION_THRESHOLD = 0.78


def compute_candidate_score(candidate: Dict[str, Any]) -> float:
    """Weighted candidate score: S = 0.25R + 0.20N + 0.20D + 0.20B + 0.15E"""
    return sum(
        weight * candidate.get(f"{key}_score", 0.0)
        for key, weight in SCORING_WEIGHTS.items()
    )


async def run_discovery_cycle():
    """Execute one full discovery → evaluation cycle."""
    logger.info("=" * 60)
    logger.info("Starting research discovery cycle at %s", datetime.utcnow().isoformat())
    logger.info("=" * 60)

    # Phase 1: Discover sources
    logger.info("Phase 1: Discovering sources...")
    sources = discover_sources({
        "topics": [
            "coin identification",
            "feature matching",
            "metric learning",
            "image retrieval",
            "multimodal matching",
            "confidence calibration",
            "inter-rater reliability",
            "anomaly detection",
            "probabilistic ranking",
            "numismatic grading",
        ],
        "max_results": 20,
    })
    logger.info("  Found %d source candidates", len(sources.get("payload", {}).get("sources", [])))

    # Phase 2: Fetch and parse documents
    logger.info("Phase 2: Fetching documents...")
    documents = fetch_documents(sources.get("payload", {}))

    # Phase 3: Extract math candidates
    logger.info("Phase 3: Extracting math candidates...")
    candidates = extract_math(documents.get("payload", {}))

    # Phase 4: Score relevance
    logger.info("Phase 4: Scoring relevance...")
    scored = score_relevance(candidates.get("payload", {}))

    # Phase 5: Check novelty
    logger.info("Phase 5: Checking novelty...")
    checked = check_novelty(scored.get("payload", {}))

    # Phase 6: Check data readiness
    logger.info("Phase 6: Checking data readiness...")
    ready = check_data(checked.get("payload", {}))

    # Phase 7: Design experiments for qualifying candidates
    logger.info("Phase 7: Designing experiments...")
    experiments = design_experiment(ready.get("payload", {}))

    # Phase 8: Promotion gate
    logger.info("Phase 8: Checking promotion gate...")
    decisions = check_promotion(experiments.get("payload", {}))

    logger.info("=" * 60)
    logger.info("Discovery cycle complete at %s", datetime.utcnow().isoformat())
    logger.info("=" * 60)

    return decisions


def main():
    """Entry point for the research orchestrator."""
    logger.info("CoinMatch Research Orchestrator starting...")
    asyncio.run(run_discovery_cycle())


if __name__ == "__main__":
    main()

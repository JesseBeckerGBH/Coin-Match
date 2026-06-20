"""
CoinMatch Research Orchestrator
Coordinates the discovery -> extraction -> evaluation -> promotion pipeline.
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any

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
    """Execute one full discovery -> evaluation cycle."""
    logger.info("=" * 60)
    logger.info("Starting research discovery cycle at %s", datetime.utcnow().isoformat())

    # Import workers
    from research.workers.source_discovery.service import run as discover
    from research.workers.document_fetch.service import run as fetch
    from research.workers.math_extraction.service import run as extract
    from research.workers.relevance.service import run as score_relevance
    from research.workers.novelty.service import run as check_novelty
    from research.workers.data_requirements.service import run as check_data
    from research.workers.experiment_design.service import run as design_experiment
    from research.workers.promotion_gate.service import run as check_promotion

    # Pipeline: discover -> fetch -> extract -> score -> novelty -> data -> experiment -> promote
    topics = {
        "topics": [
            "coin identification", "feature matching", "metric learning",
            "image retrieval", "multimodal matching", "confidence calibration",
            "inter-rater reliability", "anomaly detection", "probabilistic ranking",
        ],
        "max_results": 20,
    }

    steps = [
        ("Source Discovery", discover),
        ("Document Fetch", fetch),
        ("Math Extraction", extract),
        ("Relevance Scoring", score_relevance),
        ("Novelty Check", check_novelty),
        ("Data Readiness", check_data),
        ("Experiment Design", design_experiment),
        ("Promotion Gate", check_promotion),
    ]

    payload = topics
    for name, worker_fn in steps:
        logger.info("Running: %s", name)
        result = worker_fn(payload)
        if result["status"] == "error":
            logger.warning("  %s returned errors: %s", name, result.get("errors"))
        payload = result.get("payload", {})

    logger.info("Discovery cycle complete at %s", datetime.utcnow().isoformat())
    logger.info("=" * 60)


def main():
    asyncio.run(run_discovery_cycle())


if __name__ == "__main__":
    main()

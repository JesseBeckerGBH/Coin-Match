"""
Research Engine Scheduler

Manages the cadence of discovery cycles and worker execution.
"""
import schedule
import time
import logging
from research.orchestrator.main import run_discovery_cycle

logger = logging.getLogger("scheduler")


def setup_schedule():
    """
    Weekly operating cadence:
    - Daily: source discovery and ingestion
    - Twice weekly: extraction, relevance, novelty, scoring
    - Weekly: experiment queue cut, benchmark run, leadership digest
    - Monthly: production promotion review
    """
    # Daily discovery
    schedule.every().day.at("06:00").do(lambda: run_discovery_cycle())

    logger.info("Scheduler configured. Running on cadence.")


def run_scheduler():
    """Run the scheduler loop."""
    setup_schedule()
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    run_scheduler()

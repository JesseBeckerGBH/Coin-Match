"""
Research Engine Scheduler — manages cadence of discovery cycles.
"""
import schedule
import time
import logging

logger = logging.getLogger("scheduler")


def setup_schedule():
    """
    Weekly operating cadence:
    - Daily: source discovery and ingestion
    - Twice weekly: extraction, relevance, novelty, scoring
    - Weekly: experiment queue cut, benchmark run, leadership digest
    - Monthly: production promotion review
    """
    from research.orchestrator.main import run_discovery_cycle
    import asyncio
    schedule.every().day.at("06:00").do(lambda: asyncio.run(run_discovery_cycle()))
    logger.info("Scheduler configured.")


def run_scheduler():
    setup_schedule()
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    run_scheduler()

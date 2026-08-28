#!/usr/bin/env python3
"""
StudioSonar Autonomous Overnight Job Entrypoint.

Runs the full 24/7 autonomous multi-agent cycle to completion as a Cloud Run Job.
Cloud Run Jobs have NO request timeout: the loop (telemetry ingestion, anomaly
scanning, Gemini report authoring, GCS publication) runs reliably through the
night on the hourly scheduler, independent of any HTTP request lifecycle.
"""

import logging
import sys
from datetime import datetime, timezone

from src.agents.orchestrator import taskmaster_orchestrator
from src.core.gcs_report_manager import gcs_report_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("studiosonar.job")


def main():
    logger.info("Starting autonomous overnight cycle (cycle_type=ALL)...")
    started_at = datetime.now(timezone.utc).isoformat()
    gcs_report_manager.save_cycle_ledger({
        "status": "RUNNING",
        "started_at": started_at,
        "completed_at": None,
        "source": "overnight_job",
    })
    try:
        results = taskmaster_orchestrator.run_autonomous_cycle(cycle_type="ALL")
        published = results.get("gcs_published_reports", [])
        actions = results.get("actions_executed", [])
        gcs_report_manager.save_cycle_ledger({
            "status": "COMPLETED",
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "source": "overnight_job",
            "reports_published": len(published),
            "actions_executed": len(actions),
        })
        logger.info(
            "Autonomous cycle completed: %s actions executed, %s reports published to GCS",
            len(actions),
            len(published),
        )
        for path in published:
            logger.info("  published -> %s", path)
    except Exception as e:  # noqa: BLE001
        gcs_report_manager.save_cycle_ledger({
            "status": "FAILED",
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "source": "overnight_job",
            "error": str(e),
        })
        logger.exception("Autonomous overnight cycle failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
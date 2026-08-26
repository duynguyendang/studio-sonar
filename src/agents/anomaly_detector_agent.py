import logging
from typing import Dict, List, Any
from src.agents.base_agent import BaseADKAgent, ADKAgentMessage
from src.core.guardrails import guardrails
from src.mcp.bq_tools import (
    query_bigquery_sentiment_spikes,
    query_bigquery_viral_trends,
    search_bigquery_vector_context
)

logger = logging.getLogger("studiosonar.agent.anomaly")

class AnomalyDetectorAgent(BaseADKAgent):
    """
    Specialist Agent 1: BigQuery Analytics & Anomaly Detection.
    Connects to Google BigQuery OLAP to detect velocity spikes and viral trends.
    """

    def __init__(self):
        super().__init__(
            name="AnomalyDetectorAgent",
            role="Data & Vector Telemetry Specialist",
            system_instruction=(
                "You are the BigQuery Data Specialist. You monitor real-time video and comment streams, "
                "detect velocity accelerations, perform vector clustering, and validate anomalies against guardrails."
            ),
            tools=[
                query_bigquery_sentiment_spikes,
                query_bigquery_viral_trends,
                search_bigquery_vector_context
            ]
        )

    def scan_pr_anomalies(self, time_window_hours: int = 6) -> List[Dict[str, Any]]:
        """Queries BigQuery and filters valid PR crisis spikes."""
        logger.info(f"[{self.name}] Scanning BigQuery for sentiment velocity spikes...")
        bq_res = self.execute_tool(
            "query_bigquery_sentiment_spikes",
            time_window_hours=time_window_hours,
            min_comment_velocity_pct=200.0
        )
        
        valid_spikes = []
        for anomaly in bq_res.get("anomalies", []):
            passed, reason = guardrails.validate_crisis_anomaly(anomaly)
            if passed:
                # Vector enrich with topic cluster
                vector_info = self.execute_tool(
                    "search_bigquery_vector_context",
                    query_text=anomaly.get("video_title", "")
                )
                anomaly["vector_clusters"] = vector_info.get("clusters", [])
                valid_spikes.append(anomaly)
            else:
                logger.info(f"[{self.name}] Anomaly dampened: {reason}")

        return valid_spikes

    def scan_viral_trends(self, min_view_acceleration_pct: float = 300.0) -> List[Dict[str, Any]]:
        """Queries BigQuery for breakout viral topics and hook trajectories."""
        logger.info(f"[{self.name}] Scanning BigQuery for viral trend breakout velocities...")
        bq_res = self.execute_tool(
            "query_bigquery_viral_trends",
            min_view_acceleration_pct=min_view_acceleration_pct,
            lookback_hours=8
        )
        
        valid_trends = []
        for trend in bq_res.get("trends", []):
            passed, reason = guardrails.validate_viral_trend(trend)
            if passed:
                valid_trends.append(trend)
            else:
                logger.info(f"[{self.name}] Trend dampened: {reason}")

        return valid_trends

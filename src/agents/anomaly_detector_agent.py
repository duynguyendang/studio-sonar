"""
Specialist Agent 1: BigQuery Analytics & Anomaly Detector (Pure Google ADK Agent).
"""

import logging
from typing import Dict, List, Any
from google.adk import Agent
from src.agents.base_agent import create_pure_adk_agent
from src.mcp.bq_tools import (
    query_bigquery_sentiment_spikes,
    query_bigquery_viral_trends,
    search_bigquery_vector_context
)

logger = logging.getLogger("studiosonar.agent.anomaly")

ANOMALY_DETECTOR_INSTRUCTION = (
    "You are the AnomalyDetectorAgent, an autonomous BigQuery Data & Vector Telemetry Specialist. "
    "Your operational goals: "
    "1. Query Google BigQuery real-time video snapshot streams to calculate comment and view velocity spikes. "
    "2. Detect negative sentiment escalations (sentiment < -0.60, velocity > 200%) and handoff to PRCrisisStrategistAgent. "
    "3. Spot breakout viral topics (velocity > 300%) and handoff to ViralContentCreatorAgent. "
    "4. Enrich anomalies using Vector Search semantic clustering."
)

ANOMALY_DETECTOR_TOOLS = [
    query_bigquery_sentiment_spikes,
    query_bigquery_viral_trends,
    search_bigquery_vector_context
]

# 100% Pure Native Google ADK Agent Instance
anomaly_detector_agent: Agent = create_pure_adk_agent(
    name="AnomalyDetectorAgent",
    instruction=ANOMALY_DETECTOR_INSTRUCTION,
    tools=ANOMALY_DETECTOR_TOOLS
)

# Export alias for backwards compatibility
native_anomaly_detector = anomaly_detector_agent

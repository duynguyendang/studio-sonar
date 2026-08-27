"""
StudioSonar Native Google ADK Root Agent & Workflow Visualization Entry Point.
Compatible with `adk web`, `adk run`, and Google ADK Evaluation Suites.
"""

from google.adk import Agent, Workflow
from src.agents.orchestrator import (
    taskmaster_agent,
    taskmaster_workflow
)
from src.agents.anomaly_detector_agent import anomaly_detector_agent
from src.agents.pr_crisis_agent import pr_crisis_agent
from src.agents.viral_content_agent import viral_content_agent
from src.agents.channel_monitor_agent import channel_monitor_agent

# Standard ADK Agent & Workflow Entry Point Symbols
root_agent: Agent = taskmaster_agent
agent: Agent = taskmaster_agent
workflow: Workflow = taskmaster_workflow
root_workflow: Workflow = taskmaster_workflow

# Export all specialists for direct modular evaluation
specialists = {
    "channel_monitor": channel_monitor_agent,
    "anomaly_detector": anomaly_detector_agent,
    "pr_crisis": pr_crisis_agent,
    "viral_content": viral_content_agent
}

"""
StudioSonar Native Google ADK Root Agent Entry Point.
Compatible with `adk web`, `adk run`, and Google ADK Evaluation Suites.
"""

from google.adk import Agent
from src.agents.orchestrator import taskmaster_agent

# Standard ADK Entry Point Symbol
root_agent: Agent = taskmaster_agent
agent: Agent = taskmaster_agent

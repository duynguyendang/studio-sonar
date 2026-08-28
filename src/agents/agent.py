"""
StudioSonar Standard Google ADK Root Agent Entrypoint.
Required by `adk run`, `adk web`, and `adk deploy cloud_run`.
"""

from google.adk import Agent, Workflow
from src.agents.orchestrator import taskmaster_agent, taskmaster_workflow

agent: Agent = taskmaster_agent
root_agent: Agent = taskmaster_agent
workflow: Workflow = taskmaster_workflow
root_workflow: Workflow = taskmaster_workflow

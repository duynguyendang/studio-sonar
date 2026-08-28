"""
StudioSonar Taskmaster Agent Entrypoint.
Delegates to the Google ADK Multi-Agent Team Orchestrator.
"""

from src.agents.orchestrator import taskmaster_orchestrator, taskmaster_agent

root_agent = taskmaster_agent
agent = taskmaster_agent

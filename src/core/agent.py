"""
StudioSonar Taskmaster Agent Entrypoint.
Delegates to the Google ADK Multi-Agent Team Orchestrator.
"""

from src.agents.orchestrator import taskmaster_orchestrator, StudioSonarOrchestrator

# Standard taskmaster instance powered by Google ADK Multi-Agent System
taskmaster_agent = taskmaster_orchestrator

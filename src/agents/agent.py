from google.adk import Agent
from src.agents.orchestrator import taskmaster_orchestrator

# Standard Google ADK Root Agent Entrypoint
# Required by `adk run`, `adk web`, and `adk deploy cloud_run`
agent = taskmaster_orchestrator.get_root_adk_agent()
root_agent = agent

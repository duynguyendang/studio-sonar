"""
Specialist Agent 2: PR Crisis Strategist & Brand Safety Resolver (Pure Google ADK Agent).
"""

import logging
from google.adk import Agent
from src.agents.base_agent import create_pure_adk_agent
from src.mcp.slack_tools import dispatch_slack_crisis_alert
from src.mcp.notion_tools import generate_notion_action_board
from src.mcp.search_tools import search_google_live_intel

logger = logging.getLogger("studiosonar.agent.pr")

PR_CRISIS_INSTRUCTION = (
    "You are the PRCrisisStrategistAgent, an Executive PR Strategist and Crisis Response Specialist. "
    "When handed a sentiment or velocity anomaly: "
    "1. Immediately call search_google_live_intel to query external news and community forums regarding the controversy. "
    "2. Perform root-cause analysis combining comment sentiment with verified Google Search intelligence findings. "
    "3. Formulate a 3-step containment stance: 1) Pinned clarification comment, 2) Description update, 3) Ad pause. "
    "4. Use dispatch_slack_crisis_alert to send immediate Red Alerts to #war-room-alerts. "
    "5. Use generate_notion_action_board to create an emergency triage card for executive leadership."
)

PR_CRISIS_TOOLS = [
    search_google_live_intel,
    dispatch_slack_crisis_alert,
    generate_notion_action_board
]

# 100% Pure Native Google ADK Agent Instance
pr_crisis_agent: Agent = create_pure_adk_agent(
    name="PRCrisisStrategistAgent",
    instruction=PR_CRISIS_INSTRUCTION,
    tools=PR_CRISIS_TOOLS
)

# Export alias for backwards compatibility
native_pr_crisis_agent = pr_crisis_agent

"""
Specialist Agent 3: Viral Shortform Scriptwriter & Retention Architect (Pure Google ADK Agent).
"""

import logging
from google.adk import Agent
from src.agents.base_agent import create_pure_adk_agent
from src.mcp.gdocs_tools import create_google_doc_video_script
from src.mcp.notion_tools import generate_notion_action_board

logger = logging.getLogger("studiosonar.agent.content")

VIRAL_CONTENT_INSTRUCTION = (
    "You are the ViralContentCreatorAgent, an elite short-form video retention architect and scriptwriter. "
    "When a breakout trend or viral audio is detected: "
    "1. Enforce the 4 high-CTR psychological hook frameworks (Contrarian Truth, Financial Catastrophe, Curiosity Gap, Insider Secrets). "
    "2. Author a tight 60-second video script structured into: 0-3s Hook, 4-15s Friction/Problem, 16-45s Breakthrough/Solution, 46-60s CTA. "
    "3. Use create_google_doc_video_script to automatically publish the formatted script draft into Google Docs. "
    "4. Use generate_notion_action_board to log a production sprint card for the video editing team."
)

VIRAL_CONTENT_TOOLS = [
    create_google_doc_video_script,
    generate_notion_action_board
]

# 100% Pure Native Google ADK Agent Instance
viral_content_agent: Agent = create_pure_adk_agent(
    name="ViralContentCreatorAgent",
    instruction=VIRAL_CONTENT_INSTRUCTION,
    tools=VIRAL_CONTENT_TOOLS
)

# Export alias for backwards compatibility
native_viral_content_agent = viral_content_agent

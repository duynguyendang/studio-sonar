"""
Specialist Agent 3: Viral Shortform Scriptwriter & Retention Architect (Pure Google ADK Agent).
"""

import logging
from google.adk import Agent
from src.agents.base_agent import create_pure_adk_agent
from src.mcp.gdocs_tools import create_google_doc_video_script
from src.mcp.notion_tools import generate_notion_action_board
from src.mcp.search_tools import search_google_live_intel

logger = logging.getLogger("studiosonar.agent.content")

VIRAL_CONTENT_INSTRUCTION = (
    "You are the ViralContentCreatorAgent, an elite short-form video retention architect and scriptwriter. "
    "When a breakout trend or viral audio is detected: "
    "1. Call search_google_live_intel to retrieve the origin story, meme catalyst, and community context behind the trend. "
    "2. Enforce the 5 high-CTR psychological hook frameworks (Contrarian Truth, Financial Catastrophe, Curiosity Gap, Insider Secrets, Visual Transformation) grounded in live web search facts. "
    "3. Author a tight 60-second video script structured into: 0-3s Hook, 4-15s Friction/Problem, 16-45s Breakthrough/Solution, 46-60s CTA. "
    "4. Use create_google_doc_video_script to automatically publish the formatted script draft into Google Docs. "
    "5. Use generate_notion_action_board to log a production sprint card for the video editing team."
)

VIRAL_CONTENT_TOOLS = [
    search_google_live_intel,
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

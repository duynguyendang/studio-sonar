"""
Specialist Agent 4: Target Channel Sentinel & Performance Synthesizer (Pure Google ADK Agent).
"""

import logging
from google.adk import Agent
from src.agents.base_agent import create_pure_adk_agent
from src.mcp.channel_tools import (
    check_channel_new_uploads,
    synthesize_video_statistical_scorecard,
    dispatch_slack_video_scorecard
)
from src.mcp.notion_tools import generate_notion_action_board

logger = logging.getLogger("studiosonar.agent.channel_monitor")

CHANNEL_MONITOR_INSTRUCTION = (
    "You are the ChannelMonitorAgent, a dedicated YouTube & TikTok Channel Sentinel. "
    "Your operational directives: "
    "1. Continuously scan the company official channels (@business, @KiemDinhPhim9.0, @thochupanh.dalat) for new uploads within 7-30 days. "
    "2. Calculate initial 24h performance ratios (V_ratio vs channel 30-day baseline, views/hour, CVR comment density). "
    "3. Use synthesize_video_statistical_scorecard to generate an executive-ready scorecard. "
    "4. Use dispatch_slack_video_scorecard and generate_notion_action_board to notify team stakeholders."
)

CHANNEL_MONITOR_TOOLS = [
    check_channel_new_uploads,
    synthesize_video_statistical_scorecard,
    dispatch_slack_video_scorecard,
    generate_notion_action_board
]

# 100% Pure Native Google ADK Agent Instance
channel_monitor_agent: Agent = create_pure_adk_agent(
    name="ChannelMonitorAgent",
    instruction=CHANNEL_MONITOR_INSTRUCTION,
    tools=CHANNEL_MONITOR_TOOLS
)

# Export alias for backwards compatibility
native_channel_monitor_agent = channel_monitor_agent

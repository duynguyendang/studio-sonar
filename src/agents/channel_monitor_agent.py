import logging
from typing import Dict, List, Any, Optional
from google.adk import Agent
from src.agents.base_agent import BaseADKAgent, create_adk_agent
from src.mcp.channel_tools import (
    check_channel_new_uploads,
    synthesize_video_statistical_scorecard,
    dispatch_slack_video_scorecard
)
from src.mcp.notion_tools import generate_notion_action_board

logger = logging.getLogger("studiosonar.agent.channel_monitor")

CHANNEL_MONITOR_INSTRUCTION = (
    "You are the Dedicated Channel Sentinel. You monitor the company's video feed for new uploads, "
    "calculate statistical metrics (views/hour, engagement ratios, velocity vs channel baseline), "
    "synthesize executive-ready intelligence takeaways, and dispatch performance scorecards to Slack & Notion."
)

CHANNEL_MONITOR_TOOLS = [
    check_channel_new_uploads,
    synthesize_video_statistical_scorecard,
    dispatch_slack_video_scorecard,
    generate_notion_action_board
]

# Native Google ADK Agent Instance
native_channel_monitor_agent: Agent = create_adk_agent(
    name="ChannelMonitorAgent",
    instruction=CHANNEL_MONITOR_INSTRUCTION,
    tools=CHANNEL_MONITOR_TOOLS
)

class ChannelMonitorAgent(BaseADKAgent):
    """
    Specialist Agent 4: Target Channel Sentinel & Performance Synthesizer (Google ADK Native).
    Continuously monitors the company's official channel for newly published videos,
    tracks telemetry accumulation, and autonomously authors executive statistical scorecards.
    """

    def __init__(self):
        super().__init__(
            name="ChannelMonitorAgent",
            role="Company Channel Sentinel & Statistical Performance Synthesizer",
            system_instruction=CHANNEL_MONITOR_INSTRUCTION,
            tools=CHANNEL_MONITOR_TOOLS
        )

    def monitor_and_synthesize(self, channel_id: Optional[str] = None) -> Dict[str, Any]:
        """Monitors target channel, detects new videos, computes stats, and dispatches scorecards."""
        from src.core.registry_manager import registry_manager
        primary_ch = registry_manager.get_primary_company_channel()
        target_channel_id = channel_id or primary_ch.get("channel_id", "ch_default")
        
        logger.info(f"[{self.name}] Checking target channel '{target_channel_id}' for new uploads...")
        
        # Step 1: Detect newly published video
        upload_data = self.execute_tool("check_channel_new_uploads", channel_id=target_channel_id)
        video = upload_data.get("video", {})
        comments = upload_data.get("comments_sample", [])
        dist = upload_data.get("sentiment_distribution", {})

        # Step 2: Compute statistical metrics & synthesize executive statements
        logger.info(f"[{self.name}] Synthesizing statistical scorecard for '{video.get('title')}'...")
        scorecard = self.execute_tool(
            "synthesize_video_statistical_scorecard",
            video_data=video,
            sentiment_distribution=dist,
            sample_comments=comments
        )

        executed_actions = []

        # Step 3: Dispatch Slack Scorecard
        slack_res = self.execute_tool(
            "dispatch_slack_video_scorecard",
            scorecard=scorecard
        )
        executed_actions.append({"tool": "dispatch_slack_video_scorecard", "result": slack_res})

        # Step 4: Dispatch Notion Record
        notion_res = self.execute_tool(
            "generate_notion_action_board",
            title=f"Scorecard: {video.get('title', '')[:35]}...",
            priority="Normal",
            assigned_team="Media Analytics & Insights",
            summary=f"Automated 24h upload scorecard for '{video.get('title', '')}' ({scorecard.get('performance_verdict', '')}).",
            action_items=[
                f"Review 24h upload velocity ({scorecard.get('performance_verdict', '')})",
                "Approve short-form hook derivatives based on audience praise",
                "Archive statistical benchmark to BigQuery historical ledger"
            ]
        )
        executed_actions.append({"tool": "generate_notion_action_board", "result": notion_res})

        logger.info(f"[{self.name}] Scorecard published & dispatched (2 actions).")
        return {
            "status": "SUCCESS",
            "video_id": video.get("video_id"),
            "scorecard": scorecard,
            "actions_executed": executed_actions
        }

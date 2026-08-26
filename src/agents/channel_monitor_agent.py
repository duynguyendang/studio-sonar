import logging
from typing import Dict, List, Any, Optional
from src.agents.base_agent import BaseADKAgent, ADKAgentMessage

from src.mcp.channel_tools import (
    check_channel_new_uploads,
    synthesize_video_statistical_scorecard,
    dispatch_slack_video_scorecard
)
from src.mcp.notion_tools import generate_notion_action_board

logger = logging.getLogger("studiosonar.agent.channel_monitor")

class ChannelMonitorAgent(BaseADKAgent):
    """
    Specialist Agent 4: Target Channel Sentinel & Performance Synthesizer.
    Continuously monitors the company's official channel for newly published videos,
    tracks telemetry accumulation, and autonomously authors executive statistical scorecards.
    """

    def __init__(self):
        super().__init__(
            name="ChannelMonitorAgent",
            role="Company Channel Sentinel & Statistical Performance Synthesizer",
            system_instruction=(
                "You are the Dedicated Channel Sentinel. You monitor the company's video feed for new uploads, "
                "calculate statistical metrics (views/hour, engagement ratios, velocity vs channel baseline), "
                "synthesize executive-ready intelligence takeaways, and dispatch performance scorecards to Slack & Notion."
            ),
            tools=[
                check_channel_new_uploads,
                synthesize_video_statistical_scorecard,
                dispatch_slack_video_scorecard,
                generate_notion_action_board
            ]
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

        actions_taken = []

        # Step 3: Dispatch Slack Scorecard
        logger.info(f"[{self.name}] Dispatching Video Performance Scorecard to Slack...")
        slack_res = self.execute_tool("dispatch_slack_video_scorecard", scorecard=scorecard)
        actions_taken.append({"agent": self.name, "tool": "dispatch_slack_video_scorecard", "result": slack_res})

        # Step 4: Create Notion Performance Review Board
        logger.info(f"[{self.name}] Logging scorecard to Notion Executive Workspace...")
        notion_res = self.execute_tool(
            "generate_notion_action_board",
            title=f"Video Scorecard: {video.get('title')}",
            priority="Normal",
            assigned_team="Executive & Growth Marketing",
            summary=scorecard.get("executive_statement", ""),
            action_items=scorecard.get("recommended_next_actions", []),
            due_in_hours=48
        )
        actions_taken.append({"agent": self.name, "tool": "generate_notion_action_board", "result": notion_res})

        return {
            "status": "PROCESSED",
            "scorecard": scorecard,
            "actions_executed": actions_taken
        }

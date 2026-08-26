import logging
from typing import Dict, List, Any
from src.agents.base_agent import BaseADKAgent, ADKAgentMessage
from src.core.viral_hook_engine import ViralHookEngine
from src.mcp.gdocs_tools import create_google_doc_video_script
from src.mcp.notion_tools import generate_notion_action_board

logger = logging.getLogger("studiosonar.agent.content")

class ViralContentCreatorAgent(BaseADKAgent):
    """
    Specialist Agent 3: Viral Shortform Scriptwriter & Retention Architect.
    Applies proven psychological hook frameworks (Financial Catastrophe, Contrarian Roasting, Extreme Curiosity Gaps)
    to craft high-retention video scripts and commit drafts directly to Google Docs.
    """

    def __init__(self):
        super().__init__(
            name="ViralContentCreatorAgent",
            role="Creative Scriptwriter & High-CTR Hook Architect",
            system_instruction=(
                "You are the High-CTR Viral Content Specialist. You enforce the 4 proven psychological hook frameworks: "
                "1) Financial Catastrophe & Costly Mistakes, 2) Contrarian Truth / 'ĐỪNG LÀM NHƯ...', "
                "3) Extreme Curiosity Gaps / 'DỞ TOÀN DIỆN', 4) Insider Authority / Silicon Valley Secrets. "
                "Never write boring academic intros. Always design high-tension, retention-optimized scripts."
            ),
            tools=[
                create_google_doc_video_script,
                generate_notion_action_board
            ]
        )


    def create_viral_script(self, trend_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Synthesizes retention-optimized script and commits to Google Docs & Notion."""
        logger.info(f"[{self.name}] Received viral trend handoff. Authoring 60s video script...")
        
        topic = trend_payload.get("trend_topic", "Breakout Tech Trend")
        accel = trend_payload.get("cross_platform_acceleration_pct", 0.0)


        actions_taken = []

        # 1. Author Google Doc Video Script
        logger.info(f"[{self.name}] Calling Google Docs MCP tool...")
        doc_res = self.execute_tool(
            "create_google_doc_video_script",
            doc_title=f"Script: {topic}",
            target_platform="TikTok & YouTube Shorts",
            trend_topic=topic,
            hook_3s="Stop building chatbots in 2026. Here is what real autonomous agents actually do.",
            problem_statement="Everyone is suffering from chatbot fatigue. Typing prompts into a window all day is not automation—it's just a new kind of busywork.",
            solution_core="Real Taskmasters run 24/7 in the background on Google Cloud. They monitor BigQuery data streams, analyze sentiment anomalies, and write your code and PR responses while you sleep.",
            call_to_action="Follow StudioSonar for the full architecture blueprint and deploy your first Taskmaster agent today.",
            visual_broll_notes=[
                "0:00 - Rapid cuts of frustrated user typing prompts into a basic chat UI",
                "0:15 - Screen recording of BigQuery live SQL stream and Slack red alert auto-firing",
                "0:45 - High-tech architecture diagram showing Google ADK + Cloud Run"
            ],
            estimated_duration_sec=60
        )
        actions_taken.append({"agent": self.name, "tool": "create_google_doc_video_script", "result": doc_res})

        # 2. Sync to Notion Production Workspace
        logger.info(f"[{self.name}] Calling Notion Board MCP tool...")
        notion_res = self.execute_tool(
            "generate_notion_action_board",
            title=f"Content Sprint: Produce '{topic}' Shortform Video",
            priority="High",
            assigned_team="Creative Studio & Media Production",
            summary=f"Viral breakout trend identified across YouTube & TikTok (+{accel:.1f}% view acceleration). Script pre-drafted in Google Docs.",
            action_items=[
                "Review Google Doc script draft and finalize B-roll assets",
                "Film 60s footage following the retention hook structure",
                "Schedule release for 6:00 PM peak engagement window"
            ],
            due_in_hours=24,
            reference_link=doc_res.get("doc_url")
        )
        actions_taken.append({"agent": self.name, "tool": "generate_notion_action_board", "result": notion_res})

        return actions_taken

    def handle_breakout_trend(self, trend_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Alias for create_viral_script."""
        return self.create_viral_script(trend_payload)


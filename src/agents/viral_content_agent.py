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
        context_snippet = trend_payload.get("context_snippet", "")

        # 1. Generate Retention-Optimized Script using Google Gemini Flash
        from src.core.llm_client import llm_client
        import json

        llm_prompt = f"""You are an elite YouTube Shorts & TikTok Retention Architect and Viral Scriptwriter.
Synthesize a high-CTR 60-second video script for the following topic/asset:
Topic: "{topic}"
Acceleration / Hot Index: +{accel:.1f}%
Context / Analysis: {context_snippet}

Apply the 4 proven psychological hook frameworks (Contrarian Truth, Financial / Costly Mistakes, Extreme Curiosity Gaps, Insider Secrets).

You MUST respond strictly in valid JSON format with the following keys:
{{
  "hook_3s": "A hypnotic, curiosity-inducing opening line for seconds 0-3 that stops the scroll.",
  "problem": "The core friction, debate, or misconception viewers face (seconds 4-20).",
  "solution": "The deep insight, unexpected breakdown, or technical resolution (seconds 21-48).",
  "call_to_action": "Clear, non-spammy conversion action (seconds 49-60).",
  "visual_broll_notes": [
    "0:00 - Visual description for hook",
    "0:15 - Visual description for problem statement",
    "0:45 - Visual description for climax resolution"
  ]
}}
"""
        hook_3s = f"If you are watching '{topic}', stop making this one fatal mistake."
        problem = f"Most creators and viewers completely misunderstand the core mechanics behind '{topic}'."
        solution = f"Here is the proven insider breakdown: focus on high-velocity retention signals and algorithmic pacing."
        cta = f"Follow StudioSonar for the full breakdown and surveillance report on '{topic}'."
        brolls = [
            f"0:00 - High-contrast fast cuts illustrating '{topic}'",
            "0:15 - Real-time metrics breakdown and engagement telemetry overlay",
            "0:45 - High-tech architecture blueprint with call-to-action banner"
        ]

        try:
            gemini_res = llm_client.generate(prompt=llm_prompt, system_instruction=self.system_instruction)
            if gemini_res:
                # Clean JSON markdown fences if present
                clean_json = gemini_res.strip()
                if clean_json.startswith("```json"):
                    clean_json = clean_json[7:]
                if clean_json.startswith("```"):
                    clean_json = clean_json[3:]
                if clean_json.endswith("```"):
                    clean_json = clean_json[:-3]
                parsed = json.loads(clean_json.strip())
                hook_3s = parsed.get("hook_3s", hook_3s)
                problem = parsed.get("problem", problem)
                solution = parsed.get("solution", solution)
                cta = parsed.get("call_to_action", cta)
                brolls = parsed.get("visual_broll_notes", brolls)
                logger.info(f"[{self.name}] Successfully synthesized dynamic script via Gemini Flash: '{hook_3s[:50]}...'")
        except Exception as e:
            logger.warning(f"[{self.name}] Gemini generation notice, using resilient fallback: {e}")

        actions_taken = []

        # 2. Author Google Doc Video Script
        logger.info(f"[{self.name}] Calling Google Docs MCP tool...")
        doc_res = self.execute_tool(
            "create_google_doc_video_script",
            doc_title=f"Script: {topic}",
            target_platform="TikTok & YouTube Shorts",
            trend_topic=topic,
            hook_3s=hook_3s,
            problem_statement=problem,
            solution_core=solution,
            call_to_action=cta,
            visual_broll_notes=brolls,
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


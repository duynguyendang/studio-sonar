import logging
from typing import Dict, List, Any
from google.adk import Agent
from src.agents.base_agent import BaseADKAgent, create_adk_agent
from src.core.viral_hook_engine import ViralHookEngine
from src.mcp.gdocs_tools import create_google_doc_video_script
from src.mcp.notion_tools import generate_notion_action_board

logger = logging.getLogger("studiosonar.agent.content")

VIRAL_CONTENT_INSTRUCTION = (
    "You are the High-CTR Viral Content Specialist. You enforce the 4 proven psychological hook frameworks: "
    "1) Financial Catastrophe & Costly Mistakes, 2) Contrarian Truth / 'ĐỪNG LÀM NHƯ...', "
    "3) Extreme Curiosity Gaps / 'DỞ TOÀN DIỆN', 4) Insider Authority / Silicon Valley Secrets. "
    "Never write boring academic intros. Always design high-tension, retention-optimized scripts."
)

VIRAL_CONTENT_TOOLS = [
    create_google_doc_video_script,
    generate_notion_action_board
]

# Native Google ADK Agent Instance
native_viral_content_agent: Agent = create_adk_agent(
    name="ViralContentCreatorAgent",
    instruction=VIRAL_CONTENT_INSTRUCTION,
    tools=VIRAL_CONTENT_TOOLS
)

class ViralContentCreatorAgent(BaseADKAgent):
    """
    Specialist Agent 3: Viral Shortform Scriptwriter & Retention Architect (Google ADK Native).
    Applies proven psychological hook frameworks (Financial Catastrophe, Contrarian Roasting, Extreme Curiosity Gaps)
    to craft high-retention video scripts and commit drafts directly to Google Docs.
    """

    def __init__(self):
        super().__init__(
            name="ViralContentCreatorAgent",
            role="Creative Scriptwriter & High-CTR Hook Architect",
            system_instruction=VIRAL_CONTENT_INSTRUCTION,
            tools=VIRAL_CONTENT_TOOLS
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
    "0:00 - Rapid zoom / visual disruption",
    "0:15 - Side-by-side comparison chart",
    "0:35 - High-contrast data overlay"
  ]
}}
"""
        try:
            raw_response = llm_client.generate(
                prompt=llm_prompt,
                system_instruction=self.system_instruction
            )
            if not raw_response:
                raise ValueError("LLM returned empty response")

            parsed_json = json.loads(raw_response.strip().replace("```json", "").replace("```", "").strip())
            hook_3s = parsed_json.get("hook_3s", f"99% người xem đang hiểu sai về {topic}!")
            problem = parsed_json.get("problem", f"Khi {topic} bùng nổ, hầu hết mọi người chỉ nhìn thấy phần nổi của tảng băng chìm.")
            solution = parsed_json.get("solution", f"Dữ liệu thực tế cho thấy sự dịch chuyển khổng lồ trong hành vi người dùng.")
            cta = parsed_json.get("call_to_action", f"Đăng ký kênh để không bỏ lỡ các phân tích chuyên sâu tiếp theo.")
            b_rolls = parsed_json.get("visual_broll_notes", [
                "0:00 - High-contrast text animation",
                "0:15 - Real-time telemetry dashboard graph",
                "0:40 - Retention payoff callout box"
            ])
        except Exception as e:
            logger.warning(f"[{self.name}] LLM dynamic generation fallback: {e}")
            hooks = ViralHookEngine.generate_high_octane_hooks(topic=topic, context={"accel": accel})
            hook_3s = hooks.get("framework_1_financial_catastrophe", {}).get("hook_3s", f"Cảnh báo: 3 sai lầm đắt giá về {topic}!")
            problem = f"Tại sao 90% nhà sáng tạo bỏ lỡ làn sóng {topic} trong khi nó đang tăng trưởng +{accel:.1f}%?"
            solution = f"Bí quyết nằm ở việc nắm bắt comment velocity và nhu cầu ngách của cộng đồng trước khi đối thủ nhận ra."
            cta = "Lưu lại video này và đăng ký kênh để đón đầu làn sóng tiếp theo!"
            b_rolls = [
                "0:00 - Red alert banner + dramatic sound effect",
                "0:15 - BigQuery analytics spike graph",
                "0:45 - High-contrast CTA overlay"
            ]

        # 2. Package Complete 60s Script with Visual Cues
        full_script = f"""# 🎬 60s Viral Video Script: {topic}
**Acceleration Metric:** +{accel:.1f}% Surge | **Format:** Vertical Shorts / TikTok (9:16)

---
### ⏱️ Timeline & Audio-Visual Blueprint:
- **🪝 0:00 - 0:03 (Hypnotic Hook):**
  > "{hook_3s}"
  *(Visual: {b_rolls[0] if len(b_rolls) > 0 else 'Fast punch-in'})*

- **⚠️ 0:04 - 0:20 (Friction & Problem):**
  > "{problem}"
  *(Visual: {b_rolls[1] if len(b_rolls) > 1 else 'Split screen comparison'})*

- **💡 0:21 - 0:48 (Breakdown & Solution Core):**
  > "{solution}"
  *(Visual: {b_rolls[2] if len(b_rolls) > 2 else 'Data overlay with highlight'})*

- **🎯 0:49 - 1:00 (Call To Action):**
  > "{cta}"
  *(Visual: End-card animation with subscription arrow)*
"""

        executed_actions = []

        # Tool 1: Create Google Doc
        gdocs_res = self.execute_tool(
            "create_google_doc_video_script",
            doc_title=f"Viral Script - {topic}",
            target_platform="TikTok / YouTube Shorts",
            trend_topic=topic,
            hook_3s=hook_3s,
            problem_statement=problem,
            solution_core=solution,
            call_to_action=cta,
            visual_broll_notes=b_rolls,
            estimated_duration_sec=60
        )
        executed_actions.append({"tool": "create_google_doc_video_script", "result": gdocs_res})

        # Tool 2: Notion Production Task
        notion_res = self.execute_tool(
            "generate_notion_action_board",
            title=f"Production Sprint: {topic[:35]}...",
            priority="High",
            assigned_team="Creative Studio & Shorts Team",
            summary=f"Automated 60s viral video draft generated for breakout trend (+{accel:.1f}% velocity surge).",
            action_items=[
                "Record A-Roll talking head using 3s hook",
                "Edit B-Roll pacing at 1.2x speed with sound effects",
                "Publish to YouTube Shorts & TikTok with #StudioSonar tags"
            ],
            reference_link=gdocs_res.get("document_url")
        )
        executed_actions.append({"tool": "generate_notion_action_board", "result": notion_res})

        logger.info(f"[{self.name}] Viral shortform script authored and pushed to Google Docs.")
        return executed_actions

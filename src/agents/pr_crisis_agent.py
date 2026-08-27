import logging
from typing import Dict, List, Any
from google.adk import Agent
from src.agents.base_agent import BaseADKAgent, create_adk_agent
from src.mcp.slack_tools import dispatch_slack_crisis_alert
from src.mcp.notion_tools import generate_notion_action_board

logger = logging.getLogger("studiosonar.agent.pr")

PR_CRISIS_INSTRUCTION = (
    "You are the Crisis Response Strategist. When handed an anomaly, you perform root-cause "
    "analysis on viewer sentiment, synthesize an actionable response stance, and dispatch "
    "immediate Slack Red Alerts and Notion triage cards without human intervention."
)

PR_CRISIS_TOOLS = [
    dispatch_slack_crisis_alert,
    generate_notion_action_board
]

# Native Google ADK Agent Instance
native_pr_crisis_agent: Agent = create_adk_agent(
    name="PRCrisisStrategistAgent",
    instruction=PR_CRISIS_INSTRUCTION,
    tools=PR_CRISIS_TOOLS
)

class PRCrisisStrategistAgent(BaseADKAgent):
    """
    Specialist Agent 2: PR Crisis Strategy & Executive Resolution (Google ADK Native).
    Analyzes root-cause drivers of backlash and executes immediate remediation via Slack and Notion.
    """

    def __init__(self):
        super().__init__(
            name="PRCrisisStrategistAgent",
            role="Executive PR Strategist & Crisis Resolver",
            system_instruction=PR_CRISIS_INSTRUCTION,
            tools=PR_CRISIS_TOOLS
        )

    def handle_incident(self, anomaly_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Executes full PR crisis evaluation and multi-endpoint dispatch."""
        logger.info(f"[{self.name}] Received PR anomaly handoff. Analyzing root cause...")
        
        channel = anomaly_payload.get("channel_title", "Brand Channel")
        title = anomaly_payload.get("video_title", "Video Upload")
        velocity = anomaly_payload.get("velocity_spike_pct", 0.0)
        quotes = anomaly_payload.get("sample_negative_comments", [])
        clusters = anomaly_payload.get("vector_clusters", [])
        
        cluster_summary = ""
        if clusters:
            cluster_summary = f" Primary vector cluster: '{clusters[0].get('matched_topic')}'."

        # Prompt Gemini LLM for Real Dynamic Root Cause & Stance Synthesis
        from src.core.llm_client import llm_client
        import json

        sample_quotes_text = "\n".join([f'- "{q}"' for q in quotes[:5]])
        llm_prompt = f"""You are an executive PR Crisis Strategist for digital media. Analyze this audience backlash data:
Asset Title: "{title}" on Channel "{channel}"
Comment Velocity Surge: +{velocity:.1f}%
Sample Friction Points / Comments:
{sample_quotes_text}
{cluster_summary}

You MUST respond strictly in valid JSON format with the following keys:
{{
  "severity": "CRITICAL_P1",
  "root_cause": "A precise 1-2 sentence breakdown identifying the root controversy trigger.",
  "containment_stance": "1. [Step 1 Immediate Pinned Action]\\n2. [Step 2 Disclosure Update]\\n3. [Step 3 Ad/Distribution Pause]"
}}
"""
        try:
            raw_response = llm_client.generate(
                prompt=llm_prompt,
                system_instruction=self.system_instruction
            )
            parsed_json = json.loads(raw_response.strip().replace("```json", "").replace("```", "").strip())
            severity = parsed_json.get("severity", "CRITICAL_P1")
            root_cause = parsed_json.get("root_cause", f"Rapid sentiment backlash (+{velocity:.1f}%) on core message transparency.")
            containment_stance = parsed_json.get("containment_stance", (
                "1. Publish verified pinned clarification comment addressing friction points directly.\n"
                "2. Update video description with transparent disclosure timestamps.\n"
                "3. Temporarily pause automated ad placements until sentiment stabilizes."
            ))
        except Exception as e:
            logger.warning(f"[{self.name}] LLM dynamic generation fallback: {e}")
            severity = "CRITICAL_P1"
            root_cause = f"Rapid sentiment backlash (+{velocity:.1f}%) on transparency: '{quotes[0] if quotes else 'Public backlash'}'.{cluster_summary}"
            containment_stance = (
                "1. Publish verified pinned clarification comment addressing friction points directly.\n"
                "2. Update video description with transparent disclosure timestamps.\n"
                "3. Temporarily pause automated ad placements until sentiment stabilizes."
            )

        executed_actions = []

        # Tool 1: Slack Alert
        slack_res = self.execute_tool(
            "dispatch_slack_crisis_alert",
            severity=severity,
            title=title,
            channel_id_or_name=channel,
            root_cause_summary=root_cause,
            sample_negative_quotes=quotes[:3],
            recommended_pr_stance=containment_stance,
            metric_velocity_pct=velocity
        )
        executed_actions.append({"tool": "dispatch_slack_crisis_alert", "result": slack_res})

        # Tool 2: Notion Triage Board
        notion_res = self.execute_tool(
            "generate_notion_action_board",
            title=f"PR Backlash Triage: {title[:35]}...",
            priority="Urgent" if "P1" in severity else "High",
            assigned_team="PR & Crisis Management",
            summary=root_cause,
            action_items=[
                "Draft and approve pinned comment addressing transparency",
                "Review sponsor disclosure guidelines with legal team",
                "Monitor sentiment velocity at 60m interval"
            ]
        )
        executed_actions.append({"tool": "generate_notion_action_board", "result": notion_res})

        logger.info(f"[{self.name}] PR Incident mitigation dispatched successfully (2 actions).")
        return executed_actions

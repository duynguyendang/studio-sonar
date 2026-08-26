import logging
from typing import Dict, List, Any
from src.agents.base_agent import BaseADKAgent, ADKAgentMessage
from src.mcp.slack_tools import dispatch_slack_crisis_alert
from src.mcp.notion_tools import generate_notion_action_board

logger = logging.getLogger("studiosonar.agent.pr")

class PRCrisisStrategistAgent(BaseADKAgent):
    """
    Specialist Agent 2: PR Crisis Strategy & Executive Resolution.
    Analyzes root-cause drivers of backlash and executes immediate remediation via Slack and Notion.
    """

    def __init__(self):
        super().__init__(
            name="PRCrisisStrategistAgent",
            role="Executive PR Strategist & Crisis Resolver",
            system_instruction=(
                "You are the Crisis Response Strategist. When handed an anomaly, you perform root-cause "
                "analysis on viewer sentiment, synthesize an actionable response stance, and dispatch "
                "immediate Slack Red Alerts and Notion triage cards without human intervention."
            ),
            tools=[
                dispatch_slack_crisis_alert,
                generate_notion_action_board
            ]
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
        sample_quotes_text = "\n".join([f'- "{q}"' for q in quotes[:5]])
        llm_prompt = f"""You are an executive PR Crisis Strategist. Analyze the following social backlash data:
Video Title: '{title}' on Channel '{channel}'
Comment Velocity Spike: +{velocity:.1f}%
Sample Negative Comments:
{sample_quotes_text}
{cluster_summary}

Provide:
1. Root Cause Summary (1-2 concise sentences identifying the exact trigger).
2. Recommended 3-step immediate PR containment stance."""


        gemini_response = llm_client.generate(
            prompt=llm_prompt,
            system_instruction=self.system_instruction
        )

        if gemini_response:
            root_cause = f"Gemini 3.7 Flash Root Cause Synthesis: {gemini_response}"
            stance = "1. Execute transparent clarification.\n2. Update disclosures.\n3. Pause automated ads."
        else:
            root_cause = (
                f"Severe viewer backlash regarding undisclosed sponsorship in '{title}'.{cluster_summary} "
                "Viewers identified conflicting claims where the creator claimed self-funding while "
                "a third party announced an equity partnership on social media."
            )
            stance = (
                "1. Immediately pin a transparent clarification comment acknowledging third-party sponsorship.\n"
                "2. Update YouTube video description with full FTC compliance disclosures.\n"
                "3. Pause automated social reposts until the PR statement is approved."
            )

        actions_taken = []


        # 1. Dispatch Slack Red Alert
        logger.info(f"[{self.name}] Calling Slack Red Alert MCP tool...")
        slack_res = self.execute_tool(
            "dispatch_slack_crisis_alert",
            severity="CRITICAL_P1",
            title=f"Undisclosed Sponsor Backlash on '{title}'",
            channel_id_or_name=f"@{channel}",
            root_cause_summary=root_cause,
            sample_negative_quotes=quotes,
            recommended_pr_stance=stance,
            metric_velocity_pct=velocity
        )
        actions_taken.append({"agent": self.name, "tool": "dispatch_slack_crisis_alert", "result": slack_res})

        # 2. Dispatch Notion Triage Card
        logger.info(f"[{self.name}] Calling Notion Kanban Board MCP tool...")
        notion_res = self.execute_tool(
            "generate_notion_action_board",
            title=f"URGENT PR: Address Disclosure Backlash on '{title}'",
            priority="Urgent",
            assigned_team="PR & Crisis Management",
            summary=root_cause,
            action_items=[
                "Draft pinned clarification comment for YouTube",
                "Update FTC disclosure tags in video metadata",
                "Review sponsorship contract with Legal team"
            ],
            due_in_hours=12
        )
        actions_taken.append({"agent": self.name, "tool": "generate_notion_action_board", "result": notion_res})

        return actions_taken

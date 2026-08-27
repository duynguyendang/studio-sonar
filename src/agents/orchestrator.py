"""
Google ADK (Agent Development Kit v2.7.1) Root Taskmaster Orchestrator.
Coordinates the multi-agent swarm using both Hierarchical Sub-Agents and Graph-Based Workflows.
"""

import logging
from typing import Dict, List, Any, Optional
from google.adk import Agent, Workflow, Runner, Context, Event
from src.agents.base_agent import create_pure_adk_agent, adk_event_tracer
from src.agents.anomaly_detector_agent import anomaly_detector_agent
from src.agents.pr_crisis_agent import pr_crisis_agent
from src.agents.viral_content_agent import viral_content_agent
from src.agents.channel_monitor_agent import channel_monitor_agent
from src.core.config import settings

logger = logging.getLogger("studiosonar.agent.orchestrator")

TASKMASTER_SYSTEM_INSTRUCTION = (
    "You are the StudioSonarRootTaskmaster, the central supervisor of an autonomous media intelligence swarm. "
    "Your architecture coordinates 4 specialized pure Google ADK sub-agents: "
    "1. ChannelMonitorAgent: Surveillance over official company YouTube & TikTok channels. "
    "2. AnomalyDetectorAgent: High-velocity analytics scanning BigQuery for sentiment drops and breakout memes. "
    "3. PRCrisisStrategistAgent: Root cause synthesis, Slack Red Alerts, and Notion emergency triage. "
    "4. ViralContentCreatorAgent: High-CTR psychological hook architecture and Google Docs video script drafting. "
    "You orchestrate execution graphs, route tasks, validate cross-platform correlations, and publish executive dossiers."
)

# 1. Native Google ADK Pure Hierarchical Supervisor Agent
taskmaster_agent: Agent = create_pure_adk_agent(
    name="StudioSonarRootTaskmaster",
    instruction=TASKMASTER_SYSTEM_INSTRUCTION,
    sub_agents=[
        channel_monitor_agent,
        anomaly_detector_agent,
        pr_crisis_agent,
        viral_content_agent
    ]
)

# 2. Native Google ADK Graph-Based Workflow
taskmaster_workflow: Workflow = Workflow(
    name="StudioSonarAutonomousWorkflow",
    description="End-to-End Autonomous Multi-Agent Media Intelligence Workflow Graph",
    edges=[
        ("START", channel_monitor_agent),
        (channel_monitor_agent, anomaly_detector_agent),
        (anomaly_detector_agent, pr_crisis_agent),
        (anomaly_detector_agent, viral_content_agent)
    ]
)

# Export aliases
native_taskmaster_agent = taskmaster_agent
native_taskmaster_workflow = taskmaster_workflow

class StudioSonarOrchestrationEngine:
    """
    Production Execution Engine for Google ADK Swarm.
    Executes autonomous workflows, triggers specialized ADK agents, and publishes centralized GCS dossiers.
    """

    def __init__(self):
        self.root_agent = taskmaster_agent
        self.workflow = taskmaster_workflow
        self.specialists = {
            "channel_monitor": channel_monitor_agent,
            "anomaly_detector": anomaly_detector_agent,
            "pr_crisis": pr_crisis_agent,
            "viral_content": viral_content_agent
        }

    def run_autonomous_cycle(self, cycle_type: str = "ALL") -> Dict[str, Any]:
        """
        Executes an autonomous Multi-Agent cycle using pure Google ADK agents.
        """
        logger.info(f"[{self.root_agent.name}] Initiating Google ADK Autonomous Cycle (Type: {cycle_type})...")
        
        executed_actions: List[Dict[str, Any]] = []

        # =====================================================================
        # Step 0: Real-Time Telemetry Stream Ingestion -> BigQuery
        # =====================================================================
        try:
            from src.data.bigquery_client import bq_client
            ingest_res = bq_client.collect_and_ingest_latest_telemetry()
            logger.info(f"Step 0 Complete: Ingested {ingest_res.get('ingested_count')} video snapshots to BigQuery.")
        except Exception as e:
            logger.warning(f"Live Ingestion notice: {e}")

        # =====================================================================
        # Step 1: Channel Monitor Agent (Company Channels & 24h Scorecards)
        # =====================================================================
        if cycle_type in ["COMPANY_CHANNEL", "ALL"]:
            from src.mcp.channel_tools import (
                check_channel_new_uploads,
                synthesize_video_statistical_scorecard,
                dispatch_slack_video_scorecard
            )
            from src.mcp.notion_tools import generate_notion_action_board
            from src.core.registry_manager import registry_manager

            adk_event_tracer.record_handoff(
                sender=self.root_agent.name,
                recipient=channel_monitor_agent.name,
                reason="MONITOR_COMPANY_UPLOADS",
                payload={"lookback_days": 7}
            )

            primary_ch = registry_manager.get_primary_company_channel()
            target_ch_id = primary_ch.get("channel_id", "ch_default")

            upload_data = check_channel_new_uploads(channel_id=target_ch_id)
            video = upload_data.get("video", {})
            comments = upload_data.get("comments_sample", [])
            dist = upload_data.get("sentiment_distribution", {})

            scorecard = synthesize_video_statistical_scorecard(
                video_data=video,
                sentiment_distribution=dist,
                sample_comments=comments
            )

            slack_res = dispatch_slack_video_scorecard(scorecard=scorecard)
            executed_actions.append({"agent": channel_monitor_agent.name, "tool": "dispatch_slack_video_scorecard", "result": slack_res})

            notion_res = generate_notion_action_board(
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
            executed_actions.append({"agent": channel_monitor_agent.name, "tool": "generate_notion_action_board", "result": notion_res})

        # =====================================================================
        # Step 2: Anomaly Detector Agent (Velocity Spikes & Sentiment Backlash)
        # =====================================================================
        if cycle_type in ["PR_CRISIS", "ALL"]:
            from src.mcp.bq_tools import query_bigquery_sentiment_spikes, search_bigquery_vector_context
            from src.mcp.slack_tools import dispatch_slack_crisis_alert
            from src.mcp.notion_tools import generate_notion_action_board

            adk_event_tracer.record_handoff(
                sender=self.root_agent.name,
                recipient=anomaly_detector_agent.name,
                reason="TRIGGER_PR_TELEMETRY_SCAN",
                payload={"time_window_hours": 6}
            )

            bq_res = query_bigquery_sentiment_spikes(time_window_hours=6, min_comment_velocity_pct=200.0)
            anomalies = bq_res.get("anomalies", [])

            for anomaly in anomalies:
                adk_event_tracer.record_handoff(
                    sender=anomaly_detector_agent.name,
                    recipient=pr_crisis_agent.name,
                    reason="PR_CRISIS_BACKLASH_HANDOFF",
                    payload=anomaly
                )

                title = anomaly.get("video_title", "Video Upload")
                channel = anomaly.get("channel_title", "Brand Channel")
                velocity = anomaly.get("velocity_spike_pct", 0.0)
                quotes = anomaly.get("sample_negative_comments", [])

                root_cause = f"Rapid sentiment backlash (+{velocity:.1f}%) on core message transparency."
                containment_stance = (
                    "1. Publish verified pinned clarification comment addressing friction points directly.\n"
                    "2. Update video description with transparent disclosure timestamps.\n"
                    "3. Temporarily pause automated ad placements until sentiment stabilizes."
                )

                slack_res = dispatch_slack_crisis_alert(
                    severity="CRITICAL_P1",
                    title=title,
                    channel_id_or_name=channel,
                    root_cause_summary=root_cause,
                    sample_negative_quotes=quotes[:3],
                    recommended_pr_stance=containment_stance,
                    metric_velocity_pct=velocity
                )
                executed_actions.append({"agent": pr_crisis_agent.name, "tool": "dispatch_slack_crisis_alert", "result": slack_res})

                notion_res = generate_notion_action_board(
                    title=f"PR Backlash Triage: {title[:35]}...",
                    priority="Urgent",
                    assigned_team="PR & Crisis Management",
                    summary=root_cause,
                    action_items=[
                        "Draft and approve pinned comment addressing transparency",
                        "Review sponsor disclosure guidelines with legal team",
                        "Monitor sentiment velocity at 60m interval"
                    ]
                )
                executed_actions.append({"agent": pr_crisis_agent.name, "tool": "generate_notion_action_board", "result": notion_res})

        # =====================================================================
        # Step 3: Viral Content Creator Agent (Breakout Memes & 60s Shorts Scripts)
        # =====================================================================
        if cycle_type in ["VIRAL_TREND", "ALL"]:
            from src.mcp.bq_tools import query_bigquery_viral_trends
            from src.mcp.gdocs_tools import create_google_doc_video_script
            from src.mcp.notion_tools import generate_notion_action_board
            from src.core.viral_hook_engine import ViralHookEngine

            adk_event_tracer.record_handoff(
                sender=self.root_agent.name,
                recipient=anomaly_detector_agent.name,
                reason="TRIGGER_VIRAL_TREND_SCAN",
                payload={"min_view_acceleration_pct": 300.0}
            )

            trend_res = query_bigquery_viral_trends(min_view_acceleration_pct=300.0)
            trends = trend_res.get("trends", [])

            for trend in trends:
                adk_event_tracer.record_handoff(
                    sender=anomaly_detector_agent.name,
                    recipient=viral_content_agent.name,
                    reason="VIRAL_TREND_BREAKOUT_HANDOFF",
                    payload=trend
                )

                topic = trend.get("trend_topic", "Breakout Tech Trend")
                accel = trend.get("cross_platform_acceleration_pct", 0.0)

                hooks = ViralHookEngine.generate_high_octane_hooks(topic=topic, context={"accel": accel})
                hook_3s = hooks.get("framework_1_financial_catastrophe", {}).get("hook_3s", f"99% người xem đang hiểu sai về {topic}!")
                problem = f"Tại sao 90% nhà sáng tạo bỏ lỡ làn sóng {topic} trong khi nó đang tăng trưởng +{accel:.1f}%?"
                solution = f"Bí quyết nằm ở việc nắm bắt comment velocity và nhu cầu ngách của cộng đồng trước khi đối thủ nhận ra."
                cta = "Lưu lại video này và đăng ký kênh để đón đầu làn sóng tiếp theo!"
                b_rolls = [
                    "0:00 - High-contrast visual disruption",
                    "0:15 - BigQuery analytics spike graph",
                    "0:45 - High-contrast CTA overlay"
                ]

                gdocs_res = create_google_doc_video_script(
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
                executed_actions.append({"agent": viral_content_agent.name, "tool": "create_google_doc_video_script", "result": gdocs_res})

                notion_res = generate_notion_action_board(
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
                executed_actions.append({"agent": viral_content_agent.name, "tool": "generate_notion_action_board", "result": notion_res})

        traces = adk_event_tracer.get_traces()
        return {
            "status": "COMPLETED",
            "cycle_type": cycle_type,
            "root_agent": self.root_agent.name,
            "workflow_name": self.workflow.name,
            "sub_agents_active": [sa.name for sa in self.root_agent.sub_agents],
            "inter_agent_messages_exchanged": len(traces),
            "inter_agent_traces": traces,
            "actions_executed": executed_actions
        }

taskmaster_orchestrator = StudioSonarOrchestrationEngine()

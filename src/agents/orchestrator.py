import logging
from typing import Dict, List, Any, Optional
from google.adk import Agent, Workflow, Runner, Context, Event
from src.agents.base_agent import BaseADKAgent, ADKAgentMessage, create_adk_agent
from src.agents.anomaly_detector_agent import AnomalyDetectorAgent, native_anomaly_detector
from src.agents.pr_crisis_agent import PRCrisisStrategistAgent, native_pr_crisis_agent
from src.agents.viral_content_agent import ViralContentCreatorAgent, native_viral_content_agent
from src.agents.channel_monitor_agent import ChannelMonitorAgent, native_channel_monitor_agent
from src.core.config import settings

logger = logging.getLogger("studiosonar.agent.orchestrator")

TASKMASTER_SYSTEM_INSTRUCTION = (
    "You are the Root Taskmaster Orchestrator. You receive Cloud Scheduler triggers, "
    "delegate telemetry scanning to the AnomalyDetectorAgent, route crisis anomalies to the "
    "PRCrisisStrategistAgent, route breakout trends to the ViralContentCreatorAgent, "
    "and direct ChannelMonitorAgent to track company channel uploads and generate statistical scorecards."
)

# 1. Native Google ADK Root Agent
native_taskmaster_agent: Agent = create_adk_agent(
    name="StudioSonarRootTaskmaster",
    instruction=TASKMASTER_SYSTEM_INSTRUCTION,
    tools=[]
)

# 2. Native Google ADK Graph-Based Workflow
# Defines the multi-agent execution topology:
# START ➔ Channel Monitor ➔ Anomaly Detector ➔ [PR Crisis Strategist | Viral Content Creator]
native_taskmaster_workflow: Workflow = Workflow(
    name="StudioSonarAutonomousWorkflow",
    description="End-to-End Autonomous Multi-Agent Media Intelligence Workflow",
    edges=[
        ("START", native_channel_monitor_agent),
        (native_channel_monitor_agent, native_anomaly_detector),
        (native_anomaly_detector, native_pr_crisis_agent),
        (native_anomaly_detector, native_viral_content_agent)
    ]
)

class StudioSonarOrchestrator(BaseADKAgent):
    """
    Root Taskmaster Agent (Google ADK Multi-Agent Team Supervisor & Workflow Coordinator).
    Orchestrates specialized sub-agents, manages inter-agent handoffs, and ensures 24/7 autonomous action.
    """

    def __init__(self):
        super().__init__(
            name="StudioSonarOrchestrator",
            role="Taskmaster Team Supervisor & Chief Orchestrator",
            system_instruction=TASKMASTER_SYSTEM_INSTRUCTION,
            tools=[self.run_autonomous_cycle]
        )
        # Register Specialized Sub-Agents
        self.anomaly_detector = AnomalyDetectorAgent()
        self.pr_strategist = PRCrisisStrategistAgent()
        self.content_creator = ViralContentCreatorAgent()
        self.channel_monitor = ChannelMonitorAgent()
        
        self.agent_team = [
            self.anomaly_detector,
            self.pr_strategist,
            self.content_creator,
            self.channel_monitor
        ]

        # Bind Native ADK Workflow
        self.workflow = native_taskmaster_workflow

    def get_root_adk_agent(self) -> Agent:
        """Returns the native Google ADK Root Agent object for adk CLI & runners."""
        return native_taskmaster_agent

    def get_adk_workflow(self) -> Workflow:
        """Returns the native Google ADK Workflow graph object."""
        return self.workflow

    def run_autonomous_cycle(self, cycle_type: str = "ALL") -> Dict[str, Any]:
        """
        Runs an autonomous Multi-Agent cycle with explicit inter-agent communication logs.
        
        Cycle Types:
        - "ALL": Runs telemetry scans, PR analysis, trend spotter, and company channel monitoring.
        - "PR_CRISIS": Focuses on negative sentiment spikes and brand defense.
        - "VIRAL_TREND": Focuses on breakout meme/hook patterns and Google Docs script authoring.
        - "COMPANY_CHANNEL": Monitors the company's official channel for new uploads & generates stats.
        """
        logger.info(f"[{self.name}] Initiating Multi-Agent Taskmaster Cycle (Type: {cycle_type})...")
        
        inter_agent_traces: List[Dict[str, Any]] = []
        all_actions: List[Dict[str, Any]] = []

        # =====================================================================
        # 0. AUTONOMOUS DATA COLLECTOR JOB (YouTube Live Ingestion -> BigQuery)
        # =====================================================================
        try:
            from src.data.bigquery_client import bq_client
            ingest_res = bq_client.collect_and_ingest_latest_telemetry()
            logger.info(f"[{self.name}] Step 0 Ingestion Complete: {ingest_res.get('ingested_count')} videos streamed to BigQuery.")
        except Exception as e:
            logger.warning(f"[{self.name}] Live Ingestion error: {e}")

        # =====================================================================
        # 1. COMPANY CHANNEL MONITORING & STATISTICAL SCORECARD
        # =====================================================================
        if cycle_type in ["COMPANY_CHANNEL", "ALL"]:
            from src.core.registry_manager import registry_manager
            primary_ch = registry_manager.get_primary_company_channel()
            target_ch_id = primary_ch.get("channel_id", "ch_default")

            trace_msg0 = ADKAgentMessage(
                sender=self.name,
                recipient=self.channel_monitor.name,
                message_type="MONITOR_COMPANY_UPLOADS",
                content={"channel_id": target_ch_id, "lookback_hours": 24}
            )
            self.log_message(trace_msg0)
            inter_agent_traces.append(trace_msg0.to_dict())

            if settings.channel_monitor_url:
                try:
                    import requests
                    logger.info(f"[{self.name}] Dispatching A2A Remote Request to: {settings.channel_monitor_url}/api/v1/a2a/channel-monitor")
                    resp = requests.post(f"{settings.channel_monitor_url}/api/v1/a2a/channel-monitor", json={"channel_id": target_ch_id}, timeout=30)
                    channel_results = resp.json()
                except Exception as e:
                    logger.warning(f"A2A Remote Call failed, falling back to local: {e}")
                    channel_results = self.channel_monitor.monitor_and_synthesize(channel_id=target_ch_id)
            else:
                channel_results = self.channel_monitor.monitor_and_synthesize(channel_id=target_ch_id)

            all_actions.extend(channel_results.get("actions_executed", []))

        # =====================================================================
        # 2. DELEGATION TO ANOMALY DETECTOR AGENT (PR & Trends)
        # =====================================================================
        if cycle_type in ["PR_CRISIS", "VIRAL_TREND", "ALL"]:
            trace_msg1 = ADKAgentMessage(
                sender=self.name,
                recipient=self.anomaly_detector.name,
                message_type="TRIGGER_TELEMETRY_SCAN",
                content={"cycle_type": cycle_type, "lookback_hours": 6}
            )
            self.log_message(trace_msg1)
            inter_agent_traces.append(trace_msg1.to_dict())

        # Branch A: PR Crisis Anomaly Scan & Handoff
        if cycle_type in ["PR_CRISIS", "ALL"]:
            pr_anomalies = self.anomaly_detector.scan_pr_anomalies(time_window_hours=6)
            
            for anomaly in pr_anomalies:
                handoff_msg = ADKAgentMessage(
                    sender=self.anomaly_detector.name,
                    recipient=self.pr_strategist.name,
                    message_type="PR_ANOMALY_HANDOFF",
                    content={
                        "video_id": anomaly.get("video_id"),
                        "velocity_spike_pct": anomaly.get("velocity_spike_pct"),
                        "avg_sentiment": anomaly.get("avg_sentiment")
                    }
                )
                self.log_message(handoff_msg)
                inter_agent_traces.append(handoff_msg.to_dict())

                if settings.pr_strategist_url:
                    try:
                        import requests
                        logger.info(f"[{self.name}] Dispatching A2A Remote Request to: {settings.pr_strategist_url}/api/v1/a2a/pr-strategist")
                        resp = requests.post(f"{settings.pr_strategist_url}/api/v1/a2a/pr-strategist", json={"anomaly_payload": anomaly}, timeout=30)
                        pr_res = resp.json().get("actions_taken", [])
                    except Exception as e:
                        logger.warning(f"A2A Remote Call failed, falling back to local: {e}")
                        pr_res = self.pr_strategist.handle_incident(anomaly)
                else:
                    pr_res = self.pr_strategist.handle_incident(anomaly)

                all_actions.extend(pr_res)

        # Branch B: Viral Breakout Trend Scan & Handoff
        if cycle_type in ["VIRAL_TREND", "ALL"]:
            viral_trends = self.anomaly_detector.scan_viral_trends(min_view_acceleration_pct=300.0)
            
            for trend in viral_trends:
                handoff_msg = ADKAgentMessage(
                    sender=self.anomaly_detector.name,
                    recipient=self.content_creator.name,
                    message_type="VIRAL_TREND_HANDOFF",
                    content={
                        "trend_topic": trend.get("trend_topic"),
                        "cross_platform_acceleration_pct": trend.get("cross_platform_acceleration_pct")
                    }
                )
                self.log_message(handoff_msg)
                inter_agent_traces.append(handoff_msg.to_dict())

                if settings.content_creator_url:
                    try:
                        import requests
                        logger.info(f"[{self.name}] Dispatching A2A Remote Request to: {settings.content_creator_url}/api/v1/a2a/content-creator")
                        resp = requests.post(f"{settings.content_creator_url}/api/v1/a2a/content-creator", json={"trend_payload": trend}, timeout=30)
                        content_res = resp.json().get("actions_taken", [])
                    except Exception as e:
                        logger.warning(f"A2A Remote Call failed, falling back to local: {e}")
                        content_res = self.content_creator.create_viral_script(trend)
                else:
                    content_res = self.content_creator.create_viral_script(trend)

                all_actions.extend(content_res)

        return {
            "status": "COMPLETED",
            "cycle_type": cycle_type,
            "agent_team": [agent.name for agent in self.agent_team],
            "workflow_name": self.workflow.name,
            "inter_agent_messages_exchanged": len(inter_agent_traces),
            "inter_agent_traces": inter_agent_traces,
            "actions_executed": all_actions
        }

taskmaster_orchestrator = StudioSonarOrchestrator()

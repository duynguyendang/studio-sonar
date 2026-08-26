import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from fastapi import APIRouter, BackgroundTasks, HTTPException
from src.agents.orchestrator import taskmaster_orchestrator
from src.tools.video_report_generator import VideoReportGenerator
from src.tools.tiktok_video_analyzer import tiktok_scanner
from src.core.hook_knowledge_base import hook_kb
from src.tools.universal_hook_recommender import hook_recommender
from src.tools.trending_harvester import trending_harvester
from src.agents.settings_copilot_agent import settings_copilot
from src.core.config import settings

router = APIRouter()

class VideoAnalysisRequest(BaseModel):
    video_url_or_id: str = "https://www.youtube.com/watch?v=ye3B8kPuTnc"

class TikTokScanRequest(BaseModel):
    tiktok_url_or_id: str = "https://www.tiktok.com/@ai_creator/video/73918291039"

class HookPrescriptionRequest(BaseModel):
    topic: str = "Trí Tuệ Nhân Tạo & Lập Trình Viên"
    category: str = "Tech & Business"

class ChatCommandRequest(BaseModel):
    message: str

# --- CHAT COPILOT COMMAND ENDPOINT ---

@router.post("/api/v1/chat/command")
def process_chat_command_endpoint(req: ChatCommandRequest) -> Dict[str, Any]:
    """Processes natural language settings commands (e.g. adjust tracking duration, add channel, generate hooks)."""
    return settings_copilot.process_chat_command(req.message)

@router.get("/healthz")
@router.get("/api/v1/health")
def healthcheck_endpoint():
    """Cluster health check and microservice status."""
    return {
        "status": "healthy",
        "service": "studiosonar-taskmaster",
        "architecture": "Google ADK Multi-Agent Team",
        "agents": ["AnomalyDetectorAgent", "PRCrisisStrategistAgent", "ViralContentCreatorAgent", "ChannelSentinelAgent"],
        "model": "gemini-2.5-flash"
    }

from src.tools.realtime_24h_pulse import realtime_pulse_engine


# --- LIVE REPORT SERVING ENDPOINT (Zero-Cache Dynamic Resolution) ---

from src.core.registry_manager import registry_manager
from src.core.gcs_report_manager import gcs_report_manager

@router.get("/api/v1/registry/tracking")
def get_tracking_registry_endpoint() -> Dict[str, Any]:
    """Returns dynamic list of all monitored channels and videos from the central registry."""
    return {
        "status": "SUCCESS",
        "channels": registry_manager.get_all_channels(),
        "videos": registry_manager.get_all_videos()
    }

@router.get("/api/v1/reports/content")
def get_report_content(report_key: str):
    """Fetches real-time markdown report directly from Google Cloud Storage (GCS)."""
    content, source_path = gcs_report_manager.fetch_report(report_key)

    if not content:
        raise HTTPException(status_code=404, detail=f"Report file not found for key: {report_key}")

    return {
        "report_key": report_key,
        "file_path": source_path,
        "markdown_content": content
    }


@router.get("/api/v1/tracking/pulse/24h")
def get_realtime_24h_pulse_telemetry():
    """Returns 4-dimensional live comment classification and surge metrics for the last 24 hours."""
    return realtime_pulse_engine.get_live_24h_telemetry()



# --- HOOK TIPS & TRENDING HARVESTER ENDPOINTS ---



@router.get("/api/v1/hooks/tips")
def get_all_hook_tips() -> Dict[str, Any]:
    """Returns the central library of viral hook formulas harvested across YouTube & TikTok."""
    tips = hook_kb.list_all_hooks()
    return {
        "total_hook_tips": len(tips),
        "hook_tips": tips
    }

@router.post("/api/v1/hooks/prescribe")
def prescribe_hooks_for_topic_endpoint(req: HookPrescriptionRequest) -> Dict[str, Any]:
    """
    Generates high-CTR viral titles, 3s opening hooks, and thumbnail texts
    for ANY given topic or channel using proven psychological formulas.
    """
    prescriptions = hook_recommender.prescribe_hooks_for_topic(topic=req.topic, category=req.category)
    return {
        "topic": req.topic,
        "category": req.category,
        "total_prescriptions": len(prescriptions),
        "prescribed_hooks": prescriptions
    }

@router.post("/api/v1/hooks/harvest-trending")
def harvest_trending_hooks_endpoint() -> Dict[str, Any]:
    """Scans live trending streams across YouTube Shorts and TikTok to discover and save new hook formulas."""
    harvested = trending_harvester.harvest_cross_platform_trending_hooks()
    return {
        "status": "HARVESTED_SUCCESS",
        "newly_harvested_count": len(harvested),
        "harvested_tips": harvested
    }

@router.post("/api/v1/tiktok/scan")
def scan_tiktok_video_endpoint(req: TikTokScanRequest) -> Dict[str, Any]:
    """
    Scans any TikTok video URL, analyzes FYP completion rates,
    Save/Share multipliers, and audio virality drivers.
    """
    return tiktok_scanner.scan_tiktok_video(req.tiktok_url_or_id)



@router.get("/healthz")
def health_check() -> Dict[str, Any]:
    """Health check endpoint for Google Cloud Run container liveness probe."""
    return {
        "status": "healthy",
        "service": "studiosonar-taskmaster",
        "architecture": "Google ADK Multi-Agent Team",
        "agents": [a.name for a in taskmaster_orchestrator.agent_team],
        "model": settings.gemini_model,
        "mode": settings.execution_mode
    }

@router.post("/api/v1/video/quick-report")
def generate_quick_video_report(req: VideoAnalysisRequest) -> Dict[str, Any]:
    """
    Analyzes any YouTube video URL and generates a comprehensive growth diagnosis,
    A/B testing title recommendations, and shortform repurposing scripts.
    """
    report = VideoReportGenerator.generate_full_report(req.video_url_or_id)
    return {
        "status": "SUCCESS",
        "report": report
    }

@router.post("/api/v1/trigger-cycle")
def trigger_scheduled_cycle(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Endpoint triggered by Google Cloud Scheduler / Eventarc.
    Runs a full background analysis and autonomous Multi-Agent cycle across all tracks.
    """
    results = taskmaster_orchestrator.run_autonomous_cycle(cycle_type="ALL")
    return {
        "status": "TRIGGERED_SUCCESS",
        "execution_summary": results
    }

@router.post("/api/v1/simulate/company-channel-upload")
def simulate_company_channel_upload(channel_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Monitors target company channel for newly published uploads and generates
    an executive statistical performance scorecard + Slack/Notion sync.
    """
    results = taskmaster_orchestrator.run_autonomous_cycle(cycle_type="COMPANY_CHANNEL")
    return {
        "scenario": "COMPANY_CHANNEL_MONITORING",
        "results": results
    }

@router.post("/api/v1/simulate/pr-crisis")
def simulate_pr_crisis() -> Dict[str, Any]:
    """Manually triggers an overnight PR crisis Multi-Agent workflow for verification."""
    results = taskmaster_orchestrator.run_autonomous_cycle(cycle_type="PR_CRISIS")
    return {
        "scenario": "PR_CRISIS",
        "results": results
    }

@router.post("/api/v1/simulate/viral-trend")
def simulate_viral_trend() -> Dict[str, Any]:
    """Manually triggers a viral breakout trend Multi-Agent workflow for verification."""
    results = taskmaster_orchestrator.run_autonomous_cycle(cycle_type="VIRAL_TREND")
    return {
        "scenario": "VIRAL_TREND",
        "results": results
    }

# =====================================================================
# INTERACTIVE UI AGENT TRIGGER ENDPOINTS
# =====================================================================

class DirectAgentTriggerRequest(BaseModel):
    report_key: str = "realtime_24h"
    title: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None

@router.post("/api/v1/agents/trigger-viral-content")
def trigger_viral_content_agent_ui(req: DirectAgentTriggerRequest) -> Dict[str, Any]:
    """
    Directly triggers ViralContentCreatorAgent to synthesize a 60s viral video script,
    hook breakdown, Google Doc draft, and Notion Content Sprint task based on current report context.
    """
    topic = req.title or "Viral Breakout Campaign"
    trend_payload = {
        "trend_topic": topic,
        "cross_platform_acceleration_pct": 310.0,
        "report_key": req.report_key,
        "key_hook": "Stop building chatbots in 2026. Here is what real autonomous agents actually do."
    }
    actions = taskmaster_orchestrator.content_creator.handle_breakout_trend(trend_payload)
    
    # Extract script details from GDocs tool result
    gdoc_result = next((a["result"] for a in actions if a["tool"] == "create_google_doc_video_script"), {})
    notion_result = next((a["result"] for a in actions if a["tool"] == "generate_notion_action_board"), {})
    
    return {
        "status": "SUCCESS",
        "agent": "ViralContentCreatorAgent",
        "role": "High-CTR Viral Content Specialist & Retention Architect",
        "topic": topic,
        "script": {
            "hook_3s": gdoc_result.get("hook_3s", "Stop building chatbots in 2026. Here is what real autonomous agents actually do."),
            "problem": gdoc_result.get("problem_statement", "Everyone is suffering from chatbot fatigue."),
            "solution": gdoc_result.get("solution_core", "Real Taskmasters run 24/7 in the background on Google Cloud."),
            "call_to_action": gdoc_result.get("call_to_action", "Follow StudioSonar for the full architecture blueprint."),
            "broll_notes": gdoc_result.get("visual_broll_notes", [
                "0:00 - Rapid cuts of frustrated user typing prompts into basic chat UI",
                "0:15 - Screen recording of BigQuery live SQL stream and Slack red alert auto-firing",
                "0:45 - High-tech architecture diagram showing Google ADK + Cloud Run"
            ]),
            "doc_url": gdoc_result.get("doc_url", "https://docs.google.com/document/d/studiosonar-viral-script-draft"),
            "notion_task": notion_result.get("board_title", f"Content Sprint: Produce '{topic}' Shortform Video")
        },
        "actions_executed": actions
    }

@router.post("/api/v1/agents/trigger-crisis-strategy")
def trigger_crisis_strategy_agent_ui(req: DirectAgentTriggerRequest) -> Dict[str, Any]:
    """
    Directly triggers PRCrisisStrategistAgent to perform root-cause sentiment analysis,
    generate 3-step containment stance, Slack Red Alert, and Notion Triage board.
    """
    title = req.title or "Monitored Brand Asset"
    anomaly_payload = {
        "channel_title": "StudioSonar Brand Channel",
        "video_title": title,
        "velocity_spike_pct": 145.0,
        "sample_negative_comments": [
            "Why was this sponsorship not clearly disclosed in the first 30 seconds?",
            "Conflicting claims between self-funded claim and partner press release.",
            "Please clarify the data privacy policy regarding user telemetry tracking."
        ],
        "vector_clusters": [{"matched_topic": "Sponsorship Transparency & Compliance"}]
    }
    actions = taskmaster_orchestrator.pr_strategist.handle_incident(anomaly_payload)
    
    slack_result = next((a["result"] for a in actions if a["tool"] == "dispatch_slack_crisis_alert"), {})
    notion_result = next((a["result"] for a in actions if a["tool"] == "generate_notion_action_board"), {})
    
    return {
        "status": "SUCCESS",
        "agent": "PRCrisisStrategistAgent",
        "role": "Executive PR Strategist & Crisis Resolver",
        "title": title,
        "crisis_plan": {
            "severity": "CRITICAL_P1",
            "root_cause": slack_result.get("root_cause", "Viewer backlash regarding disclosure timing and partner claims."),
            "containment_stance": slack_result.get("recommended_stance", "1. Pin transparent clarification comment.\n2. Update video description with full disclosures.\n3. Pause automated social reposts."),
            "slack_dispatched_channel": slack_result.get("slack_channel", "#war-room-alerts"),
            "notion_triage_board": notion_result.get("board_title", f"URGENT PR: Containment Plan for '{title}'")
        },
        "actions_executed": actions
    }


# =====================================================================
# DISTRIBUTED GOOGLE ADK A2A (AGENT-TO-AGENT) MICROSERVICE ENDPOINTS
# =====================================================================

@router.post("/api/v1/a2a/channel-monitor")
def a2a_channel_monitor_endpoint(payload: Dict[str, Any] = {}) -> Dict[str, Any]:
    """Dedicated Google ADK Endpoint for ChannelMonitorAgent."""
    primary_ch = registry_manager.get_primary_company_channel()
    channel_id = payload.get("channel_id") or primary_ch.get("channel_id", "ch_default")
    return taskmaster_orchestrator.channel_monitor.monitor_and_synthesize(channel_id=channel_id)


@router.post("/api/v1/a2a/anomaly-detector")
def a2a_anomaly_detector_endpoint(payload: Dict[str, Any] = {}) -> Dict[str, Any]:
    """Dedicated Google ADK Endpoint for AnomalyDetectorAgent."""
    return taskmaster_orchestrator.anomaly_detector.scan_for_anomalies()

@router.post("/api/v1/a2a/pr-strategist")
def a2a_pr_strategist_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Dedicated Google ADK Endpoint for PRCrisisStrategistAgent."""
    anomaly_payload = payload.get("anomaly_payload", payload)
    actions = taskmaster_orchestrator.pr_strategist.handle_incident(anomaly_payload)
    return {"status": "SUCCESS", "actions_taken": actions}

@router.post("/api/v1/a2a/content-creator")
def a2a_content_creator_endpoint(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Dedicated Google ADK Endpoint for ViralContentCreatorAgent."""
    trend_payload = payload.get("trend_payload", payload)
    actions = taskmaster_orchestrator.content_creator.handle_breakout_trend(trend_payload)
    return {"status": "SUCCESS", "actions_taken": actions}



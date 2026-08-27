import logging
from typing import Dict, List, Any, Optional
import requests
from src.core.config import settings

logger = logging.getLogger("studiosonar.mcp.slack")

def dispatch_slack_crisis_alert(
    severity: str,
    title: str,
    channel_id_or_name: str,
    root_cause_summary: str,
    sample_negative_quotes: List[str],
    recommended_pr_stance: str,
    metric_velocity_pct: float
) -> Dict[str, Any]:
    """
    Dispatches a high-urgency PR crisis alert to the enterprise Slack #pr-crisis channel.
    
    Args:
        severity: Severity level (e.g., "CRITICAL_P1", "HIGH_P2", "MEDIUM_P3").
        title: Short title of the incident.
        channel_id_or_name: Target channel or account (e.g. "@business" or "@KiemDinhPhim9.0").
        root_cause_summary: Concise explanation of why the backlash is happening.
        sample_negative_quotes: Verbatim representative quotes from user comments.
        recommended_pr_stance: Concrete strategic recommendation for the PR/Executive team.
        metric_velocity_pct: Percentage velocity increase of negative commentary.
        
    Returns:
        Dictionary with dispatch status and delivered message payload.
    """
    severity_emoji = "🚨 [RED ALERT P1]" if "P1" in severity else "⚠️ [ELEVATED P2]"
    
    # Slack Block Kit Payload
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{severity_emoji} StudioSonar PR Incident Alert",
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Severity:*\n`{severity}`"},
                {"type": "mrkdwn", "text": f"*Velocity Spike:*\n`+{metric_velocity_pct:.1f}% / baseline`"},
                {"type": "mrkdwn", "text": f"*Target Property:*\n{channel_id_or_name}"},
                {"type": "mrkdwn", "text": f"*Incident Topic:*\n*{title}*"}
            ]
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🔎 Root Cause Summary:*\n{root_cause_summary}"
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*💬 Evidence Snippets (Direct from BigQuery Telemetry):*\n" + "\n".join([f"> • \"{q}\"" for q in sample_negative_quotes[:4]])
            }
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*🛡️ Recommended Immediate Action:*\n{recommended_pr_stance}"
            }
        }
    ]

    payload = {
        "text": f"{severity_emoji} StudioSonar PR Incident: {title}",
        "blocks": blocks
    }

    if settings.execution_mode == "live" and settings.slack_webhook_url:
        try:
            resp = requests.post(settings.slack_webhook_url, json=payload, timeout=5)
            if resp.status_code == 200:
                logger.info("Successfully delivered crisis alert to live Slack webhook.")
                return {"status": "DELIVERED_LIVE", "channel": "#pr-crisis", "payload": payload}
            else:
                logger.error(f"Slack webhook returned status {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.error(f"Failed to post to Slack webhook: {e}")

    # Simulated Delivery for Test/Demo
    return {
        "status": "DELIVERED_SIMULATED",
        "destination": "Slack Channel: #pr-crisis-red-alert",
        "severity": severity,
        "delivered_payload": payload
    }

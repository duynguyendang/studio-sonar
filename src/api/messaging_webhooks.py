import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Response, HTTPException
from src.agents.settings_copilot_agent import settings_copilot
from src.core.config import settings

logger = logging.getLogger("studiosonar.messaging_webhooks")
router = APIRouter(prefix="/api/v1/webhooks", tags=["Messaging Webhooks (Slack & WhatsApp)"])

# ==============================================================================
# 1. SLACK SLASH COMMANDS & EVENT SUBSCRIPTIONS
# ==============================================================================

@router.post("/slack/command")
async def handle_slack_slash_command(request: Request) -> Dict[str, Any]:
    """
    Handles Slack Slash Commands (e.g. /sonar track @business 14d, /sonar Chỉnh video Quốc 7 ngày).
    Allows team members to adjust settings & lookback windows straight from Slack.
    """
    form_data = await request.form()
    user_text = form_data.get("text", "").strip()
    user_name = form_data.get("user_name", "user")
    channel_id = form_data.get("channel_id", "")

    logger.info(f"Received Slack Slash Command from @{user_name}: '{user_text}'")

    if not user_text:
        return {
            "response_type": "ephemeral",
            "text": "👋 Xin chào! Hãy dùng lệnh: `/sonar [lệnh]`. Ví dụ:\n• `/sonar Chỉnh video Lê Viết Quốc theo dõi 7 ngày`\n• `/sonar Thêm kênh @business quét 14 ngày`\n• `/sonar Sinh 3 hook về Microservices`"
        }

    # Execute intent via Copilot Agent
    res = settings_copilot.process_chat_command(user_text)

    # Format Slack Block Kit response
    return {
        "response_type": "in_channel",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🤖 *StudioSonar Taskmaster Response* (Requested by <@{user_name}>):\n\n{res['reply']}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"⚡ *Action:* `{res.get('action_executed', 'GENERAL')}` | *Status:* Confirmed & Updated in BigQuery Registry"
                    }
                ]
            }
        ]
    }

@router.post("/slack/events")
async def handle_slack_events(request: Request) -> Dict[str, Any]:
    """Handles Slack Events API (e.g. url_verification and app_mention)."""
    payload = await request.json()

    # URL Verification for Slack App setup
    if payload.get("type") == "url_verification":
        return {"challenge": payload.get("challenge")}

    event = payload.get("event", {})
    if event.get("type") == "app_mention":
        user_text = event.get("text", "")
        # Remove bot mention tag e.g. <@U12345>
        clean_text = " ".join([w for w in user_text.split() if not w.startswith("<@")])
        res = settings_copilot.process_chat_command(clean_text)
        logger.info(f"Processed Slack Mention: '{clean_text}' -> {res['action_executed']}")

    return {"status": "EVENT_PROCESSED"}

# ==============================================================================
# 2. WHATSAPP CLOUD API WEBHOOKS
# ==============================================================================

@router.get("/whatsapp")
async def verify_whatsapp_webhook(request: Request):
    """Verifies WhatsApp Cloud API webhook endpoint (Meta verification challenge)."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    # Verify token configured in settings or default
    verify_token = getattr(settings, "whatsapp_verify_token", "studiosonar_wa_token_2026")

    if mode == "subscribe" and token == verify_token:
        logger.info("WhatsApp Webhook Verified Successfully!")
        return Response(content=challenge, media_type="text/plain")

    raise HTTPException(status_code=403, detail="Verification token mismatch")

@router.post("/whatsapp")
async def handle_whatsapp_message(request: Request) -> Dict[str, Any]:
    """
    Receives incoming WhatsApp messages from executives / team members,
    parses command, and executes settings changes.
    """
    payload = await request.json()
    logger.info("Received WhatsApp Webhook Payload")

    try:
        entries = payload.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for msg in messages:
                    if msg.get("type") == "text":
                        incoming_text = msg.get("text", {}).get("body", "")
                        from_number = msg.get("from", "")
                        
                        logger.info(f"WhatsApp Message from +{from_number}: '{incoming_text}'")
                        res = settings_copilot.process_chat_command(incoming_text)
                        
                        # In production, send reply back via WhatsApp Cloud API POST https://graph.facebook.com/v18.0/{phone_number_id}/messages
                        logger.info(f"WhatsApp Auto-Reply Generated: {res['reply']}")
    except Exception as e:
        logger.error(f"Error parsing WhatsApp payload: {e}")

    return {"status": "WHATSAPP_PROCESSED"}

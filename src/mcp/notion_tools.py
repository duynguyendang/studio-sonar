import logging
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
import requests
from src.core.config import settings

logger = logging.getLogger("studiosonar.mcp.notion")

def generate_notion_action_board(
    title: str,
    priority: str,
    assigned_team: str,
    summary: str,
    action_items: List[str],
    due_in_hours: int = 24,
    reference_link: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates a prioritized action card on the production/PR team's Notion workspace.
    
    Args:
        title: Title of the task card.
        priority: Priority level ("Urgent", "High", "Medium", "Normal").
        assigned_team: Department or team assigned ("PR & Crisis Management", "Creative Studio").
        summary: Contextual summary of why this task was automatically generated.
        action_items: Concrete checklist of action items for the team to complete.
        due_in_hours: Due date calculated in hours from now.
        reference_link: Optional URL to associated Google Doc or video source.
        
    Returns:
        Dictionary with Notion card creation status, card ID, and direct URL.
    """
    due_date = (datetime.now(timezone.utc) + timedelta(hours=due_in_hours)).strftime("%Y-%m-%d")
    card_id = f"notion_card_{uuid.uuid4().hex[:8]}"
    card_url = f"https://notion.so/studiosonar-workspace/{card_id}"

    card_data = {
        "card_id": card_id,
        "title": title,
        "priority": priority,
        "assigned_team": assigned_team,
        "due_date": due_date,
        "status": "In Progress / Automated Action",
        "summary": summary,
        "action_checklist": action_items,
        "reference_link": reference_link or "N/A"
    }

    if settings.execution_mode == "live" and settings.notion_api_key and settings.notion_database_id:
        try:
            headers = {
                "Authorization": f"Bearer {settings.notion_api_key}",
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }
            body = {
                "parent": {"database_id": settings.notion_database_id},
                "properties": {
                    "Name": {"title": [{"text": {"content": title}}]},
                    "Priority": {"select": {"name": priority}},
                    "Team": {"select": {"name": assigned_team}},
                    "Status": {"status": {"name": "In Progress"}}
                }
            }
            resp = requests.post("https://api.notion.com/v1/pages", headers=headers, json=body, timeout=5)
            if resp.status_code in [200, 201]:
                live_data = resp.json()
                logger.info(f"Successfully created live Notion page: {live_data.get('url')}")
                return {
                    "status": "CREATED_LIVE",
                    "notion_page_id": live_data.get("id"),
                    "notion_url": live_data.get("url"),
                    "card_data": card_data
                }
        except Exception as e:
            logger.error(f"Failed to create live Notion page: {e}")

    # Simulated Delivery for Test/Demo
    return {
        "status": "CREATED_SIMULATED",
        "notion_card_id": card_id,
        "notion_url": card_url,
        "card_data": card_data
    }

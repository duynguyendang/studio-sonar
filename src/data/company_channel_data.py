from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

def get_company_channel_new_video_scenario() -> Dict[str, Any]:
    """
    Simulates a newly published product launch video on the company's official channel
    and rich audience telemetry for automated statistical scorecard generation.
    """
    now = datetime.now(timezone.utc)
    
    new_video = {
        "video_id": "yt_company_launch_2026",
        "platform": "youtube",
        "channel_id": "UC_Company_Official_2026",
        "channel_title": "Acme AI Corp (Official)",
        "title": "Introducing Acme AgentStudio 2.0: Build Background Taskmasters in Minutes",
        "description": "Watch our CEO explain how Acme AgentStudio 2.0 connects BigQuery and Gemini 3.7 Flash for automated enterprise workflows.",
        "published_at": (now - timedelta(hours=3, minutes=30)).isoformat(), # Published 3.5 hours ago
        "ingested_at": now.isoformat(),
        "duration_sec": 480, # 8 minutes
        "view_count": 42500,
        "like_count": 3890,
        "comment_count": 612,
        "historical_channel_baseline_views_3h": 12000, # Normal 3h view baseline
        "view_acceleration_vs_baseline_pct": 254.1, # 2.5x above channel baseline
        "transcript_summary": (
            "In this keynote demo, we introduce AgentStudio 2.0 with native Google Cloud integration, "
            "ClickHouse/BigQuery real-time analytics, and zero-prompt background execution."
        )
    }

    sample_comments = [
        {"text": "The zero-prompt background architecture is exactly what we needed for our marketing team!", "sentiment": 0.92, "category": "feature_praise"},
        {"text": "Is there a free tier for developers to test BigQuery vector search with Gemini 3.7 Flash?", "sentiment": 0.35, "category": "pricing_inquiry"},
        {"text": "Great demo! How does it handle YouTube API quota limits in high-throughput mode?", "sentiment": 0.40, "category": "technical_question"},
        {"text": "Finally someone addressing chatbot fatigue instead of building another wrapper.", "sentiment": 0.88, "category": "market_alignment"},
        {"text": "The UI looks super clean. Excited to migrate our workflows from Zapier.", "sentiment": 0.85, "category": "feature_praise"},
        {"text": "Please provide a Python SDK tutorial for custom MCP tool integration.", "sentiment": 0.50, "category": "tutorial_request"}
    ]

    return {
        "channel_name": "Acme AI Corp (Official)",
        "video": new_video,
        "comments_sample": sample_comments,
        "sentiment_distribution": {
            "positive_pct": 82.5,
            "neutral_inquiries_pct": 14.2,
            "negative_pct": 3.3
        }
    }

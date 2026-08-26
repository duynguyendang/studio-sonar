import hashlib
import random
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any

class MockStreamGenerator:
    """Generates realistic media telemetry, video transcripts, and comments."""

    @staticmethod
    def get_pr_crisis_scenario() -> Dict[str, Any]:
        """Simulates an overnight PR crisis breakout on YouTube and TikTok."""
        now = datetime.now(timezone.utc)
        
        video = {
            "video_id": "yt_vid_crisis_9021",
            "platform": "youtube",
            "channel_id": "UC_TechVision_Global",
            "channel_title": "TechVision Media",
            "title": "Why We Switched Everything to QuantumCloud (Full Review)",
            "description": "An in-depth review of our studio's infrastructure migration.",
            "transcript": (
                "Hey everyone, today we are breaking down our entire studio stack and why QuantumCloud "
                "is the only solution we trust for our enterprise storage. We tested it for 6 months..."
            ),
            "view_count": 482000,
            "like_count": 8200,
            "comment_count": 1420,
            "published_at": (now - timedelta(hours=14)).isoformat(),
            "ingested_at": now.isoformat(),
            "view_velocity_pct": 340.0,
            "topic_tags": ["cloud", "tech-review", "infrastructure"]
        }

        # Simulated toxic/angry comments with sudden velocity spike
        toxic_comments = [
            "Wait, you said you paid for this yourself, but QuantumCloud just posted on LinkedIn that you are an angel investor? Disclose your sponsors!",
            "Completely undisclosed paid promotion. The benchmarks in this video are totally fabricated compared to independent tests.",
            "Unsubscribing immediately. You used to be the only honest tech channel left on YouTube.",
            "Did anyone else notice the small print at 14:02? It literally says 'sponsored partnership' after claiming it wasn't sponsored in the intro.",
            "This feels super deceptive. Losing all trust in TechVision after 5 years of watching.",
            "Major FTC disclosure violation right here. Already reported.",
            "I spent $2,000 on QuantumCloud based on your recommendation last week and it crashed our production database!",
            "The comments calling out the conflict of interest are getting deleted! Shady behavior."
        ]

        comments = []
        for i, text in enumerate(toxic_comments * 4): # Repeat to simulate volume
            comments.append({
                "comment_id": f"cmt_crisis_{i+1:04d}",
                "video_id": video["video_id"],
                "platform": "youtube",
                "author_id_hash": hashlib.sha256(f"user_{i}".encode()).hexdigest()[:16],
                "comment_text": text,
                "sentiment_score": round(random.uniform(-0.95, -0.65), 3),
                "toxicity_score": round(random.uniform(0.70, 0.95), 3),
                "like_count": random.randint(15, 380),
                "published_at": (now - timedelta(minutes=random.randint(5, 180))).isoformat(),
                "ingested_at": now.isoformat()
            })

        return {
            "scenario": "PR_CRISIS",
            "video": video,
            "comments": comments,
            "metrics": {
                "negative_comment_velocity_pct": 380.0,
                "average_sentiment": -0.82,
                "p95_toxicity": 0.88,
                "spike_window_hours": 6
            }
        }

    @staticmethod
    def get_viral_trend_scenario() -> Dict[str, Any]:
        """Simulates a breakout viral shortform trend across TikTok and YouTube Shorts."""
        now = datetime.now(timezone.utc)
        
        videos = [
            {
                "video_id": "tt_trend_viral_5521",
                "platform": "tiktok",
                "channel_id": "creator_ai_future",
                "channel_title": "AI Builders Club",
                "title": "Stop building chatbots in 2026. Here is why Taskmaster agents are taking over.",
                "description": "Chatbots are dead. Background autonomous Taskmasters are the future. #agentic #ai #coding",
                "transcript": (
                    "If you are still building passive chatbots in 2026, you are already obsolete. "
                    "The real breakthrough is autonomous Taskmasters. They don't wait for your prompt; "
                    "they watch your data 24/7 and write your code and PR alerts while you sleep."
                ),
                "view_count": 890000,
                "like_count": 94000,
                "comment_count": 3100,
                "published_at": (now - timedelta(hours=8)).isoformat(),
                "ingested_at": now.isoformat(),
                "view_velocity_pct": 420.0,
                "topic_tags": ["ai-agents", "taskmaster", "future-tech", "productivity"]
            },
            {
                "video_id": "yt_shorts_viral_7719",
                "platform": "youtube",
                "channel_id": "UC_SiliconValley_Daily",
                "channel_title": "Silicon Valley Daily",
                "title": "The End of Chatbot Fatigue: Autonomous Taskmasters Explained in 45s",
                "description": "Why enterprises are firing chatbots and hiring 24/7 background AI taskmasters.",
                "transcript": (
                    "Ever felt chatbot fatigue? Typing the same prompt over and over? "
                    "Autonomous taskmaster agents connect BigQuery to Slack and execute your chores automatically."
                ),
                "view_count": 650000,
                "like_count": 52000,
                "comment_count": 1800,
                "published_at": (now - timedelta(hours=6)).isoformat(),
                "ingested_at": now.isoformat(),
                "view_velocity_pct": 360.0,
                "topic_tags": ["taskmaster", "ai-agents", "automation"]
            }
        ]

        positive_comments = [
            "This hook is 100% true! Chatbots are so exhausting to prompt manually every day.",
            "Can someone drop a tutorial on building background agents on GCP?",
            "The concept of Taskmasters taking real actions in Slack/Docs instead of just talking is insane.",
            "Where can I learn more about this architecture?",
            "Our agency needs this immediately. We spend 20 hours a week manually copy-pasting reports."
        ]

        return {
            "scenario": "VIRAL_TREND",
            "videos": videos,
            "positive_comments": positive_comments,
            "metrics": {
                "trend_keyword": "Autonomous Taskmaster Agents vs Passive Chatbots",
                "cross_platform_view_acceleration_pct": 390.0,
                "average_sentiment": 0.86,
                "retention_hook_pattern": "Contrarian hook ('Stop doing X in 2026') -> 3s Proof -> 30s Architecture Demo -> CTA",
                "lookback_hours": 8
            }
        }

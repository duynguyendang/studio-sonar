import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from src.models.tracking_models import (
    TrackedChannel,
    TrackedVideo,
    ChannelSnapshot,
    VideoMetricSnapshot
)
from src.tools.youtube_video_analyzer import extract_youtube_id, analyze_youtube_video_target
from src.tools.video_report_generator import VideoReportGenerator

STORAGE_FILE = "src/data/tracking_registry.json"

class TrackingManagerService:
    """Core Service for Managing Real-Time Tracking of Channels and Individual Videos."""

    def __init__(self):
        self.channels: Dict[str, TrackedChannel] = {}
        self.videos: Dict[str, TrackedVideo] = {}
        self._load_storage()
        if not self.channels and not self.videos:
            self._seed_default_tracked_entities()

    def _load_storage(self):
        """Loads registered channels and videos from persistent JSON store."""
        if os.path.exists(STORAGE_FILE):
            try:
                with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for c in data.get("channels", []):
                        self.channels[c["channel_id"]] = TrackedChannel(**c)
                    for v in data.get("videos", []):
                        self.videos[v["video_id"]] = TrackedVideo(**v)
            except Exception as e:
                pass

    def _save_storage(self):
        """Persists tracking registry to disk."""
        os.makedirs(os.path.dirname(STORAGE_FILE), exist_ok=True)
        data = {
            "channels": [c.model_dump() for c in self.channels.values()],
            "videos": [v.model_dump() for v in self.videos.values()]
        }
        with open(STORAGE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _seed_default_tracked_entities(self):
        """Seeds initial target channels and videos analyzed in the project."""
        # 1. Seed Channels
        # Pre-seed target channels with industry-specific tailored taxonomies
        self.channels["ch_business"] = TrackedChannel(
            channel_id="ch_business",
            handle="@business",
            platform="youtube",
            title="Bloomberg Originals",
            category="Global Business & Documentaries",
            tracking_status="ACTIVE",
            check_frequency_minutes=15,
            video_lookback_days=30,
            custom_sentiment_categories=["Macroeconomic Debates", "Data & Source Requests", "Contrarian Perspectives", "Editorial Praise"],
            notification_channel="#media-alerts",
            snapshots=[ChannelSnapshot(subscriber_count=3400000, total_video_count=1850, average_views_per_video=650000.0)]
        )

        self.channels["ch_kiemdinhphim90"] = TrackedChannel(
            channel_id="ch_kiemdinhphim90",
            handle="@KiemDinhPhim9.0",
            platform="youtube",
            title="Kiểm Định Phim 9.0",
            category="Film Criticism & Satire",
            tracking_status="ACTIVE",
            check_frequency_minutes=15,
            video_lookback_days=30,
            custom_sentiment_categories=["Comedic Roasting Praise", "Actor & Drama Defense", "Next Episode Suggestions", "Awards Voting"],
            notification_channel="#media-alerts",
            snapshots=[ChannelSnapshot(subscriber_count=48400, total_video_count=65, average_views_per_video=55000.0)]
        )

        self.channels["ch_thochupanhdalat"] = TrackedChannel(
            channel_id="ch_thochupanhdalat",
            handle="@thochupanh.dalat",
            platform="tiktok",
            title="Thợ Chụp Ảnh Đà Lạt",
            category="Travel & Photography",
            tracking_status="ACTIVE",
            check_frequency_minutes=15,
            video_lookback_days=30,
            custom_sentiment_categories=["Direct Booking & Pricing", "Aesthetic & Photo Praise", "Location Inquiries", "Service Feedback"],
            notification_channel="#media-alerts",
            snapshots=[ChannelSnapshot(subscriber_count=85000, total_video_count=120, average_views_per_video=210000.0)]
        )

        self.channels["ch_google"] = TrackedChannel(
            channel_id="ch_google",
            handle="@Google",
            platform="youtube",
            title="Google",
            category="Global Tech & AI Innovation",
            tracking_status="ACTIVE",
            check_frequency_minutes=15,
            video_lookback_days=30,
            custom_sentiment_categories=["AI Innovation & Gemini", "Android & Pixel Ecosystem", "Developer Tools & Cloud", "Product Feedback & Critique"],
            notification_channel="#media-alerts",
            snapshots=[ChannelSnapshot(subscriber_count=11500000, total_video_count=3200, average_views_per_video=450000.0)]
        )

        self.channels["ch_theverge"] = TrackedChannel(
            channel_id="ch_theverge",
            handle="@TheVerge",
            platform="youtube",
            title="The Verge",
            category="Tech Journalism & Consumer Tech Reviews",
            tracking_status="ACTIVE",
            check_frequency_minutes=15,
            video_lookback_days=30,
            custom_sentiment_categories=["Product Reviews & Gadgets", "Tech Policy & Editorial", "Reviewer Authenticity", "Design & Hardware Critique"],
            notification_channel="#media-alerts",
            snapshots=[ChannelSnapshot(subscriber_count=3400000, total_video_count=4500, average_views_per_video=280000.0)]
        )

        # Pre-seed target priority videos
        self.videos["ye3B8kPuTnc"] = TrackedVideo(
            video_id="ye3B8kPuTnc",
            channel_id="ch_momentum",
            url="https://www.youtube.com/watch?v=ye3B8kPuTnc",
            title="Dr. Luong Minh Thang: From Google Translate to the Superhuman AI Race | Momentum EP7",
            published_at="2026-08-20T10:00:00Z",
            tracking_duration_days=30,
            custom_sentiment_categories=["National Pride & Inspiration", "Luong Attention & AlphaProof Inquiries", "Scholarship & Mentorship", "Audio & Pacing Feedback"],
            monitoring_tier="HIGH_PRIORITY_24H",
            tracking_status="ACTIVE",
            generated_report_path="reports/video_report_ye3B8kPuTnc.md",
            snapshots=[
                VideoMetricSnapshot(
                    hours_since_publish=18.5,
                    views=58400,
                    likes=4200,
                    comments=386,
                    velocity_views_per_hour=312.5,
                    sentiment_positive_pct=96.8,
                    sentiment_negative_pct=0.4
                )
            ]
        )

        self.videos["kqBKKSV50es"] = TrackedVideo(
            video_id="kqBKKSV50es",
            channel_id="ch_momentum",
            url="https://www.youtube.com/watch?v=kqBKKSV50es",
            title="Từ SCIENTIST đến INNOVATOR: Google tạo bệ phóng để TS. Lê Viết Quốc đi xa thế nào? | MOMENTUM EP05",
            published_at="2026-08-22T10:00:00Z",
            tracking_duration_days=30,
            custom_sentiment_categories=["Reverence for Scientific Humility", "Seq2Seq & Neural Architecture Inquiries", "Startup Founder Collaboration", "Title Packaging Feedback"],
            monitoring_tier="HIGH_PRIORITY_24H",
            tracking_status="ACTIVE",
            generated_report_path="reports/video_report_kqBKKSV50es.md",
            snapshots=[
                VideoMetricSnapshot(
                    hours_since_publish=24.0,
                    views=10317,
                    likes=680,
                    comments=192,
                    velocity_views_per_hour=85.0,
                    sentiment_positive_pct=98.2,
                    sentiment_negative_pct=0.2
                )
            ]
        )
        self._save_storage()

    # --- CHANNEL MANAGEMENT ---
    def add_channel(self, handle_or_url: str, category: str = "General", video_lookback_days: int = 30, custom_sentiment_categories: Optional[List[str]] = None, notification_channel: str = "#media-alerts") -> TrackedChannel:
        """Registers a new channel for on-demand 30-day telemetry monitoring with custom sentiment taxonomy."""
        clean_handle = handle_or_url.strip().replace("https://www.youtube.com/", "").replace("https://youtube.com/", "")
        if not clean_handle.startswith("@") and not clean_handle.startswith("ch_"):
            clean_handle = f"@{clean_handle}"
        
        channel_id = f"ch_{re.sub(r'[^a-zA-Z0-9_]', '', clean_handle).lower()}"
        
        categories = custom_sentiment_categories or ["Praise & Loyalty", "Technical Inquiries", "Commercial Leads", "Complaints & Friction"]

        channel = TrackedChannel(
            channel_id=channel_id,
            handle=clean_handle,
            title=f"Channel {clean_handle}",
            category=category,
            tracking_status="ACTIVE",
            check_frequency_minutes=15,
            video_lookback_days=video_lookback_days,
            custom_sentiment_categories=categories,
            notification_channel=notification_channel,
            snapshots=[ChannelSnapshot(subscriber_count=0, total_video_count=0, average_views_per_video=0.0)]
        )
        self.channels[channel_id] = channel
        self._save_storage()
        return channel

    def update_channel_sentiment_categories(self, channel_id: str, new_categories: List[str]) -> Optional[TrackedChannel]:
        """Updates the custom sentiment/intent taxonomy dimensions for a specific channel."""
        if channel_id in self.channels:
            self.channels[channel_id].custom_sentiment_categories = new_categories
            self._save_storage()
            return self.channels[channel_id]
        return None

    def list_channels(self) -> List[TrackedChannel]:
        """Returns all registered channels."""
        return list(self.channels.values())

    def remove_channel(self, channel_id: str) -> bool:
        """Deletes a channel from tracking."""
        if channel_id in self.channels:
            del self.channels[channel_id]
            self._save_storage()
            return True
        return False

    # --- VIDEO MANAGEMENT ---
    def add_video(self, video_url_or_id: str, tracking_duration_days: int = 30, monitoring_tier: str = "HIGH_PRIORITY_24H") -> TrackedVideo:
        """Registers an individual video URL for custom lookback tracking."""
        video_id = extract_youtube_id(video_url_or_id)
        
        # Analyze and generate initial report
        report = VideoReportGenerator.generate_full_report(video_url_or_id)
        raw_meta = report["raw_metadata"]

        video = TrackedVideo(
            video_id=video_id,
            channel_id=f"ch_{raw_meta.get('channel_title', 'unknown').lower().replace(' ', '_')}",
            url=f"https://www.youtube.com/watch?v={video_id}",
            title=raw_meta.get("title", f"Video {video_id}"),
            published_at=raw_meta.get("published_at", datetime.now(timezone.utc).isoformat()),
            tracking_duration_days=tracking_duration_days,
            monitoring_tier=monitoring_tier,
            tracking_status="ACTIVE",
            generated_report_path=report.get("report_file_path"),
            last_analyzed_at=datetime.now(timezone.utc).isoformat(),
            snapshots=[
                VideoMetricSnapshot(
                    hours_since_publish=24.0,
                    views=raw_meta.get("view_count", 0),
                    likes=raw_meta.get("like_count", 0),
                    comments=raw_meta.get("comment_count", 0),
                    velocity_views_per_hour=raw_meta.get("view_velocity_vs_channel_baseline_pct", 100.0),
                    sentiment_positive_pct=raw_meta.get("sentiment_distribution", {}).get("positive_pct", 85.0),
                    sentiment_negative_pct=raw_meta.get("sentiment_distribution", {}).get("negative_pct", 5.0)
                )
            ]
        )
        self.videos[video_id] = video
        self._save_storage()
        return video

    def update_video_tracking_duration(self, video_id: str, new_duration_days: int) -> Optional[TrackedVideo]:
        """Adjusts the active surveillance window for a specific video to optimize cloud costs."""
        if video_id in self.videos:
            self.videos[video_id].tracking_duration_days = new_duration_days
            self._save_storage()
            return self.videos[video_id]
        return None

    def list_videos(self) -> List[TrackedVideo]:
        """Returns all tracked videos."""
        return list(self.videos.values())

    def get_video_report(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves or generates report for a tracked video."""
        if video_id in self.videos:
            return VideoReportGenerator.generate_full_report(video_id)
        return None


tracking_service = TrackingManagerService()

from datetime import datetime, timezone
from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field

class ChannelSnapshot(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    subscriber_count: int = 0
    total_video_count: int = 0
    average_views_per_video: float = 0.0

# Pre-defined Industry Taxonomy Templates
DEFAULT_TAXONOMY_TEMPLATES = {
    "FINANCE_MEDIA": ["Macroeconomic Debates", "Data & Source Requests", "Contrarian Perspectives", "Editorial Praise"],
    "B2B_TECH_SAAS": ["Architecture Inquiries", "Bug & Code Challenges", "Recruitment & Careers", "General Tech Praise"],
    "LOCAL_SERVICE_BOOKING": ["Direct Booking & Pricing", "Aesthetic & Photo Praise", "Location Inquiries", "Service Feedback"],
    "ENTERTAINMENT_ROAST": ["Comedic Roasting Praise", "Actor & Drama Defense", "Next Episode Suggestions", "Awards Voting"]
}

class TrackedChannel(BaseModel):
    channel_id: str
    handle: str # e.g. "@business", "@KiemDinhPhim9.0"
    platform: Literal["youtube", "tiktok"] = "youtube"
    title: str
    category: str = "General" # "Tech/Software", "Entertainment/Film", "Corporate"
    tracking_status: Literal["ACTIVE", "PAUSED"] = "ACTIVE"
    check_frequency_minutes: int = 15
    video_lookback_days: int = 30 # FinOps: Only inspect videos published within last 30 days
    custom_sentiment_categories: List[str] = Field(default_factory=lambda: ["Praise & Loyalty", "Technical Inquiries", "Commercial Leads", "Complaints & Friction"])
    notification_channel: str = "#media-alerts"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_checked_at: Optional[str] = None
    latest_video_id: Optional[str] = None
    snapshots: List[ChannelSnapshot] = []

class VideoMetricSnapshot(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    hours_since_publish: float = 0.0
    views: int
    likes: int
    comments: int
    velocity_views_per_hour: float = 0.0
    sentiment_positive_pct: float = 80.0
    sentiment_negative_pct: float = 5.0

class TrackedVideo(BaseModel):
    video_id: str
    channel_id: str
    url: str
    title: str
    published_at: str
    tracking_duration_days: int = 30 # FinOps: Configurable tracking window in days
    expires_at: Optional[str] = None
    custom_sentiment_categories: List[str] = Field(default_factory=lambda: ["Praise & Loyalty", "Technical Inquiries", "Commercial Leads", "Complaints & Friction"])
    monitoring_tier: Literal["HIGH_PRIORITY_24H", "NORMAL_7D", "ARCHIVED"] = "HIGH_PRIORITY_24H"
    tracking_status: Literal["ACTIVE", "PAUSED", "COMPLETED"] = "ACTIVE"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_analyzed_at: Optional[str] = None
    snapshots: List[VideoMetricSnapshot] = []
    generated_report_path: Optional[str] = None
    anomaly_status: Literal["NORMAL", "VIRAL_ACCELERATION", "PR_CRISIS"] = "NORMAL"

class AddChannelRequest(BaseModel):
    channel_handle_or_url: str
    category: str = "General"
    video_lookback_days: int = 30
    custom_sentiment_categories: Optional[List[str]] = None
    notification_channel: str = "#media-alerts"

class UpdateChannelCategoriesRequest(BaseModel):
    custom_sentiment_categories: List[str]

class AddVideoRequest(BaseModel):
    video_url_or_id: str
    tracking_duration_days: int = 30
    custom_sentiment_categories: Optional[List[str]] = None
    monitoring_tier: Literal["HIGH_PRIORITY_24H", "NORMAL_7D"] = "HIGH_PRIORITY_24H"

class UpdateVideoDurationRequest(BaseModel):
    tracking_duration_days: int



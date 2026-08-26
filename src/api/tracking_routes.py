from typing import Dict, List, Any
from fastapi import APIRouter, HTTPException
from src.models.tracking_models import (
    TrackedChannel,
    TrackedVideo,
    AddChannelRequest,
    AddVideoRequest,
    UpdateChannelCategoriesRequest
)
from src.services.tracking_service import tracking_service

router = APIRouter(prefix="/api/v1/tracking", tags=["Tracking Engine"])

# --- CHANNELS ENDPOINTS ---

@router.get("/channels", response_model=List[TrackedChannel])
def get_all_tracked_channels():
    """Returns the list of all registered YouTube/TikTok channels currently tracked."""
    return tracking_service.list_channels()

@router.post("/channels", response_model=TrackedChannel)
def add_new_tracked_channel(req: AddChannelRequest):
    """Registers a new YouTube/TikTok channel to track for upload events, 30-day velocity, and custom taxonomy."""
    return tracking_service.add_channel(
        handle_or_url=req.channel_handle_or_url,
        category=req.category,
        video_lookback_days=req.video_lookback_days,
        custom_sentiment_categories=req.custom_sentiment_categories,
        notification_channel=req.notification_channel
    )

@router.patch("/channels/{channel_id}/categories", response_model=TrackedChannel)
def update_channel_custom_categories(channel_id: str, req: UpdateChannelCategoriesRequest):
    """Allows channel owners/analysts to dynamically customize the 4D sentiment/intent taxonomy dimensions."""
    updated = tracking_service.update_channel_sentiment_categories(channel_id, req.custom_sentiment_categories)
    if not updated:
        raise HTTPException(status_code=404, detail="Channel not found")
    return updated


@router.delete("/channels/{channel_id}")
def delete_tracked_channel(channel_id: str):
    """Deletes a channel from tracking."""
    success = tracking_service.remove_channel(channel_id)
    if not success:
        raise HTTPException(status_code=404, detail="Channel not found")
    return {"status": "DELETED_SUCCESS", "channel_id": channel_id}

# --- VIDEOS ENDPOINTS ---

@router.get("/videos", response_model=List[TrackedVideo])
def get_all_tracked_videos():
    """Returns the list of all individual videos monitored in real-time."""
    return tracking_service.list_videos()

@router.post("/videos", response_model=TrackedVideo)
def add_new_tracked_video(req: AddVideoRequest):
    """Registers an individual YouTube video URL to track velocity, sentiment, and auto-generate reports."""
    return tracking_service.add_video(
        video_url_or_id=req.video_url_or_id,
        tracking_duration_days=req.tracking_duration_days,
        monitoring_tier=req.monitoring_tier
    )

@router.patch("/videos/{video_id}/duration", response_model=TrackedVideo)
def update_video_duration(video_id: str, req: Dict[str, int]):
    """Adjusts the active surveillance window in days for a specific video to optimize BigQuery/Cloud Run costs."""
    duration = req.get("tracking_duration_days", 30)
    updated = tracking_service.update_video_tracking_duration(video_id, duration)
    if not updated:
        raise HTTPException(status_code=404, detail="Video not found")
    return updated

@router.get("/videos/{video_id}/report")
def get_tracked_video_report(video_id: str):

    """Fetches or re-generates the comprehensive intelligence report for a tracked video."""
    report = tracking_service.get_video_report(video_id)
    if not report:
        raise HTTPException(status_code=404, detail="Video report not found")
    return report

# --- SUMMARY DASHBOARD ---

@router.get("/dashboard/summary")
def get_tracking_dashboard_summary() -> Dict[str, Any]:
    """Provides high-level real-time KPI overview of all tracked assets."""
    channels = tracking_service.list_channels()
    videos = tracking_service.list_videos()
    
    total_views_tracked = sum([v.snapshots[-1].views for v in videos if v.snapshots])
    active_anomalies = [v for v in videos if v.anomaly_status != "NORMAL"]

    return {
        "status": "HEALTHY",
        "total_channels_tracked": len(channels),
        "total_videos_monitored": len(videos),
        "total_views_under_management": total_views_tracked,
        "active_anomalies_detected": len(active_anomalies),
        "active_channels": [c.handle for c in channels if c.tracking_status == "ACTIVE"],
        "active_videos": [{"id": v.video_id, "title": v.title, "views": v.snapshots[-1].views if v.snapshots else 0} for v in videos]
    }

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

from src.core.config import settings

logger = logging.getLogger("studiosonar.registry")

REGISTRY_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "tracking_registry.json")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")

class TrackingRegistryManager:
    """
    Central Dynamic Registry for Monitored Channels, Videos, and Reports.
    Eliminates all hardcoded channel/video IDs across the system.
    """

    def __init__(self, registry_file: str = REGISTRY_PATH):
        self.registry_file = registry_file
        self._bq_client = None
        self._bq_available = False
        self._ensure_registry_exists()

    def _get_bq_client(self):
        """Lazily initializes the BigQuery client (single source of truth on Cloud Run)."""
        if self._bq_client is not None:
            return self._bq_client
        try:
            from google.cloud import bigquery
            self._bq_client = bigquery.Client(project=settings.gcp_project_id)
            self._bq_available = True
        except Exception as e:
            logger.warning(f"BigQuery registry client unavailable (strict BigQuery mode): {e}")
            self._bq_client = None
            self._bq_available = False
        return self._bq_client

    def _ensure_seeded(self):
        """Seeds the canonical sample registry into BigQuery if tables lack rows."""
        client = self._get_bq_client()
        if not client:
            return False
        try:
            from src.data.registry_seeder import ensure_registry_seeded
            ensure_registry_seeded(client, settings.gcp_project_id, settings.bigquery_dataset)
            return True
        except Exception as e:
            logger.warning(f"Registry seeding notice: {e}")
            return False

    def _ensure_registry_exists(self):
        if not os.path.exists(self.registry_file):
            default_data = {"channels": [], "videos": []}
            os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(default_data, f, indent=2, ensure_ascii=False)

    def _load_data(self) -> Dict[str, Any]:
        try:
            with open(self.registry_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read tracking registry: {e}")
            return {"channels": [], "videos": []}

    def _save_data(self, data: Dict[str, Any]):
        try:
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save tracking registry: {e}")

    def get_all_channels(self) -> List[Dict[str, Any]]:
        """
        Returns all actively tracked channels directly from BigQuery (tracked_channels).
        Strict BigQuery source-of-truth: no JSON fallback. Seeds tables if empty.
        """
        client = self._get_bq_client()
        if not client:
            logger.warning("get_all_channels: BigQuery unavailable (strict mode) -> returning empty list.")
            return []

        dataset = settings.bigquery_dataset
        channels = self._query_channels(client, dataset)

        # Self-heal: if the table is empty, seed canonical sample and re-query.
        if not channels:
            self._ensure_seeded()
            channels = self._query_channels(client, dataset)

        return channels

    def _query_channels(self, client, dataset: str) -> List[Dict[str, Any]]:
        try:
            query = f"""
                SELECT channel_id, handle, platform, title, category, tracking_status,
                       check_frequency_minutes, notification_channel,
                       subscriber_count, total_video_count, created_at, last_checked_at
                FROM `{client.project}.{dataset}.tracked_channels`
                WHERE tracking_status = 'ACTIVE'
                ORDER BY title
            """
            query_job = client.query(query)
            default_categories = ["Praise & Loyalty", "Technical Inquiries", "Commercial Leads", "Complaints & Friction"]
            result = []
            for row in query_job.result():
                result.append({
                    "channel_id": row.channel_id,
                    "report_key": f"channel_{row.handle.replace('@', '').replace('.', '_').lower()}",
                    "handle": row.handle,
                    "platform": row.platform or "youtube",
                    "title": row.title or row.handle,
                    "category": row.category or "General",
                    "tracking_status": row.tracking_status or "ACTIVE",
                    "check_frequency_minutes": row.check_frequency_minutes or 15,
                    "video_lookback_days": 30,
                    "custom_sentiment_categories": default_categories,
                    "notification_channel": row.notification_channel or "#media-alerts",
                    "snapshots": [{
                        "timestamp": (row.created_at.isoformat() if row.created_at else datetime.now(timezone.utc).isoformat()),
                        "subscriber_count": int(row.subscriber_count or 0),
                        "total_video_count": int(row.total_video_count or 0),
                        "average_views_per_video": 0.0
                    }]
                })
            return result
        except Exception as e:
            logger.debug(f"BigQuery dynamic channel query fallback notice: {e}")
            return []

    def get_all_videos(self) -> List[Dict[str, Any]]:
        """
        Returns all actively tracked videos (including TikTok sounds) directly from
        BigQuery (videos). Strict BigQuery source-of-truth: no JSON fallback.
        Seeds tables if empty.
        """
        client = self._get_bq_client()
        if not client:
            logger.warning("get_all_videos: BigQuery unavailable (strict mode) -> returning empty list.")
            return []

        dataset = settings.bigquery_dataset
        videos = self._query_videos(client, dataset)

        # Self-heal: if the table is empty, seed canonical sample and re-query.
        if not videos:
            self._ensure_seeded()
            videos = self._query_videos(client, dataset)

        return videos

    def _query_videos(self, client, dataset: str) -> List[Dict[str, Any]]:
        try:
            query = f"""
                SELECT video_id, channel_id, platform, url, title, published_at,
                       monitoring_tier, tracking_status, view_count, like_count, comment_count
                FROM `{client.project}.{dataset}.videos`
                WHERE tracking_status = 'ACTIVE'
                ORDER BY published_at DESC
            """
            query_job = client.query(query)
            result = []
            for row in query_job.result():
                result.append({
                    "video_id": row.video_id,
                    "channel_id": row.channel_id or "ch_music_vpop",
                    "platform": row.platform or "youtube",
                    "url": row.url or f"https://www.youtube.com/watch?v={row.video_id}",
                    "title": row.title,
                    "published_at": (row.published_at.isoformat() if row.published_at else datetime.now(timezone.utc).isoformat()),
                    "tracking_status": "ACTIVE",
                    "monitoring_tier": row.monitoring_tier or "HIGH_PRIORITY_24H",
                    "snapshots": [{
                        "views": int(row.view_count or 0),
                        "likes": int(row.like_count or 0),
                        "comments": int(row.comment_count or 0)
                    }]
                })
            return result
        except Exception as e:
            logger.debug(f"BigQuery dynamic video query fallback notice: {e}")
            return []


    def get_monitored_video_ids(self) -> List[str]:
        """Returns list of video IDs currently monitored."""
        videos = self.get_all_videos()
        return [v.get("video_id") for v in videos if v.get("video_id")]

    def get_primary_company_channel(self) -> Dict[str, Any]:
        """Returns the primary company channel configured in the registry."""
        channels = self.get_all_channels()
        if channels:
            return channels[0]
        return {
            "channel_id": "ch_default_official",
            "title": "Official Company Channel",
            "handle": "@official_channel"
        }

    def add_or_update_video(self, video_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamically registers a new video for tracking."""
        data = self._load_data()
        videos = data.setdefault("videos", [])
        vid_id = video_data.get("video_id")
        
        # Check if already exists
        for i, v in enumerate(videos):
            if v.get("video_id") == vid_id:
                videos[i].update(video_data)
                self._save_data(data)
                return videos[i]
        
        # Add new
        new_entry = {
            "video_id": vid_id,
            "channel_id": video_data.get("channel_id", "custom_channel"),
            "url": video_data.get("url", f"https://www.youtube.com/watch?v={vid_id}"),
            "title": video_data.get("title", f"Video {vid_id}"),
            "published_at": video_data.get("published_at", datetime.now(timezone.utc).isoformat()),
            "tracking_status": "ACTIVE",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "generated_report_path": f"reports/video_report_{vid_id}.md"
        }
        videos.append(new_entry)
        self._save_data(data)
        return new_entry

    def resolve_report_path(self, report_key: str) -> Optional[str]:
        """
        Dynamically locates a report file from disk without static dictionaries.
        Supports fuzzy keyword matching and prefix stripping.
        """
        if not report_key:
            return None

        if report_key == "realtime_24h":
            return os.path.join(REPORTS_DIR, "realtime_24h_pulse_report.md")
        
        clean_key = report_key.replace("video_", "").replace("channel_", "").replace("tt_sound_", "").strip()
        
        alias_map = {
            "business": "bloomberg_originals",
            "bloomberg": "bloomberg_originals",
            "kiemdinhphim90": "kiemdinhphim",
            "thochupanhdalat": "thochupanh_dalat",
            "thochupanh": "thochupanh_dalat"
        }
        mapped_key = alias_map.get(clean_key, clean_key)

        # 1. Try explicit direct filename candidates
        candidates = [
            os.path.join(REPORTS_DIR, f"{report_key}.md"),
            os.path.join(REPORTS_DIR, f"video_report_{clean_key}.md"),
            os.path.join(REPORTS_DIR, f"channel_report_{clean_key}.md"),
            os.path.join(REPORTS_DIR, f"channel_report_{mapped_key}.md"),
            os.path.join(REPORTS_DIR, f"tiktok_report_{clean_key}.md"),
            os.path.join(REPORTS_DIR, f"tiktok_report_sound_{clean_key}.md"),
            os.path.join(REPORTS_DIR, f"tiktok_report_sound_{clean_key.replace('pmc_', '').replace('dtap_', '')}.md"),
            os.path.join(REPORTS_DIR, f"video_report_{report_key}.md"),
            os.path.join(REPORTS_DIR, f"channel_report_{report_key}.md"),
            os.path.join(REPORTS_DIR, f"{clean_key}.md"),
            os.path.join(REPORTS_DIR, f"{mapped_key}.md")
        ]
        
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        
        # 2. Scan reports directory for loose matching
        sub_keywords = [w for w in clean_key.split("_") if len(w) > 3] + [w for w in mapped_key.split("_") if len(w) > 3]
        if os.path.exists(REPORTS_DIR):
            for fname in os.listdir(REPORTS_DIR):
                if not fname.endswith(".md"):
                    continue
                f_lower = fname.lower()
                # Match clean keyword, mapped key, or sub-keywords in filename
                if clean_key.lower() in f_lower or mapped_key.lower() in f_lower or any(sk.lower() in f_lower for sk in sub_keywords):
                    return os.path.join(REPORTS_DIR, fname)
                    
        return None



registry_manager = TrackingRegistryManager()


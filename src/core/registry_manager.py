import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

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
        self._ensure_registry_exists()

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
        """Returns all actively tracked channels."""
        return self._load_data().get("channels", [])

    def get_all_videos(self) -> List[Dict[str, Any]]:
        """
        Returns all actively tracked videos directly from Database (BigQuery).
        If user deletes or adds a video in BigQuery, dashboard reflects immediately!
        """
        if not os.getenv("K_SERVICE") and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return self._load_data().get("videos", [])

        try:
            from google.cloud import bigquery
            client = bigquery.Client(project=os.getenv("GCP_PROJECT_ID", "studiosonar-dev"))
            dataset = os.getenv("BIGQUERY_DATASET", "studiosonar_analytics")
            query = f"SELECT video_id, channel_id, url, title, view_count, like_count, comment_count FROM `{client.project}.{dataset}.videos`"
            query_job = client.query(query)
            bq_videos = []
            for row in query_job.result():
                bq_videos.append({
                    "video_id": row.video_id,
                    "channel_id": row.channel_id or "ch_music_vpop",
                    "url": row.url or f"https://www.youtube.com/watch?v={row.video_id}",
                    "title": row.title,
                    "tracking_status": "ACTIVE",
                    "snapshots": [{
                        "views": row.view_count or 0,
                        "likes": row.like_count or 0,
                        "comments": row.comment_count or 0
                    }]
                })
            if bq_videos:
                return bq_videos
        except Exception as e:
            logger.debug(f"BigQuery dynamic video query fallback: {e}")

        # Fallback to local JSON registry
        return self._load_data().get("videos", [])


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


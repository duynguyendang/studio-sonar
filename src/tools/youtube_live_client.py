import os
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta
from src.core.config import settings

logger = logging.getLogger("studiosonar.youtube_live_client")

class YouTubeLiveClient:
    """
    Direct client for Google YouTube Data API v3.
    Fetches real-time video statistics, channel uploads, and live incoming comments.
    """

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.youtube_data_api_key or os.getenv("YOUTUBE_DATA_API_KEY")

    def get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Fetches live statistics and metadata for a specific YouTube video."""
        if not self.api_key:
            return None
        
        url = f"{self.BASE_URL}/videos"
        params = {
            "part": "snippet,statistics,contentDetails",
            "id": video_id,
            "key": self.api_key
        }
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                items = data.get("items", [])
                if items:
                    item = items[0]
                    snippet = item.get("snippet", {})
                    stats = item.get("statistics", {})
                    return {
                        "video_id": video_id,
                        "title": snippet.get("title"),
                        "channel_title": snippet.get("channelTitle"),
                        "published_at": snippet.get("publishedAt"),
                        "views": int(stats.get("viewCount", 0)),
                        "likes": int(stats.get("likeCount", 0)),
                        "comments_count": int(stats.get("commentCount", 0)),
                        "tags": snippet.get("tags", [])
                    }
        except Exception as e:
            logger.error(f"Error fetching YouTube video details for {video_id}: {e}")
        return None

    def get_channel_recent_videos(
        self, 
        channel_handle_or_id: str, 
        lookback_days: int = 30, 
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Dynamically fetches verified videos published by a channel within the last N days (7, 30 days).
        Uses official Uploads Playlist to avoid stale/outdated assets.
        """
        if not self.api_key:
            return []

        clean_handle = channel_handle_or_id.replace("@", "").strip()
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        try:
            # 1. Resolve Channel & Uploads Playlist ID
            ch_url = f"{self.BASE_URL}/channels"
            params = {
                "part": "id,snippet,contentDetails,statistics",
                "key": self.api_key
            }
            if clean_handle.startswith("UC"):
                params["id"] = clean_handle
            else:
                params["forHandle"] = clean_handle

            res_ch = requests.get(ch_url, params=params, timeout=10)
            if res_ch.status_code != 200:
                logger.warning(f"Failed to fetch channel for handle {clean_handle}: {res_ch.text}")
                return []

            items = res_ch.json().get("items", [])
            if not items:
                # Fallback search if handle lookup fails
                search_url = f"{self.BASE_URL}/search"
                s_params = {
                    "part": "snippet",
                    "q": clean_handle,
                    "type": "channel",
                    "maxResults": 1,
                    "key": self.api_key
                }
                s_res = requests.get(search_url, params=s_params, timeout=10)
                s_items = s_res.json().get("items", [])
                if s_items:
                    ch_id = s_items[0]["snippet"]["channelId"]
                    return self.get_channel_recent_videos(ch_id, lookback_days, max_results)
                return []

            ch_item = items[0]
            uploads_playlist_id = ch_item.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
            if not uploads_playlist_id:
                return []

            # 2. Fetch Latest Uploaded Videos from Playlist
            pl_url = f"{self.BASE_URL}/playlistItems"
            pl_params = {
                "part": "snippet,contentDetails",
                "playlistId": uploads_playlist_id,
                "maxResults": min(max_results * 2, 50),
                "key": self.api_key
            }
            res_pl = requests.get(pl_url, params=pl_params, timeout=10)
            if res_pl.status_code != 200:
                return []

            recent_videos = []
            for item in res_pl.json().get("items", []):
                snippet = item.get("snippet", {})
                published_at_str = snippet.get("publishedAt")
                if not published_at_str:
                    continue

                # Parse UTC timestamp
                try:
                    pub_dt = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
                except Exception:
                    pub_dt = datetime.now(timezone.utc)

                # Filter strictly within lookback_days
                if pub_dt >= cutoff_date:
                    video_id = snippet.get("resourceId", {}).get("videoId")
                    if video_id:
                        # Fetch full statistics
                        v_details = self.get_video_details(video_id)
                        if v_details:
                            v_details["hours_since_publish"] = round((datetime.now(timezone.utc) - pub_dt).total_seconds() / 3600.0, 1)
                            recent_videos.append(v_details)

                if len(recent_videos) >= max_results:
                    break

            return recent_videos

        except Exception as e:
            logger.error(f"Error fetching channel recent videos for {channel_handle_or_id}: {e}")
            return []

    def get_live_comments(self, video_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Fetches latest real incoming comments from a YouTube video."""
        if not self.api_key:
            return []
        
        url = f"{self.BASE_URL}/commentThreads"
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(max_results, 100),
            "order": "time",
            "key": self.api_key
        }
        comments = []
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for item in data.get("items", []):
                    top_comment = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                    comments.append({
                        "author": top_comment.get("authorDisplayName"),
                        "text": top_comment.get("textDisplay"),
                        "like_count": top_comment.get("likeCount", 0),
                        "published_at": top_comment.get("publishedAt")
                    })
        except Exception as e:
            logger.error(f"Error fetching live YouTube comments for {video_id}: {e}")
        return comments

youtube_live_client = YouTubeLiveClient()

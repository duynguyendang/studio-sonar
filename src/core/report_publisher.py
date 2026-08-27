"""
StudioSonar Full-Surveillance Report Publisher.
Synchronizes and uploads ALL 12 markdown intelligence reports to Google Cloud Storage bucket
with live metrics from YouTube Data API v3 and BigQuery.
"""

import os
import glob
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

from src.core.gcs_report_manager import gcs_report_manager, REPORTS_DIR
from src.tools.youtube_live_client import youtube_live_client

logger = logging.getLogger("studiosonar.report_publisher")

class ReportPublisher:
    """Manages multi-asset report synchronization and bulk publishing to GCS."""

    def publish_all_reports_to_gcs(self, live_video_stats: Dict[str, Dict[str, Any]] = None) -> List[str]:
        """
        Updates and uploads all local intelligence reports to GCS bucket.
        Returns list of published GCS URIs.
        """
        published_uris = []
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # 1. Fetch live YouTube stats if not provided
        if not live_video_stats:
            live_video_stats = {}
            target_ids = ["UH21OnJwxZE", "Rp6ZnP5WRgI", "R7Bf4l5VgO8", "TNl9diGdyPo", "FEhLXCMXWUk"]
            for vid in target_ids:
                details = youtube_live_client.get_video_details(vid)
                if details:
                    live_video_stats[vid] = details

        # 2. Iterate through all markdown files in reports directory
        md_files = glob.glob(os.path.join(REPORTS_DIR, "*.md"))
        for file_path in md_files:
            filename = os.path.basename(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Dynamic enrichment for video reports
                if filename.startswith("video_report_"):
                    vid_id = filename.replace("video_report_", "").replace(".md", "")
                    if vid_id in live_video_stats:
                        stats = live_video_stats[vid_id]
                        views = stats.get("views", 0)
                        likes = stats.get("likes", 0)
                        comments = stats.get("comments_count", 0)
                        
                        # Update metrics line if exists
                        lines = content.split("\n")
                        new_lines = []
                        for line in lines:
                            if "> **Real-Time Analytics:**" in line:
                                new_lines.append(f"> **Real-Time Analytics:** {views:,} Views • {likes:,} Likes • {comments:,} Comments (Live YouTube API)  ")
                            elif "Last Synced:" in line:
                                new_lines.append(f"> *Last Synced:* {now_utc}  ")
                            else:
                                new_lines.append(line)
                        content = "\n".join(new_lines)
                        if "Last Synced:" not in content:
                            content += f"\n\n---\n*Last Synchronized:* {now_utc} by StudioSonar Swarm Taskmaster\n"

                elif filename.startswith("channel_report_") or filename.startswith("tiktok_report_"):
                    if "Last Synchronized:" not in content:
                        content += f"\n\n---\n*Last Synchronized:* {now_utc} by StudioSonar Swarm Taskmaster\n"
                    else:
                        lines = [line for line in content.split("\n") if "Last Synchronized:" not in line]
                        content = "\n".join(lines).strip() + f"\n\n---\n*Last Synchronized:* {now_utc} by StudioSonar Swarm Taskmaster\n"

                # Upload to GCS
                success = gcs_report_manager.save_report(filename, content)
                if success:
                    uri = f"gs://{gcs_report_manager.bucket_name}/{filename}"
                    published_uris.append(uri)
                    logger.info(f"Published intelligence report: {uri}")
            except Exception as e:
                logger.warning(f"Error publishing report {filename} to GCS: {e}")

        return published_uris

report_publisher = ReportPublisher()

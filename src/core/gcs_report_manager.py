import os
import logging
from typing import Optional, Tuple
from src.core.registry_manager import registry_manager, REPORTS_DIR

logger = logging.getLogger("studiosonar.gcs_reports")

GCS_BUCKET_NAME = os.getenv("GCS_REPORTS_BUCKET", "studiosonar-dev-reports")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "studiosonar-dev")

class GCSReportManager:
    """
    Cloud-Native Storage Manager for StudioSonar Intelligence Reports.
    Reads and writes markdown intelligence reports directly to/from Google Cloud Storage.
    Falls back seamlessly to container local reports if GCS is unreachable.
    """

    def __init__(self, bucket_name: str = GCS_BUCKET_NAME, project_id: str = GCP_PROJECT_ID):
        self.bucket_name = bucket_name
        self.project_id = project_id
        self._storage_client = None
        self._bucket = None

    def _get_bucket(self):
        if self._bucket is None:
            try:
                from google.cloud import storage
                self._storage_client = storage.Client(project=self.project_id)
                self._bucket = self._storage_client.bucket(self.bucket_name)
                logger.info(f"Connected to GCS Report Bucket: gs://{self.bucket_name}")
            except Exception as e:
                logger.warning(f"GCS client init notice (will fallback to local): {e}")
        return self._bucket


    def fetch_report(self, report_key: str) -> Tuple[Optional[str], str]:
        """
        Fetches markdown content for a report key from GCS, with local filesystem fallback.
        Returns: (markdown_content, source_path)
        """
        if not report_key:
            return None, "Not found"

        clean_key = report_key.replace("video_", "").replace("channel_", "").replace("tt_sound_", "").strip()

        # Alias mappings for channels and videos
        alias_map = {
            "business": "bloomberg_originals",
            "bloomberg": "bloomberg_originals",
            "bloomberg_originals": "bloomberg_originals",
            "kiemdinhphim90": "kiemdinhphim9_0",
            "kiemdinhphim": "kiemdinhphim9_0",
            "thochupanhdalat": "thochupanh_dalat",
            "thochupanh": "thochupanh_dalat",
            "thien_duong": "UH21OnJwxZE",
            "thienduong": "UH21OnJwxZE",
            "brent_oil": "Fe2AjVSW-TA",
            "brent": "Fe2AjVSW-TA",
            "oil": "Fe2AjVSW-TA",
            "us_iran": "Fe2AjVSW-TA",
            "nutella": "TNl9diGdyPo",
            "thuy_chi": "R7Bf4l5VgO8",
            "yeu_lam_mien_tay": "R7Bf4l5VgO8"
        }
        mapped_key = alias_map.get(clean_key, clean_key)

        # Dynamic registry resolution if not directly in alias map
        try:
            for v in registry_manager.get_all_videos():
                vid = v.get("video_id", "")
                v_title = (v.get("title") or "").lower()
                clean_lower = clean_key.lower().replace("_", " ")
                if clean_key == vid or clean_lower in v_title:
                    mapped_key = vid
                    break
        except Exception:
            pass

        # 1. Try Fetching directly from Google Cloud Storage (GCS)
        try:
            bucket = self._get_bucket()
            if bucket:
                # Candidate blob names in bucket
                blob_names = [
                    f"{report_key}.md",
                    f"video_report_{clean_key}.md",
                    f"video_report_{mapped_key}.md",
                    f"channel_report_{clean_key}.md",
                    f"channel_report_{mapped_key}.md",
                    f"tiktok_report_{clean_key}.md",
                    f"tiktok_report_sound_{clean_key}.md",
                    f"tiktok_report_sound_{mapped_key}.md",
                    f"tiktok_report_sound_{clean_key.replace('pmc_', '').replace('dtap_', '')}.md",
                    f"video_report_{report_key}.md",
                    f"channel_report_{report_key}.md",
                    f"{clean_key}.md",
                    f"{mapped_key}.md"
                ]
                if report_key == "realtime_24h":
                    blob_names.insert(0, "realtime_24h_pulse_report.md")

                for b_name in blob_names:
                    blob = bucket.blob(b_name)
                    if blob.exists():
                        content = blob.download_as_text(encoding="utf-8")
                        logger.info(f"Loaded report from GCS: gs://{self.bucket_name}/{b_name}")
                        return content, f"gs://{self.bucket_name}/{b_name}"
                
                # Precise fuzzy match in GCS bucket: only match blobs whose name contains clean_key or mapped_key
                blobs = list(bucket.list_blobs(prefix=""))
                for b in blobs:
                    if not b.name.endswith(".md") or b.name == "README.md" or b.name.startswith("channel_report_."):
                        continue
                    b_lower = b.name.lower()
                    if (clean_key.lower() in b_lower and len(clean_key) > 3) or (mapped_key.lower() in b_lower and len(mapped_key) > 3):
                        content = b.download_as_text(encoding="utf-8")
                        logger.info(f"Loaded report via GCS fuzzy match: gs://{self.bucket_name}/{b.name}")
                        return content, f"gs://{self.bucket_name}/{b.name}"
        except Exception as e:
            logger.warning(f"GCS Fetch failed for key '{report_key}', falling back to disk: {e}")



        # 2. Fallback to container local filesystem
        local_path = registry_manager.resolve_report_path(report_key)
        if local_path and os.path.exists(local_path):
            with open(local_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.info(f"Loaded report from local disk fallback: {local_path}")
            return content, local_path

        return None, "Report not found"

    def save_report(self, filename: str, markdown_content: str) -> bool:
        """
        Saves a generated markdown report directly to GCS and local mirror.
        """
        # Save local mirror
        local_path = os.path.join(REPORTS_DIR, filename)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)

        # Upload to GCS
        try:
            bucket = self._get_bucket()
            if bucket:
                blob = bucket.blob(filename)
                blob.upload_from_string(markdown_content, content_type="text/markdown; charset=utf-8")
                logger.info(f"Uploaded report to GCS: gs://{self.bucket_name}/{filename}")
                return True
        except Exception as e:
            logger.error(f"Failed to upload report to GCS gs://{self.bucket_name}/{filename}: {e}")

        return False

    # ------------------------------------------------------------------ cycle ledger
    # A small JSON ledger in GCS lets the dashboard stay IN SYNC with the
    # async/job cycle: the UI polls until `completed_at` advances, then
    # refreshes telemetry + reports knowing the data is fresh.

    def save_cycle_ledger(self, ledger: dict) -> bool:
        import json
        payload = json.dumps(ledger, ensure_ascii=False, indent=2)
        try:
            bucket = self._get_bucket()
            if bucket:
                blob = bucket.blob("cycle_ledger.json")
                blob.upload_from_string(payload, content_type="application/json")
                logger.info(f"Cycle ledger updated: {ledger}")
                return True
        except Exception as e:
            logger.warning(f"Failed to save cycle ledger: {e}")
        return False

    def fetch_cycle_ledger(self) -> dict:
        import json
        default = {"status": "UNKNOWN", "started_at": None, "completed_at": None}
        try:
            bucket = self._get_bucket()
            if bucket:
                blob = bucket.blob("cycle_ledger.json")
                if blob.exists():
                    data = json.loads(blob.download_as_text(encoding="utf-8"))
                    return {**default, **data}
        except Exception as e:
            logger.debug(f"Cycle ledger fetch notice: {e}")
        return default

    def list_available_reports(self):
        """
        Lists all available intelligence reports directly from Google Cloud Storage,
        falling back to the local reports/ mirror if GCS is unreachable.
        Returns a sorted, categorized list of report descriptors for frontend selectors.
        """
        reports_map = {}

        # 1. Fetch registry lookup maps for rich titles
        video_title_map = {}
        channel_title_map = {}
        try:
            for v in registry_manager.get_all_videos():
                vid = v.get("video_id")
                if vid:
                    video_title_map[vid] = v.get("title") or vid
            for ch in registry_manager.get_all_channels():
                ch_key = ch.get("report_key") or ch.get("channel_id")
                if ch_key:
                    channel_title_map[ch_key] = ch.get("title") or ch.get("handle") or ch_key
        except Exception as e:
            logger.debug(f"Registry title lookup notice: {e}")

        # 2. Query GCS Bucket Blobs
        try:
            bucket = self._get_bucket()
            if bucket:
                blobs = bucket.list_blobs()
                for blob in blobs:
                    name = blob.name
                    if not name.endswith(".md") or name == "README.md" or name == "channel_report_.md":
                        continue
                    mtime = blob.updated.isoformat() if blob.updated else ""
                    self._process_report_entry(name, mtime, video_title_map, channel_title_map, reports_map)
        except Exception as e:
            logger.warning(f"Could not list blobs from GCS: {e}")

        # 3. If GCS yielded nothing or for local development, scan local reports directory
        if not reports_map and os.path.exists(REPORTS_DIR):
            for fname in os.listdir(REPORTS_DIR):
                if not fname.endswith(".md") or fname == "README.md" or fname == "channel_report_.md":
                    continue
                fpath = os.path.join(REPORTS_DIR, fname)
                mtime = os.path.getmtime(fpath)
                from datetime import datetime, timezone
                dt_str = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
                self._process_report_entry(fname, dt_str, video_title_map, channel_title_map, reports_map)

        # 4. Sort and order: Master pulse first, then Videos, then Channels, then TikTok/Others
        category_order = {"master": 0, "video": 1, "channel": 2, "tiktok": 3, "other": 4}
        sorted_reports = sorted(
            reports_map.values(),
            key=lambda r: (category_order.get(r.get("category", "other"), 5), r.get("title", ""))
        )
        return sorted_reports

    def _process_report_entry(self, filename: str, updated_at: str, video_title_map: dict, channel_title_map: dict, reports_map: dict):
        clean_name = filename.replace(".md", "")
        
        if clean_name in ["realtime_24h_pulse_report", "realtime_24h"]:
            report_key = "realtime_24h"
            title = "📊 Master 24h Pulse Dossier (All Channels)"
            category = "master"
        elif clean_name.startswith("video_report_"):
            vid_id = clean_name.replace("video_report_", "")
            report_key = f"video_{vid_id}"
            v_title = video_title_map.get(vid_id)
            if not v_title:
                v_title = vid_id
            title = f"📹 Video: {v_title[:45]}"
            category = "video"
        elif clean_name.startswith("channel_report_"):
            ch_key = clean_name.replace("channel_report_", "")
            report_key = f"channel_report_{ch_key}"
            ch_title = channel_title_map.get(ch_key) or ch_key.replace("_", " ").title()
            title = f"🏢 Channel: {ch_title[:40]}"
            category = "channel"
        elif clean_name.startswith("tiktok_report_"):
            sound_key = clean_name.replace("tiktok_report_", "")
            report_key = clean_name
            title = f"🎵 TikTok Sound: {sound_key.replace('_', ' ').title()[:35]}"
            category = "tiktok"
        else:
            report_key = clean_name
            title = f"📄 Report: {clean_name.replace('_', ' ').title()}"
            category = "other"

        reports_map[report_key] = {
            "report_key": report_key,
            "filename": filename,
            "title": title,
            "category": category,
            "updated_at": updated_at
        }

gcs_report_manager = GCSReportManager()

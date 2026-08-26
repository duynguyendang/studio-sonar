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

        # Alias mappings for channels
        alias_map = {
            "business": "bloomberg_originals",
            "bloomberg": "bloomberg_originals",
            "kiemdinhphim90": "kiemdinhphim",
            "thochupanhdalat": "thochupanh_dalat",
            "thochupanh": "thochupanh_dalat"
        }
        mapped_key = alias_map.get(clean_key, clean_key)

        # 1. Try Fetching directly from Google Cloud Storage (GCS)
        try:
            bucket = self._get_bucket()
            if bucket:
                # Candidate blob names in bucket
                blob_names = [
                    f"{report_key}.md",
                    f"video_report_{clean_key}.md",
                    f"channel_report_{clean_key}.md",
                    f"channel_report_{mapped_key}.md",
                    f"channel_report_bloomberg_originals.md",
                    f"channel_report_kiemdinhphim.md",
                    f"channel_report_thochupanh_dalat.md",
                    f"tiktok_report_{clean_key}.md",
                    f"tiktok_report_sound_{clean_key}.md",
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
                
                # Loose scan in GCS bucket by sub-keywords
                sub_keywords = [w for w in clean_key.split("_") if len(w) > 3] + [w for w in mapped_key.split("_") if len(w) > 3]
                blobs = list(bucket.list_blobs(prefix=""))
                for b in blobs:
                    if not b.name.endswith(".md"):
                        continue
                    b_lower = b.name.lower()
                    if clean_key.lower() in b_lower or mapped_key.lower() in b_lower or any(sk.lower() in b_lower for sk in sub_keywords):
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

gcs_report_manager = GCSReportManager()

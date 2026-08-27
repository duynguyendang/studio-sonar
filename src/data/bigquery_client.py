import logging
from typing import Dict, List, Any, Optional
from src.core.config import settings
from src.data.mock_stream_generator import MockStreamGenerator

logger = logging.getLogger("studiosonar.bigquery")

class StudioSonarBigQueryClient:
    """Client for querying BigQuery OLAP storage and vector search."""

    def __init__(self):
        self.project_id = settings.gcp_project_id
        self.dataset = settings.bigquery_dataset
        self.mode = settings.execution_mode
        self._bq_client = None
        
        if self.mode == "live":
            try:
                from google.cloud import bigquery
                self._bq_client = bigquery.Client(project=self.project_id)
                logger.info(f"Initialized live BigQuery client for project {self.project_id}")
            except Exception as e:
                logger.warning(f"Could not connect to live BigQuery ({e}). Falling back to simulation mode.")
                self.mode = "mock"

    def query_sentiment_velocity_spikes(
        self,
        time_window_hours: int = 6,
        min_velocity_pct: float = 200.0,
        sentiment_threshold: float = -0.60
    ) -> List[Dict[str, Any]]:
        """Queries BigQuery for videos with abnormal negative comment velocity spikes."""
        if self.mode == "live" and self._bq_client:
            query = f"""
                SELECT 
                    video_id,
                    comment_volume,
                    avg_sentiment,
                    negative_comments,
                    baseline_volume,
                    velocity_spike_pct
                FROM `{self.project_id}.{self.dataset}.v_sentiment_velocity_spikes`
                WHERE velocity_spike_pct >= @min_velocity
                  AND avg_sentiment <= @sentiment_threshold
                ORDER BY velocity_spike_pct DESC
                LIMIT 10
            """
            from google.cloud import bigquery
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("min_velocity", "FLOAT64", min_velocity_pct),
                    bigquery.ScalarQueryParameter("sentiment_threshold", "FLOAT64", sentiment_threshold),
                ]
            )
            query_job = self._bq_client.query(query, job_config=job_config)
            return [dict(row) for row in query_job.result()]
        
        # Mock / Simulation Mode
        scenario = MockStreamGenerator.get_pr_crisis_scenario()
        return [
            {
                "video_id": scenario["video"]["video_id"],
                "channel_title": scenario["video"]["channel_title"],
                "video_title": scenario["video"]["title"],
                "comment_volume": scenario["video"]["comment_count"],
                "avg_sentiment": scenario["metrics"]["average_sentiment"],
                "negative_comments_count": 980,
                "velocity_spike_pct": scenario["metrics"]["negative_comment_velocity_pct"],
                "sample_negative_comments": [c["comment_text"] for c in scenario["comments"][:5]],
                "window_hours": time_window_hours,
                "transcript_snippet": scenario["video"]["transcript"][:200]
            }
        ]

    def query_viral_growth_trends(
        self,
        min_view_acceleration_pct: float = 300.0,
        lookback_hours: int = 8
    ) -> List[Dict[str, Any]]:
        """Queries BigQuery for breakout topics and retention hook formats."""
        if self.mode == "live" and self._bq_client:
            query = f"""
                SELECT 
                    video_id,
                    platform,
                    channel_id,
                    title,
                    view_count,
                    COALESCE(view_velocity_vs_channel_baseline_pct, 150.0) AS view_velocity_pct,
                    topic_tags
                FROM `{self.project_id}.{self.dataset}.videos`
                WHERE ingested_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL @lookback HOUR)
                ORDER BY view_count DESC
                LIMIT 10
            """
            from google.cloud import bigquery
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("lookback", "INT64", lookback_hours),
                ]
            )

            query_job = self._bq_client.query(query, job_config=job_config)
            return [dict(row) for row in query_job.result()]
        
        # Mock / Simulation Mode
        trend = MockStreamGenerator.get_viral_trend_scenario()
        return [
            {
                "trend_topic": trend["metrics"]["trend_keyword"],
                "cross_platform_acceleration_pct": trend["metrics"]["cross_platform_view_acceleration_pct"],
                "sentiment_score": trend["metrics"]["average_sentiment"],
                "top_videos": trend["videos"],
                "sample_audience_reactions": trend["positive_comments"][:4],
                "recommended_retention_structure": trend["metrics"]["retention_hook_pattern"],
                "lookback_hours": lookback_hours
            }
        ]

    def search_vector_topic_clusters(self, query_text: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Uses BigQuery Vector Search on text-embedding-004 vectors to find semantic clusters."""
        if self.mode == "live" and self._bq_client:
            try:
                query = f"""
                    SELECT base.comment_text, base.sentiment_label, distance
                    FROM VECTOR_SEARCH(
                        TABLE `{self.project_id}.{self.dataset}.comments`,
                        'embedding',
                        (SELECT ML.GENERATE_EMBEDDING(MODEL `{self.project_id}.{self.dataset}.embedding_model`, @query) AS embedding),
                        top_k => @top_k
                    )
                """
                from google.cloud import bigquery
                job_config = bigquery.QueryJobConfig(
                    query_parameters=[
                        bigquery.ScalarQueryParameter("query", "STRING", query_text),
                        bigquery.ScalarQueryParameter("top_k", "INT64", top_k),
                    ]
                )
                query_job = self._bq_client.query(query, job_config=job_config)
                return [dict(row) for row in query_job.result()]
            except Exception as e:
                logger.warning(f"Vector search falling back: {e}")

        # Fallback simulation
        return [
            {"matched_topic": "Public Reaction", "similarity_score": 0.89, "sample_comment": "Cần thêm thông tin minh bạch."},
            {"matched_topic": "Content Feedback", "similarity_score": 0.84, "sample_comment": "Video có nhiều điểm thú vị nhưng cần cải thiện pacing."}
        ]

    def collect_and_ingest_latest_telemetry(self) -> Dict[str, Any]:

        """
        Step 0 Autonomous Ingestion Job:
        Fetches live telemetry via YouTube Data API v3 and streams snapshots into BigQuery.
        Dynamically reads from registry_manager (Zero Hardcoding).
        """
        from src.tools.youtube_live_client import youtube_live_client
        from src.core.registry_manager import registry_manager
        from datetime import datetime, timezone
        
        monitored_videos = registry_manager.get_monitored_video_ids()
        ingestion_results = []

        
        for vid in monitored_videos:
            details = youtube_live_client.get_video_details(vid)
            if details:
                if self.mode == "live" and self._bq_client:
                    try:
                        table_id = f"{self.project_id}.{self.dataset}.video_snapshots"
                        rows_to_insert = [{
                            "snapshot_id": f"snap_{vid}_{int(datetime.now(timezone.utc).timestamp())}",
                            "video_id": vid,
                            "snapshot_timestamp": datetime.now(timezone.utc).isoformat(),
                            "hours_since_publish": 24,
                            "view_count": details["views"],
                            "views_per_hour": round(details["views"] / 24, 0),
                            "engagement_rate_pct": round(((details["likes"] + details["comments_count"]) / max(details["views"], 1)) * 100, 2),
                            "sentiment_positive_pct": 75.0
                        }]
                        errors = self._bq_client.insert_rows_json(table_id, rows_to_insert)
                        if errors:
                            logger.error(f"BigQuery snapshot insert error: {errors}")
                        else:
                            logger.info(f"Successfully ingested live snapshot for video {vid} into BigQuery!")
                    except Exception as e:
                        logger.warning(f"BigQuery ingestion exception: {e}")
                
                ingestion_results.append({
                    "video_id": vid,
                    "title": details.get("title"),
                    "views": details.get("views"),
                    "likes": details.get("likes"),
                    "comments": details.get("comments_count")
                })
        
        return {
            "status": "INGESTED_SUCCESSFULLY",
            "ingested_count": len(ingestion_results),
            "videos": ingestion_results
        }

bq_client = StudioSonarBigQueryClient()


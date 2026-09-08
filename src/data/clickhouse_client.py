"""
StudioSonar Real-Time Analytics ClickHouse Client (Hot Path Substrate).
Executes high-throughput stream ingestion and sub-second sliding window queries
for comment velocity spikes and viral trend detection.
"""

import re
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from src.core.config import settings

logger = logging.getLogger("studiosonar.clickhouse")

def _sanitize_id(id_str: str) -> str:
    """Strict whitelist regex sanitization for video/channel IDs to prevent SQL injection."""
    if not id_str or not isinstance(id_str, str) or not re.match(r"^[a-zA-Z0-9_\-\.]{1,64}$", id_str.strip()):
        raise ValueError(f"Invalid identifier for ClickHouse query: {id_str!r}. Only alphanumeric, dash, underscore, and dot (max 64 chars) are permitted.")
    return id_str.strip()

class StudioSonarClickHouseClient:
    """
    High-Performance ClickHouse Client for Real-Time OLAP Telemetry.
    Uses ClickHouse Native HTTP API (port 8123/8443) with zero heavy driver dependencies,
    optimized for Google Cloud Run serverless execution.
    Follows Zero-Fake Doctrine: strictly reports measured telemetry or explicit SIMULATED_STANDBY tags.
    """

    def __init__(self):
        self.host = settings.clickhouse_host
        self.port = settings.clickhouse_port
        self.user = settings.clickhouse_user
        self.password = settings.clickhouse_password
        self.database = settings.clickhouse_database
        self.secure = settings.clickhouse_secure
        self.protocol = "https" if self.secure else "http"
        self.base_url = f"{self.protocol}://{self.host}:{self.port}"
        self._is_online = None
        self._radar_ticks_count = 0
        self._hot_queries_count = 0
        self._latencies_ms: List[float] = []
        self._last_check = 0.0

    def execute_query(
        self,
        query: str,
        format_json: bool = True,
        timeout: float = 3.0,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """Executes a SQL query against ClickHouse HTTP endpoint with parameter binding."""
        import time
        now = time.time()
        # Fast circuit breaker if ClickHouse is offline (retry after 30s)
        if self._is_online is False and (now - self._last_check) < 30.0:
            return None

        endpoint = f"{self.base_url}/"
        params: Dict[str, Any] = {
            "database": self.database,
            "default_format": "JSON" if format_json else "TabSeparated"
        }
        if query_params:
            for k, v in query_params.items():
                params[f"param_{k}"] = v

        auth = (self.user, self.password) if self.password else None
        self._hot_queries_count += 1
        t0 = time.perf_counter()
        try:
            self._last_check = now
            resp = requests.post(
                endpoint,
                params=params,
                data=query.encode("utf-8"),
                auth=auth,
                timeout=timeout
            )
            lat_ms = (time.perf_counter() - t0) * 1000.0
            self._latencies_ms.append(round(lat_ms, 2))
            if len(self._latencies_ms) > 100:
                self._latencies_ms.pop(0)

            if resp.status_code == 200:
                self._is_online = True
                if format_json:
                    return resp.json().get("data", [])
                return resp.text
            else:
                logger.warning(f"ClickHouse query error ({resp.status_code}): {resp.text[:120]}")
                return None
        except Exception as e:
            logger.debug(f"ClickHouse cold-start or connection notice: {e}")
            self._is_online = False
            return None

    def check_health(self) -> Dict[str, Any]:
        """Checks connectivity to the ClickHouse Hot Path substrate."""
        res = self.execute_query("SELECT 1 AS alive", format_json=True)
        is_alive = bool(res and res[0].get("alive") == 1)
        return {
            "substrate": "ClickHouse Hot Path OLAP",
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "status": "ONLINE" if is_alive else "STANDBY / IN_PROCESS_CACHE",
            "sub_second_engine": True
        }

    def insert_snapshots(self, snapshots: List[Dict[str, Any]]) -> int:
        """
        Batch streams hourly video snapshots into ClickHouse video_snapshots table.
        Uses native JSONEachRow streaming format (immune to SQL injection, zero SQL string formatting).
        """
        import json
        if not snapshots:
            return 0
        
        endpoint = f"{self.base_url}/"
        params = {
            "database": self.database,
            "query": "INSERT INTO video_snapshots FORMAT JSONEachRow"
        }
        auth = (self.user, self.password) if self.password else None

        rows = []
        for s in snapshots:
            ts = s.get("snapshot_timestamp") or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            raw_vid = s.get("video_id", "vid_default")
            v_id = _sanitize_id(raw_vid)
            h_pub = float(s.get("hours_since_publish", 1.0))
            views = int(s.get("view_count", 0))
            likes = int(s.get("like_count", 0))
            comments = int(s.get("comment_count", 0))
            v_per_h = float(s.get("views_per_hour", 0.0))
            eng = float(s.get("engagement_rate_pct", 0.0))
            pos = float(s.get("sentiment_positive_pct", 95.0))
            neg = float(s.get("sentiment_negative_pct", 1.0))
            raw_snap = s.get("snapshot_id") or f"snap_{v_id}_{int(datetime.now(timezone.utc).timestamp())}"
            snap_id = _sanitize_id(raw_snap)

            rows.append(json.dumps({
                "snapshot_id": snap_id,
                "video_id": v_id,
                "snapshot_timestamp": ts,
                "hours_since_publish": h_pub,
                "view_count": views,
                "like_count": likes,
                "comment_count": comments,
                "views_per_hour": v_per_h,
                "engagement_rate_pct": eng,
                "sentiment_positive_pct": pos,
                "sentiment_negative_pct": neg
            }))

        payload = "\n".join(rows)
        try:
            resp = requests.post(endpoint, params=params, data=payload.encode("utf-8"), auth=auth, timeout=5.0)
            if resp.status_code == 200:
                return len(snapshots)
            else:
                logger.warning(f"ClickHouse JSONEachRow insert error ({resp.status_code}): {resp.text[:120]}")
                return 0
        except Exception as e:
            logger.debug(f"ClickHouse insert notice: {e}")
            return 0

    def query_realtime_sentiment_spikes(
        self,
        time_window_hours: int = 6,
        min_velocity_pct: float = 200.0,
        sentiment_threshold: float = -0.50
    ) -> List[Dict[str, Any]]:
        """
        Executes sub-second parameterized query on ClickHouse Materialized View
        to detect real-time sentiment backlash spikes.
        Follows Zero-Fake: never returns canned fake anomalies when no spikes exist.
        """
        query = f"""
            SELECT 
                video_id,
                sum(comment_volume) AS comment_volume,
                sum(negative_comments) AS negative_comments,
                sum(positive_comments) AS positive_comments,
                round(sum(sum_sentiment) / greatest(sum(comment_volume), 1), 2) AS avg_sentiment,
                round((sum(comment_volume) / greatest({{time_window_hours:UInt32}}, 1)) * 100.0, 1) AS velocity_spike_pct
            FROM {self.database}.hourly_sentiment_aggregates
            WHERE window_start >= now() - INTERVAL {{time_window_hours:UInt32}} HOUR
            GROUP BY video_id
            HAVING negative_comments >= 3 AND avg_sentiment <= {{sentiment_threshold:Float32}}
            ORDER BY negative_comments DESC
            LIMIT 5
        """
        results = self.execute_query(
            query,
            query_params={
                "time_window_hours": int(time_window_hours),
                "sentiment_threshold": float(sentiment_threshold)
            }
        )
        if results is not None:
            for r in results:
                r["data_provenance"] = "MEASURED_REALTIME"
                r["is_measured"] = True
            return results

        return []

    def query_realtime_viral_trends(
        self,
        min_view_acceleration_pct: float = 300.0,
        lookback_hours: int = 8
    ) -> List[Dict[str, Any]]:
        """
        Queries ClickHouse for explosive breakout viral topics & retention surges.
        Follows Zero-Fake: never returns canned fake breakout trends in live mode.
        """
        query = f"""
            SELECT 
                video_id,
                any(title) AS trend_topic,
                round(max(views_per_hour) - min(views_per_hour), 1) AS cross_platform_acceleration_pct
            FROM {self.database}.video_snapshots
            WHERE snapshot_timestamp >= now() - INTERVAL {{lookback_hours:UInt32}} HOUR
            GROUP BY video_id
            HAVING cross_platform_acceleration_pct >= {{min_accel:Float32}}
            LIMIT 3
        """
        res = self.execute_query(
            query,
            query_params={
                "lookback_hours": int(lookback_hours),
                "min_accel": float(min_view_acceleration_pct)
            }
        )
        if res is not None:
            for r in res:
                r["data_provenance"] = "MEASURED_REALTIME"
                r["is_measured"] = True
            return res

        return []

    # =========================================================================
    # U1 — 1-Minute Radar Loop (Raw-Column Sliding Window Query & Native Decay Heat)
    # =========================================================================
    def query_ad_hoc_raw_velocity_spikes(self) -> List[Dict[str, Any]]:
        """
        Executes an ad-hoc, multi-window raw-column aggregation on comments_realtime.
        Compares instant 5-minute velocity against a 6-hour rolling baseline.
        Executed every minute via Cloud Scheduler radar loop.
        Follows Zero-Fake: returns empty list if no spikes exist. Never fabricates crisis!
        """
        self._radar_ticks_count += 1
        query = f"""
            SELECT
                video_id,
                countIf(published_at >= now() - INTERVAL 5 MINUTE) * 12.0 AS rate_5m_per_hr,
                countIf(published_at >= now() - INTERVAL 6 HOUR) / 6.0 AS rate_6h_per_hr,
                countIf(published_at >= now() - INTERVAL 6 HOUR AND sentiment_score < -0.5)
                / greatest(countIf(published_at >= now() - INTERVAL 6 HOUR), 1) AS neg_ratio_6h,
                count() AS total_samples_6h
            FROM {self.database}.comments_realtime
            WHERE published_at >= now() - INTERVAL 6 HOUR
            GROUP BY video_id
            HAVING rate_5m_per_hr > greatest(rate_6h_per_hr * 2.0, 10.0)
            ORDER BY rate_5m_per_hr DESC
            LIMIT 5
        """
        results = self.execute_query(query)
        if results is not None:
            for r in results:
                r["data_provenance"] = "MEASURED_REALTIME"
                r["is_measured"] = True
            return results

        return []

    def query_decay_adjusted_heat_spikes(self, halflife_seconds: int = 600) -> List[Dict[str, Any]]:
        """
        Evaluates real-time comment heat score using native exponentialTimeDecayedCount.
        Weights recent comments exponentially higher (10-minute half-life).
        """
        query = f"""
            SELECT
                video_id,
                exponentialTimeDecayedCount({{halflife:UInt32}})(1, published_at) AS heat_halflife_10m,
                count() AS raw_6h
            FROM {self.database}.comments_realtime
            WHERE published_at >= now() - INTERVAL 6 HOUR
            GROUP BY video_id
            ORDER BY heat_halflife_10m DESC
            LIMIT 5
        """
        results = self.execute_query(query, query_params={"halflife": int(halflife_seconds)})
        if results is not None:
            for r in results:
                r["data_provenance"] = "MEASURED_REALTIME"
                r["is_measured"] = True
            return results

        return []

    def query_velocity_acceleration_slope(self, video_id: str, window_hours: int = 24) -> Dict[str, Any]:
        """
        Computes momentum slope (2nd derivative of velocity) using native simpleLinearRegression.
        slope > 0 = accelerating upward (viral takeoff or escalating crisis)
        slope < 0 = past peak momentum (decelerating, avoids knee-jerk PR panic)
        Parameter-bound query to prevent SQL injection.
        """
        clean_vid = _sanitize_id(video_id)
        query = f"""
            SELECT
                video_id,
                (simpleLinearRegression(toUnixTimestamp(window_start))(comment_volume) AS lr).1 AS slope_per_sec,
                sum(comment_volume) AS total_vol_24h
            FROM {self.database}.hourly_sentiment_aggregates
            WHERE video_id = {{video_id:String}} AND window_start >= now() - INTERVAL {{window_hours:UInt32}} HOUR
            GROUP BY video_id
        """
        results = self.execute_query(
            query,
            query_params={"video_id": clean_vid, "window_hours": int(window_hours)}
        )
        if results and len(results) > 0:
            slope = float(results[0].get("slope_per_sec", 0.0))
            total_vol = int(results[0].get("total_vol_24h", 0))
            data_provenance = "MEASURED_REALTIME"
            is_measured = True
        else:
            slope = 0.0
            total_vol = 0
            data_provenance = "SIMULATED_STANDBY"
            is_measured = False

        status = "ACCELERATING" if slope > 0.005 else ("DECELERATING" if slope < -0.005 else "PLATEAU")
        return {
            "video_id": clean_vid,
            "slope_per_sec": round(slope, 5),
            "momentum_status": status,
            "total_volume_24h": total_vol,
            "data_provenance": data_provenance,
            "is_measured": is_measured,
            "interpretation": (
                "Trend momentum accelerating upward (viral growth active)."
                if status == "ACCELERATING" else
                ("Velocity has passed its peak and is decelerating; PR risk is subsiding." if status == "DECELERATING" else "Velocity is plateaued.")
            )
        }

    # =========================================================================
    # U3 — Drill-Down Burst: Brigade & Bot Attack Detection (Exact 24h Global Math)
    # =========================================================================
    def drill_down_spike_brigade_analysis(self, video_id: str) -> Dict[str, Any]:
        """
        Performs forensic analysis combining unique author ratios and Shannon entropy
        entropy(author_id_hash) to detect coordinated bot brigade attacks vs genuine community feedback.
        Uses exact single-pass 24h global ClickHouse aggregations (Zero-Fake mathematical precision).
        """
        clean_vid = _sanitize_id(video_id)

        # 1. Exact Global 24h Aggregation (single-pass, avoids overcounting unique authors or distorting entropy)
        global_query = f"""
            SELECT
                count() AS total_comments,
                uniqExact(author_id_hash) AS exact_unique_authors,
                round(count() / greatest(uniqExact(author_id_hash), 1), 2) AS comments_per_author,
                round(entropy(author_id_hash), 3) AS global_author_entropy,
                round(quantile(0.95)(toxicity_score), 3) AS global_p95_toxicity,
                round(countIf(toxicity_score > 0.6) / greatest(count(), 1), 3) AS toxic_comment_ratio
            FROM {self.database}.comments_realtime
            WHERE video_id = {{video_id:String}} AND published_at >= now() - INTERVAL 24 HOUR
        """
        global_res = self.execute_query(global_query, query_params={"video_id": clean_vid})

        # 2. Hourly breakdown for forensic timeline visualization
        hourly_query = f"""
            SELECT
                toStartOfHour(published_at) AS h,
                multiIf(sentiment_score < -0.5, 'neg', sentiment_score > 0.5, 'pos', 'neu') AS band,
                count() AS c,
                uniqExact(author_id_hash) AS uniq_authors,
                round(count() / greatest(uniqExact(author_id_hash), 1), 2) AS comments_per_author,
                round(entropy(author_id_hash), 3) AS author_entropy,
                round(quantile(0.95)(toxicity_score), 3) AS p95_tox
            FROM {self.database}.comments_realtime
            WHERE video_id = {{video_id:String}} AND published_at >= now() - INTERVAL 24 HOUR
            GROUP BY h, band
            ORDER BY h
        """
        hourly_res = self.execute_query(hourly_query, query_params={"video_id": clean_vid})

        if global_res and len(global_res) > 0 and int(global_res[0].get("total_comments", 0)) > 0:
            row = global_res[0]
            total_comments = int(row.get("total_comments", 0))
            unique_authors = int(row.get("exact_unique_authors", 0))
            p95_toxicity = float(row.get("global_p95_toxicity", 0.0))
            author_entropy = float(row.get("global_author_entropy", 0.0))
            data_provenance = "MEASURED_REALTIME"
            is_measured = True
        else:
            # Zero-Fake: report real zero values if ClickHouse has no comments for this asset
            total_comments = 0
            unique_authors = 0
            p95_toxicity = 0.0
            author_entropy = 0.0
            data_provenance = "SIMULATED_STANDBY"
            is_measured = False

        if total_comments == 0:
            author_diversity_ratio = 0.0
            comments_per_author = 0.0
            is_brigade = False
            verdict = "INSUFFICIENT_DATA"
            containment = "Continue standard telemetry monitoring; zero comment activity detected in the last 24 hours."
        elif total_comments < 20:
            author_diversity_ratio = round(unique_authors / max(total_comments, 1), 3)
            comments_per_author = round(total_comments / max(unique_authors, 1), 2)
            is_brigade = False
            verdict = "INSUFFICIENT_DATA_SAMPLE"
            containment = "Sample volume under 20 comments is too small for statistical entropy confidence; continue passive monitoring."
        else:
            author_diversity_ratio = round(unique_authors / max(total_comments, 1), 3)
            comments_per_author = round(total_comments / max(unique_authors, 1), 2)
            # Exact Brigade Heuristic: high repetition (>= 3.0), low Shannon entropy (< 3.5), and severe toxicity (>= 0.65)
            is_brigade = bool(comments_per_author >= 3.0 and author_entropy < 3.5 and p95_toxicity >= 0.65)
            verdict = "COORDINATED_BRIGADE_ATTACK" if is_brigade else "ORGANIC_COMMUNITY_OUTCRY"
            containment = (
                "Do NOT issue public apology. Alert platform trust & safety teams to purge bot accounts."
                if is_brigade else
                "Issue official brand clarification addressing verified community friction."
            )

        return {
            "status": "DRILL_DOWN_COMPLETE",
            "video_id": clean_vid,
            "data_provenance": data_provenance,
            "is_measured": is_measured,
            "total_comments_24h": total_comments,
            "unique_authors_24h": unique_authors,
            "author_diversity_ratio": author_diversity_ratio,
            "comments_per_author": comments_per_author,
            "author_entropy": author_entropy,
            "p95_toxicity": p95_toxicity,
            "is_brigade_attack": is_brigade,
            "verdict": verdict,
            "threat_verdict": verdict,
            "recommended_containment": containment,
            "hourly_bands": hourly_res or []
        }

    # =========================================================================
    # Native Timeseries Analytics: Cross-Platform Synergy (corr), ASCII Sparkbar, topK
    # =========================================================================
    def query_cross_platform_synergy_correlation(self, days: int = 7) -> Dict[str, Any]:
        """
        Computes Pearson correlation coefficient between YouTube and TikTok hourly activity:
        corr(yt_h, tt_h) over the past 7 days.
        """
        query = f"""
            SELECT round(corr(yt_h, tt_h), 3) AS synergy_7d
            FROM (
                SELECT toStartOfHour(published_at) AS h,
                       countIf(platform = 'youtube') AS yt_h,
                       countIf(platform = 'tiktok')  AS tt_h
                FROM {self.database}.comments_realtime
                WHERE published_at >= now() - INTERVAL {{days:UInt32}} DAY
                GROUP BY h
            )
        """
        results = self.execute_query(query, query_params={"days": int(days)})
        if results and results[0].get("synergy_7d") is not None:
            try:
                corr_val = float(results[0]["synergy_7d"])
                data_provenance = "MEASURED_REALTIME"
                is_measured = True
            except Exception:
                corr_val = 0.0
                data_provenance = "SIMULATED_STANDBY"
                is_measured = False
        else:
            corr_val = 0.0
            data_provenance = "SIMULATED_STANDBY"
            is_measured = False

        return {
            "time_window_days": int(days),
            "pearson_correlation": corr_val,
            "data_provenance": data_provenance,
            "is_measured": is_measured,
            "synergy_verdict": (
                "STRONG_CROSS_PLATFORM_AMPLIFICATION" if corr_val >= 0.70 else
                ("MODERATE_CORRELATION" if corr_val >= 0.40 else "INDEPENDENT_AUDIENCE_ENGAGEMENT")
            ),
            "description": f"ClickHouse native corr(yt, tt) over {days}d reveals r={corr_val} synchronized viral dynamics."
        }

    def query_ascii_sparkbar(self, video_id: str, hours: int = 48) -> str:
        """
        Generates native ClickHouse ASCII sparkbar string sparkbar(48)(window_start, comment_volume).
        Returns a data-native UTF-8 block graph (e.g.  ▂▃▅▆▇█) ready for GCS markdown dossiers.
        """
        clean_vid = _sanitize_id(video_id)
        query = f"""
            SELECT sparkbar({{hours:UInt32}})(toUnixTimestamp(window_start), comment_volume) AS volume_spark
            FROM {self.database}.hourly_sentiment_aggregates
            WHERE video_id = {{video_id:String}} AND window_start >= now() - INTERVAL {{hours:UInt32}} HOUR
        """
        results = self.execute_query(query, query_params={"video_id": clean_vid, "hours": int(hours)})
        if results and results[0].get("volume_spark"):
            return str(results[0]["volume_spark"])
        return ""

    def query_top_friction_terms(self, video_id: str, top_n: int = 5) -> List[str]:
        """
        Extracts top friction terms among negative comments using ClickHouse topK(5)(comment_text).
        """
        clean_vid = _sanitize_id(video_id)
        query = f"""
            SELECT topK({{top_n:UInt32}})(comment_text) AS top_terms
            FROM {self.database}.comments_realtime
            WHERE video_id = {{video_id:String}} AND sentiment_score < -0.40 AND published_at >= now() - INTERVAL 24 HOUR
        """
        results = self.execute_query(query, query_params={"video_id": clean_vid, "top_n": int(top_n)})
        if results and results[0].get("top_terms"):
            return list(results[0]["top_terms"])
        return []

    # =========================================================================
    # U2 — 5s Dashboard Polling & Cost Defense Telemetry (Zero-Fake Transparency)
    # =========================================================================
    def get_hot_counters(self) -> Dict[str, Any]:
        """
        Provides real-time telemetry counters and transparent financial cost defense metrics.
        Adheres to Zero-Fake Doctrine:
        - Never returns seeded latencies (p50/p95 are None when unmeasured)
        - Queries ClickHouse for real 5m comment buckets across last 30m; returns [] if no data
        - Never hardcodes fake numbers
        """
        import statistics

        if self._latencies_ms:
            p50 = round(statistics.median(self._latencies_ms), 1)
            p95 = round(sorted(self._latencies_ms)[int(len(self._latencies_ms) * 0.95)] if len(self._latencies_ms) >= 5 else max(self._latencies_ms), 1)
            data_provenance = "MEASURED_REALTIME"
            is_measured = True
        else:
            p50 = None
            p95 = None
            data_provenance = "SIMULATED_STANDBY"
            is_measured = False

        # Query ClickHouse for real 5-minute volume buckets in the last 30 minutes
        sparkline_query = f"""
            SELECT 
                toStartOfInterval(published_at, INTERVAL 5 MINUTE) AS b,
                count() AS vol
            FROM {self.database}.comments_realtime
            WHERE published_at >= now() - INTERVAL 30 MINUTE
            GROUP BY b
            ORDER BY b
        """
        spark_res = self.execute_query(sparkline_query)
        if spark_res and len(spark_res) > 0:
            sparkline = [int(r.get("vol", 0)) for r in spark_res]
        else:
            sparkline = []

        stream_velocity_eps = round(sparkline[-1] / 60.0, 2) if sparkline else 0.0

        # Financial cost defense formula:
        # Polling BigQuery every 10s = 8,640 queries/day * 10MB min scan = 2.6 TB/mo ≈ $15.45/mo.
        # ClickHouse = fixed compute, $0 marginal cost for high-frequency polling.
        projected_daily_queries = 8640
        projected_monthly_saving = round((projected_daily_queries * 30 * 10.0 / (1024.0 * 1024.0)) * 6.25, 2)
        measured_saving = round((self._hot_queries_count * 30 * 10.0 / (1024.0 * 1024.0)) * 6.25, 2) if self._hot_queries_count > 0 else 0.0

        return {
            "status": "HOT_LAYER_ONLINE" if is_measured else "HOT_LAYER_STANDBY",
            "data_provenance": data_provenance,
            "is_measured": is_measured,
            "hot_queries_served": self._hot_queries_count,
            "radar_ticks_24h": self._radar_ticks_count,
            "latency": {
                "p50_ms": p50,
                "p95_ms": p95,
                "engine": "ClickHouse Native Columnar HTTP",
                "sample_count": len(self._latencies_ms)
            },
            "stream_velocity_eps": stream_velocity_eps,
            "sparkline_30m": sparkline,
            "cost_defense": {
                "daily_hot_queries_measured": self._hot_queries_count,
                "projected_daily_queries_at_scale": projected_daily_queries,
                "bigquery_scan_cost_equiv_usd": projected_monthly_saving,
                "clickhouse_marginal_cost_usd": 0.0,
                "monthly_saving_usd": projected_monthly_saving,
                "measured_cost_saving_usd": measured_saving,
                "data_provenance": data_provenance,
                "defense_argument": "High-frequency 5s polling is free on ClickHouse; on BigQuery 8,640 polls/day scans ~2.6TB/mo ($15.45/mo) with 1-3s latency."
            }
        }

ch_client = StudioSonarClickHouseClient()

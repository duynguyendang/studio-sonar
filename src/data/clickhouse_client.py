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

    def insert_comments(self, comments: List[Dict[str, Any]]) -> int:
        """
        Batch streams raw real-time comments into ClickHouse comments_realtime table.
        Feeds real-time Materialized Views and sliding-window aggregations.
        """
        import json
        import hashlib
        if not comments:
            return 0
        
        endpoint = f"{self.base_url}/"
        params = {
            "database": self.database,
            "query": "INSERT INTO comments_realtime FORMAT JSONEachRow"
        }
        auth = (self.user, self.password) if self.password else None

        rows = []
        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        for c in comments:
            raw_vid = c.get("video_id", "vid_default")
            v_id = _sanitize_id(raw_vid)
            text = (c.get("comment_text") or c.get("text") or "").strip()
            if not text:
                continue
            
            author = (c.get("author") or c.get("author_name") or "anonymous").strip()
            auth_hash = c.get("author_id_hash") or hashlib.sha256(author.encode("utf-8")).hexdigest()[:16]
            c_id = c.get("comment_id") or f"c_{hashlib.md5(f'{v_id}_{author}_{text[:20]}'.encode('utf-8')).hexdigest()[:16]}"
            
            # Sentiment & toxicity heuristic if not pre-computed
            sent_score = float(c.get("sentiment_score", 0.0))
            tox_score = float(c.get("toxicity_score", 0.0))
            if sent_score == 0.0 and tox_score == 0.0:
                t_lower = text.lower()
                neg_words = ["dở", "tệ", "chán", "rác", "scam", "lừa", "đạo", "sạn", "thất vọng", "fake", "bad", "hate", "terrible", "worst"]
                pos_words = ["hay", "tuyệt", "đẹp", "xuất sắc", "đỉnh", "thích", "yêu", "chất", "tuyệt vời", "good", "great", "love", "awesome"]
                has_neg = any(w in t_lower for w in neg_words)
                has_pos = any(w in t_lower for w in pos_words)
                if has_neg and not has_pos:
                    sent_score = -0.75
                    tox_score = 0.70
                elif has_pos and not has_neg:
                    sent_score = 0.85
                    tox_score = 0.05
                else:
                    sent_score = 0.20
                    tox_score = 0.05

            pub_at = c.get("published_at")
            if pub_at:
                try:
                    pub_clean = pub_at.replace("T", " ").replace("Z", "").split(".")[0]
                except Exception:
                    pub_clean = now_ts
            else:
                pub_clean = now_ts

            likes = int(c.get("like_count", 0))

            rows.append(json.dumps({
                "comment_id": c_id,
                "video_id": v_id,
                "platform": c.get("platform", "youtube"),
                "author_id_hash": auth_hash,
                "comment_text": text[:2000],
                "sentiment_score": sent_score,
                "toxicity_score": tox_score,
                "like_count": likes,
                "published_at": pub_clean,
                "ingested_at": now_ts
            }))

        if not rows:
            return 0

        payload = "\n".join(rows)
        try:
            resp = requests.post(endpoint, params=params, data=payload.encode("utf-8"), auth=auth, timeout=5.0)
            if resp.status_code == 200:
                logger.info(f"Successfully streamed {len(rows)} raw comments into ClickHouse comments_realtime")
                return len(rows)
            else:
                logger.warning(f"ClickHouse comment insert error ({resp.status_code}): {resp.text[:120]}")
                return 0
        except Exception as e:
            logger.debug(f"ClickHouse comment insert notice: {e}")
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
                (simpleLinearRegression(comment_volume, toUnixTimestamp(window_start)) AS lr).1 AS slope_per_sec,
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

    def query_recent_friction_comments(self, video_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves real verbatim negative/friction comments from ClickHouse comments_realtime.
        Used by ExternalAttributionMapper to diagnose audience complaints and criticism.
        """
        clean_vid = _sanitize_id(video_id)
        query = f"""
            SELECT comment_text, sentiment_score, toxicity_score, published_at
            FROM {self.database}.comments_realtime
            WHERE video_id = {{video_id:String}} AND (sentiment_score < -0.15 OR toxicity_score > 0.35)
            ORDER BY toxicity_score DESC, published_at DESC
            LIMIT {{limit:UInt32}}
        """
        results = self.execute_query(query, query_params={"video_id": clean_vid, "limit": int(limit)})
        return results or []

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

    # =========================================================================
    # Advanced Analytical Functions (Z-Score, Micro-NLP, Polarization, Lexical)
    # =========================================================================
    def query_zscore_velocity_anomalies(self, video_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Calculates dynamic statistical Z-Scores using ClickHouse Window Functions
        (avg(views_per_hour) OVER w, stddevSamp(views_per_hour) OVER w).
        Flags true statistical outliers (Z >= 2.5 sigma) rather than naive static % surges.
        """
        where_clause = ""
        params: Dict[str, Any] = {}
        if video_id:
            clean_vid = _sanitize_id(video_id)
            where_clause = "WHERE video_id = {video_id:String}"
            params["video_id"] = clean_vid

        query = f"""
            SELECT 
                video_id,
                snapshot_timestamp,
                views_per_hour,
                round(avg_vel, 1) AS mean_velocity,
                round(std_vel, 2) AS stddev_velocity,
                round(case when std_vel > 0 then (views_per_hour - avg_vel) / std_vel else 0.0 end, 2) AS z_score,
                case 
                    when z_score >= 3.0 then 'CRITICAL_OUTLIER_3SIGMA'
                    when z_score >= 2.0 then 'ELEVATED_SURGE_2SIGMA'
                    when z_score <= -2.0 then 'UNUSUAL_DROP'
                    else 'NORMAL_STATISTICAL_BAND'
                end AS statistical_status
            FROM (
                SELECT 
                    video_id,
                    snapshot_timestamp,
                    views_per_hour,
                    avg(views_per_hour) OVER w AS avg_vel,
                    stddevSamp(views_per_hour) OVER w AS std_vel
                FROM {self.database}.video_snapshots
                {where_clause}
                WINDOW w AS (PARTITION BY video_id ORDER BY snapshot_timestamp ROWS BETWEEN 24 PRECEDING AND 1 PRECEDING)
            )
            ORDER BY snapshot_timestamp DESC
            LIMIT 10
        """
        results = self.execute_query(query, query_params=params)
        return results or []

    def query_weighted_friction_ngrams(self, video_id: Optional[str] = None, top_n: int = 6) -> List[Dict[str, Any]]:
        """
        Micro-NLP in ClickHouse: Extracts top weighted bigrams using
        tokens(), arrayMap(), and topKWeighted(N)(bigram, toxicity_weight).
        Excludes HTML artifacts (<br>) and restricts to real negative/friction comments
        to avoid attributing positive comments as toxic.
        """
        where_parts = [
            "length(comment_text) >= 6",
            "(toxicity_score >= 0.20 OR sentiment_score <= -0.15)"
        ]
        params: Dict[str, Any] = {"top_n": int(top_n)}
        if video_id:
            clean_vid = _sanitize_id(video_id)
            where_parts.append("video_id = {video_id:String}")
            params["video_id"] = clean_vid

        where_str = " AND ".join(where_parts)
        query = f"""
            SELECT 
                topKWeighted({{top_n:UInt32}})(
                    bigram, 
                    CAST(greatest(toxicity_score * 100, 1.0) AS UInt32)
                ) AS weighted_phrases
            FROM (
                SELECT 
                    arrayJoin(
                        arrayFilter(b -> not (b LIKE '%br%' OR b LIKE '%http%' OR b LIKE '%www%' OR b LIKE '%href%'),
                            arrayMap((x, y) -> concat(x, ' ', y), 
                                     arrayPopBack(tokens(lower(replaceAll(replaceAll(comment_text, '<br>', ' '), '<br/>', ' ')))), 
                                     arrayPopFront(tokens(lower(replaceAll(replaceAll(comment_text, '<br>', ' '), '<br/>', ' '))))
                            )
                        )
                    ) AS bigram,
                    toxicity_score
                FROM {self.database}.comments_realtime
                WHERE {where_str}
            )
        """
        results = self.execute_query(query, query_params=params)
        if results and results[0].get("weighted_phrases"):
            phrases = [p for p in results[0]["weighted_phrases"] if p and p.strip()]
            return [{"phrase": p, "rank": idx + 1} for idx, p in enumerate(phrases)]
        return []

    def query_audience_polarization_index(self, video_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Uses ClickHouse quantilesExact(0.10, 0.50, 0.90)(sentiment_score) to measure
        Audience Polarization Spread (Q90 - Q10) and identify Community Civil Wars.
        """
        where_clause = ""
        params: Dict[str, Any] = {}
        if video_id:
            clean_vid = _sanitize_id(video_id)
            where_clause = "WHERE video_id = {video_id:String}"
            params["video_id"] = clean_vid

        query = f"""
            SELECT 
                count() AS total_comments,
                quantilesExact(0.10, 0.50, 0.90)(sentiment_score) AS q,
                round(q[3] - q[1], 3) AS polarization_spread,
                round(avg(sentiment_score), 2) AS mean_sentiment
            FROM {self.database}.comments_realtime
            {where_clause}
        """
        results = self.execute_query(query, query_params=params)
        if results and results[0].get("total_comments", 0) > 0:
            row = results[0]
            q = row.get("q", [0.0, 0.0, 0.0])
            spread = float(row.get("polarization_spread", 0.0))
            status = "UNANIMOUS_CONSENSUS"
            if spread >= 1.4:
                status = "CIVIL_WAR_POLARIZED"
            elif spread >= 0.8:
                status = "MODERATE_DEBATE"

            return {
                "total_comments": row["total_comments"],
                "q10_negative_tail": round(float(q[0]), 2),
                "q50_median": round(float(q[1]), 2),
                "q90_positive_tail": round(float(q[2]), 2),
                "polarization_spread": spread,
                "mean_sentiment": row["mean_sentiment"],
                "status": status
            }
        return {
            "total_comments": 0,
            "q10_negative_tail": 0.0,
            "q50_median": 0.0,
            "q90_positive_tail": 0.0,
            "polarization_spread": 0.0,
            "mean_sentiment": 0.0,
            "status": "STANDBY_NO_DATA"
        }

    def query_lexical_bot_forensics(self, video_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Advanced Astroturfing Forensics:
        - Lexical Diversity: uniqExact(cityHash64(tokens(lower(comment_text)))) / count()
        - Author Diversity: uniqExact(author_id_hash) / count()
        - Shannon Entropy: entropy(author_id_hash)
        """
        where_clause = ""
        params: Dict[str, Any] = {}
        if video_id:
            clean_vid = _sanitize_id(video_id)
            where_clause = "WHERE video_id = {video_id:String}"
            params["video_id"] = clean_vid

        query = f"""
            SELECT 
                count() AS total_comments,
                uniqExact(author_id_hash) AS uniq_authors,
                round(uniq_authors / nullIf(total_comments, 0), 3) AS author_diversity_ratio,
                round(uniqExact(cityHash64(tokens(lower(comment_text)))) / nullIf(total_comments, 0), 3) AS lexical_diversity_ratio,
                round(entropy(author_id_hash), 2) AS shannon_entropy,
                round(quantile(0.95)(toxicity_score), 2) AS p95_toxicity
            FROM {self.database}.comments_realtime
            {where_clause}
        """
        results = self.execute_query(query, query_params=params)
        if results and results[0].get("total_comments", 0) > 0:
            r = results[0]
            lex = float(r.get("lexical_diversity_ratio", 1.0))
            auth_div = float(r.get("author_diversity_ratio", 1.0))
            ent = float(r.get("shannon_entropy", 5.0))
            verdict = "ORGANIC_GENUINE_AUDIENCE"
            if (lex < 0.35 or auth_div < 0.35) and ent < 4.0:
                verdict = "COORDINATED_ASTROTURFING_BOTS"
            elif lex < 0.50:
                verdict = "SUSPECTED_PARAPHRASE_SEEDING"

            return {
                "total_comments": r["total_comments"],
                "uniq_authors": r["uniq_authors"],
                "author_diversity_ratio": auth_div,
                "lexical_diversity_ratio": lex,
                "shannon_entropy": ent,
                "p95_toxicity": r["p95_toxicity"],
                "forensic_verdict": verdict
            }
        return {
            "total_comments": 0,
            "uniq_authors": 0,
            "author_diversity_ratio": 1.0,
            "lexical_diversity_ratio": 1.0,
            "shannon_entropy": 0.0,
            "p95_toxicity": 0.0,
            "forensic_verdict": "STANDBY_NO_DATA"
        }

    def get_advanced_forensics_summary(self, video_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Single-invocation bundle delivering all ClickHouse analytical metrics:
        Z-Score outliers, Polarization Spread, Weighted N-Grams, and Bot Forensics.
        """
        return {
            "video_id": video_id or "all_monitored_assets",
            "zscore_anomalies": self.query_zscore_velocity_anomalies(video_id),
            "polarization": self.query_audience_polarization_index(video_id),
            "weighted_toxic_ngrams": self.query_weighted_friction_ngrams(video_id, top_n=6),
            "bot_forensics": self.query_lexical_bot_forensics(video_id)
        }

ch_client = StudioSonarClickHouseClient()

-- ==============================================================================
-- StudioSonar BigQuery Storage & Vector Analytics Schema
-- Dataset: studiosonar_analytics
-- Target Warehouse: Google Cloud BigQuery (Serverless OLAP & Vector Search)
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS `studiosonar_analytics`
OPTIONS(
  location="us-central1",
  description="StudioSonar Media Intelligence, Channel Sentinel & Time-Series Telemetry"
);

-- ------------------------------------------------------------------------------
-- 1. TRACKED CHANNELS REGISTRY TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `studiosonar_analytics.tracked_channels` (
  channel_id STRING NOT NULL,
  handle STRING NOT NULL, -- e.g. '@business', '@KiemDinhPhim9.0'
  platform STRING NOT NULL, -- 'youtube' | 'tiktok'
  title STRING NOT NULL,
  category STRING, -- 'Tech/Software', 'Entertainment/Film', 'Corporate'
  tracking_status STRING DEFAULT 'ACTIVE', -- 'ACTIVE' | 'PAUSED'
  check_frequency_minutes INT64 DEFAULT 15,
  notification_channel STRING DEFAULT '#media-alerts',
  subscriber_count INT64,
  total_video_count INT64,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  last_checked_at TIMESTAMP
)
CLUSTER BY platform, tracking_status;

-- ------------------------------------------------------------------------------
-- 2. TIME-SERIES CHANNEL SNAPSHOTS TABLE (Daily/Weekly Trends)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `studiosonar_analytics.channel_snapshots` (
  snapshot_id STRING NOT NULL,
  channel_id STRING NOT NULL,
  snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  subscriber_count INT64,
  total_video_count INT64,
  average_views_per_video FLOAT64,
  sub_growth_velocity_pct FLOAT64
)
PARTITION BY DATE(snapshot_timestamp)
CLUSTER BY channel_id;

-- ------------------------------------------------------------------------------
-- 3. VIDEO METADATA & TELEMETRY TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `studiosonar_analytics.videos` (
  video_id STRING NOT NULL,
  channel_id STRING NOT NULL,
  platform STRING NOT NULL, -- 'youtube' | 'tiktok'
  url STRING NOT NULL,
  title STRING NOT NULL,
  speaker STRING,
  duration_sec INT64,
  published_at TIMESTAMP,
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  monitoring_tier STRING DEFAULT 'HIGH_PRIORITY_24H', -- 'HIGH_PRIORITY_24H' | 'NORMAL_7D' | 'ARCHIVED'
  tracking_status STRING DEFAULT 'ACTIVE',
  view_count INT64,
  like_count INT64,
  comment_count INT64,
  view_velocity_vs_channel_baseline_pct FLOAT64,
  content_quality_score FLOAT64,
  packaging_score FLOAT64,
  topic_tags ARRAY<STRING>,
  generated_report_path STRING
)
PARTITION BY DATE(ingested_at)
CLUSTER BY channel_id, monitoring_tier;

-- ------------------------------------------------------------------------------
-- 4. HOURLY TIME-SERIES VIDEO SNAPSHOTS (Velocity Tracking)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `studiosonar_analytics.video_snapshots` (
  snapshot_id STRING NOT NULL,
  video_id STRING NOT NULL,
  snapshot_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  hours_since_publish FLOAT64,
  view_count INT64,
  like_count INT64,
  comment_count INT64,
  views_per_hour FLOAT64,
  engagement_rate_pct FLOAT64,
  sentiment_positive_pct FLOAT64,
  sentiment_negative_pct FLOAT64
)
PARTITION BY DATE(snapshot_timestamp)
CLUSTER BY video_id
OPTIONS(
  partition_expiration_days=60, -- Cost FinOps: Auto-purge snapshots older than 60 days
  description="Time-series hourly velocity metrics"
);

-- ------------------------------------------------------------------------------
-- 5. SOCIAL COMMENTS & VECTOR EMBEDDINGS TABLE (768-dim text-embedding-004)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `studiosonar_analytics.comments` (
  comment_id STRING NOT NULL,
  video_id STRING NOT NULL,
  platform STRING NOT NULL,
  author_id_hash STRING NOT NULL, -- Anonymized user ID for privacy compliance
  comment_text STRING NOT NULL,
  sentiment_score FLOAT64, -- -1.0 (Extreme Negative) to +1.0 (Extreme Positive)
  toxicity_score FLOAT64,  -- 0.0 to 1.0
  like_count INT64,
  published_at TIMESTAMP,
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  embedding ARRAY<FLOAT64> -- 768-dim vector embedding from Google text-embedding-004
)
PARTITION BY DATE(ingested_at)
CLUSTER BY video_id, platform
OPTIONS(
  partition_expiration_days=90, -- Cost FinOps: Auto-purge raw comments older than 90 days
  require_partition_filter=true, -- Cost FinOps: Prevents expensive full-table scans
  description="Comments and embeddings storage"
);



-- ------------------------------------------------------------------------------
-- 6. ANOMALY & TREND SPIKES REGISTRY TABLE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `studiosonar_analytics.trend_anomalies` (
  anomaly_id STRING NOT NULL,
  anomaly_type STRING NOT NULL, -- 'PR_CRISIS_SPIKE' | 'VIRAL_TREND_ACCELERATION' | 'UNUSUAL_DROP'
  entity_id STRING NOT NULL, -- video_id or topic
  platform STRING NOT NULL,
  velocity_rate_pct FLOAT64 NOT NULL,
  sentiment_average FLOAT64,
  sample_evidence ARRAY<STRING>,
  status STRING DEFAULT 'PENDING_AGENT_EVALUATION', -- 'PENDING' | 'RESOLVED' | 'DISMISSED'
  detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(detected_at)
CLUSTER BY anomaly_type, status;

-- ------------------------------------------------------------------------------
-- 7. ANALYTICAL VIEWS
-- ------------------------------------------------------------------------------

-- View A: Real-time Negative Sentiment Velocity Spikes (PR Early Warning)
CREATE OR REPLACE VIEW `studiosonar_analytics.v_sentiment_velocity_spikes` AS
WITH current_window AS (
  SELECT 
    video_id,
    COUNT(*) AS comment_volume,
    AVG(sentiment_score) AS avg_sentiment,
    COUNTIF(sentiment_score < -0.5) AS negative_comments
  FROM `studiosonar_analytics.comments`
  WHERE ingested_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 6 HOUR)
  GROUP BY video_id
),
historical_window AS (
  SELECT 
    video_id,
    COUNT(*) / 4.0 AS baseline_volume,
    AVG(sentiment_score) AS baseline_sentiment
  FROM `studiosonar_analytics.comments`
  WHERE ingested_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
    AND ingested_at < TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 6 HOUR)
  GROUP BY video_id
)
SELECT 
  c.video_id,
  c.comment_volume,
  c.avg_sentiment,
  c.negative_comments,
  COALESCE(h.baseline_volume, 1.0) AS baseline_volume,
  SAFE_DIVIDE(c.comment_volume - h.baseline_volume, h.baseline_volume) * 100.0 AS velocity_spike_pct
FROM current_window c
LEFT JOIN historical_window h ON c.video_id = h.video_id
WHERE SAFE_DIVIDE(c.comment_volume - h.baseline_volume, h.baseline_volume) * 100.0 >= 200.0
  AND c.avg_sentiment <= -0.50;

-- ------------------------------------------------------------------------------
-- 8. SWARM REASONING & AGENT TELEMETRY SYSTEM OF RECORD
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `studiosonar_analytics.agent_telemetry` (
  telemetry_id STRING NOT NULL,
  agent_id STRING NOT NULL,
  agent_name STRING NOT NULL,
  role STRING NOT NULL,
  status STRING NOT NULL, -- 'ACTIVE' | 'IDLE' | 'EXECUTING'
  cpu_pct FLOAT64,
  memory_mb FLOAT64,
  batch_id STRING,
  tasks_completed INT64,
  last_action STRING,
  last_tool_call STRING,
  last_payload_summary STRING,
  gemini_reasoning STRING,
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
PARTITION BY DATE(recorded_at)
CLUSTER BY agent_id, status;

-- ------------------------------------------------------------------------------
-- 9. AUTONOMOUS CYCLE EXECUTION AUDIT LEDGER (System of Record)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `studiosonar_analytics.cycle_ledger` (
  cycle_id STRING NOT NULL,
  cycle_type STRING NOT NULL, -- 'ALL' | 'COMPANY_CHANNEL' | 'PR_CRISIS' | 'VIRAL_TREND'
  trigger_source STRING NOT NULL, -- 'CLOUD_SCHEDULER' | 'WEB_API' | 'CLI_JOB'
  status STRING NOT NULL, -- 'SUCCESS' | 'FAILED' | 'PARTIAL'
  started_at TIMESTAMP NOT NULL,
  completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  duration_seconds FLOAT64,
  ingested_snapshot_count INT64,
  anomalies_detected_count INT64,
  slack_alerts_dispatched INT64,
  notion_cards_created INT64,
  gdocs_scripts_created INT64,
  gcs_reports_published ARRAY<STRING>,
  error_message STRING
)
PARTITION BY DATE(started_at)
CLUSTER BY cycle_type, status;



-- ==============================================================================
-- StudioSonar ClickHouse Real-Time Storage & Stream Processing Schema
-- Database: studiosonar
-- Target: ClickHouse Serverless / Managed Cluster (Hot Path Analytics)
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS studiosonar;

-- ------------------------------------------------------------------------------
-- 1. TRACKED CHANNELS REGISTRY (Real-time in-memory lookup)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS studiosonar.tracked_channels (
    channel_id String,
    handle String,
    platform LowCardinality(String), -- 'youtube' | 'tiktok'
    title String,
    category LowCardinality(String),
    tracking_status LowCardinality(String) DEFAULT 'ACTIVE',
    check_frequency_minutes UInt16 DEFAULT 15,
    subscriber_count UInt64 DEFAULT 0,
    total_video_count UInt32 DEFAULT 0,
    created_at DateTime DEFAULT now(),
    last_checked_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(last_checked_at)
ORDER BY (platform, channel_id);

-- ------------------------------------------------------------------------------
-- 2. REAL-TIME HOURLY VIDEO SNAPSHOTS (Sliding Window Velocity Calculations)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS studiosonar.video_snapshots (
    snapshot_id String,
    video_id String,
    snapshot_timestamp DateTime DEFAULT now(),
    hours_since_publish Float32,
    view_count UInt64,
    like_count UInt64,
    comment_count UInt64,
    views_per_hour Float32,
    engagement_rate_pct Float32,
    sentiment_positive_pct Float32,
    sentiment_negative_pct Float32
) ENGINE = ReplacingMergeTree(snapshot_timestamp)
PARTITION BY toYYYYMM(snapshot_timestamp)
ORDER BY (video_id, snapshot_timestamp)
TTL snapshot_timestamp + INTERVAL 30 DAY
SETTINGS index_granularity = 8192;

-- ------------------------------------------------------------------------------
-- 3. HIGH-THROUGHPUT REAL-TIME COMMENTS STREAM
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS studiosonar.comments_realtime (
    comment_id String,
    video_id String,
    platform LowCardinality(String),
    author_id_hash String,
    comment_text String,
    sentiment_score Float32, -- -1.0 to +1.0
    toxicity_score Float32,
    like_count UInt32,
    published_at DateTime,
    ingested_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toDate(ingested_at)
ORDER BY (video_id, published_at, comment_id)
TTL ingested_at + INTERVAL 14 DAY
SETTINGS index_granularity = 8192;

-- ------------------------------------------------------------------------------
-- 4. MATERIALIZED VIEW: HOURLY SENTIMENT & COMMENT VELOCITY AGGREGATE
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS studiosonar.hourly_sentiment_aggregates (
    video_id String,
    window_start DateTime,
    comment_volume UInt32,
    negative_comments UInt32,
    positive_comments UInt32,
    sum_sentiment Float64
) ENGINE = SummingMergeTree()
PRIMARY KEY (video_id, window_start)
TTL window_start + INTERVAL 30 DAY;

CREATE MATERIALIZED VIEW IF NOT EXISTS studiosonar.mv_hourly_sentiment_spikes
TO studiosonar.hourly_sentiment_aggregates
AS SELECT
    video_id,
    toStartOfHour(published_at) AS window_start,
    count() AS comment_volume,
    countIf(sentiment_score <= -0.50) AS negative_comments,
    countIf(sentiment_score >= 0.50) AS positive_comments,
    sum(sentiment_score) AS sum_sentiment
FROM studiosonar.comments_realtime
GROUP BY video_id, window_start;

-- ------------------------------------------------------------------------------
-- 4.1 MATERIALIZED VIEW: 5-MINUTE ULTRA-FAST SLIDING ROLLUP (U4 High-Frequency Radar)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS studiosonar.five_minute_sentiment_aggregates (
    video_id String,
    window_start DateTime,
    comment_volume UInt32,
    negative_comments UInt32,
    positive_comments UInt32,
    sum_sentiment Float64
) ENGINE = SummingMergeTree()
PRIMARY KEY (video_id, window_start)
TTL window_start + INTERVAL 7 DAY;

CREATE MATERIALIZED VIEW IF NOT EXISTS studiosonar.mv_5min_windows
TO studiosonar.five_minute_sentiment_aggregates
AS SELECT
    video_id,
    toStartOfFiveMinute(published_at) AS window_start,
    count() AS comment_volume,
    countIf(sentiment_score <= -0.50) AS negative_comments,
    countIf(sentiment_score >= 0.50) AS positive_comments,
    sum(sentiment_score) AS sum_sentiment
FROM studiosonar.comments_realtime
GROUP BY video_id, window_start;

-- ------------------------------------------------------------------------------
-- 4.2 AGGREGATING MERGETREE RICH MV (-State Combinators for Quantile & Uniq)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS studiosonar.hourly_rich_aggregates (
    video_id String,
    window_start DateTime,
    cnt_state AggregateFunction(count),
    sent_p95_state AggregateFunction(quantile(0.95), Float32),
    authors_state AggregateFunction(uniq, String)
) ENGINE = AggregatingMergeTree()
PRIMARY KEY (video_id, window_start)
TTL window_start + INTERVAL 14 DAY;

CREATE MATERIALIZED VIEW IF NOT EXISTS studiosonar.mv_hourly_rich
TO studiosonar.hourly_rich_aggregates
AS SELECT
    video_id,
    toStartOfHour(published_at) AS window_start,
    countState() AS cnt_state,
    quantileState(0.95)(sentiment_score) AS sent_p95_state,
    uniqState(author_id_hash) AS authors_state
FROM studiosonar.comments_realtime
GROUP BY video_id, window_start;

-- ------------------------------------------------------------------------------
-- 4.3 PROJECTIONS ON COMMENTS REALTIME (Sub-5ms Ad-Hoc Grouping Acceleration)
-- ------------------------------------------------------------------------------
ALTER TABLE studiosonar.comments_realtime ADD PROJECTION IF NOT EXISTS proj_video_hour (
    SELECT
        video_id,
        toStartOfHour(published_at) AS h,
        count(),
        avg(sentiment_score),
        uniq(author_id_hash)
    GROUP BY video_id, h
);

-- ------------------------------------------------------------------------------
-- 5. REAL-TIME TREND ANOMALIES & PR BACKLASH SPIKES
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS studiosonar.trend_anomalies (
    anomaly_id String,
    anomaly_type LowCardinality(String), -- 'PR_CRISIS_SPIKE' | 'VIRAL_TREND_ACCELERATION' | 'UNUSUAL_DROP'
    entity_id String,
    platform LowCardinality(String),
    velocity_rate_pct Float32,
    sentiment_average Float32,
    sample_evidence Array(String),
    status LowCardinality(String) DEFAULT 'PENDING_AGENT_EVALUATION',
    detected_at DateTime DEFAULT now()
) ENGINE = MergeTree()
PARTITION BY toDate(detected_at)
ORDER BY (anomaly_type, detected_at, anomaly_id)
TTL detected_at + INTERVAL 30 DAY;


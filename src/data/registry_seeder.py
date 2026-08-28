"""
Canonical Surveillance Registry Seeder.

BigQuery is the single source of truth for monitored channels, videos and
TikTok sounds on Cloud Run. This module holds the canonical sample dataset
(same entities that were previously hardcoded in tracking_registry.json) and
provides an idempotent routine that seeds it into the `tracked_channels` and
`videos` BigQuery tables when they are empty / missing rows.

It is NOT a read fallback: reads always come from BigQuery. This function only
guarantees the tables get populated so the dashboard is never empty on Cloud Run.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any

logger = logging.getLogger("studiosonar.registry_seeder")

# ------------------------------------------------------------------------------
# Canonical Sample Dataset (Source of Truth for seeding BigQuery)
# ------------------------------------------------------------------------------

SEED_CHANNELS: List[Dict[str, Any]] = [
    {
        "channel_id": "ch_business",
        "report_key": "channel_bloomberg",
        "handle": "@business",
        "platform": "youtube",
        "title": "Bloomberg Originals",
        "category": "Global Business & Documentaries",
        "tracking_status": "ACTIVE",
        "check_frequency_minutes": 15,
        "video_lookback_days": 30,
        "notification_channel": "#media-alerts",
        "custom_sentiment_categories": [
            "Macroeconomic Debates",
            "Data & Source Requests",
            "Contrarian Perspectives",
            "Editorial Praise"
        ],
        "subscriber_count": 3400000,
        "total_video_count": 1850,
        "average_views_per_video": 650000.0
    },
    {
        "channel_id": "ch_kiemdinhphim90",
        "report_key": "channel_kiemdinhphim",
        "handle": "@KiemDinhPhim9.0",
        "platform": "youtube",
        "title": "Kiểm Định Phim 9.0",
        "category": "Film Criticism & Satire",
        "tracking_status": "ACTIVE",
        "check_frequency_minutes": 15,
        "video_lookback_days": 30,
        "notification_channel": "#media-alerts",
        "custom_sentiment_categories": [
            "Comedic Roasting Praise",
            "Actor & Drama Defense",
            "Next Episode Suggestions",
            "Awards Voting"
        ],
        "subscriber_count": 48400,
        "total_video_count": 65,
        "average_views_per_video": 55000.0
    },
    {
        "channel_id": "ch_thochupanhdalat",
        "report_key": "channel_thochupanh",
        "handle": "@thochupanh.dalat",
        "platform": "tiktok",
        "title": "Thợ Chụp Ảnh Đà Lạt",
        "category": "Travel & Photography (TikTok Creator)",
        "tracking_status": "ACTIVE",
        "check_frequency_minutes": 15,
        "video_lookback_days": 30,
        "notification_channel": "#media-alerts",
        "custom_sentiment_categories": [
            "Direct Booking & Pricing",
            "Aesthetic & Photo Praise",
            "Location Inquiries",
            "Service Feedback"
        ],
        "subscriber_count": 85000,
        "total_video_count": 120,
        "average_views_per_video": 210000.0
    },
    {
        "channel_id": "ch_google",
        "report_key": "channel_google",
        "handle": "@Google",
        "platform": "youtube",
        "title": "Google",
        "category": "Global Tech & AI Innovation",
        "tracking_status": "ACTIVE",
        "check_frequency_minutes": 15,
        "video_lookback_days": 30,
        "notification_channel": "#media-alerts",
        "custom_sentiment_categories": [
            "AI Innovation & Gemini",
            "Android & Pixel Ecosystem",
            "Developer Tools & Cloud",
            "Product Feedback & Critique"
        ],
        "subscriber_count": 11500000,
        "total_video_count": 3200,
        "average_views_per_video": 450000.0
    },
    {
        "channel_id": "ch_theverge",
        "report_key": "channel_theverge",
        "handle": "@TheVerge",
        "platform": "youtube",
        "title": "The Verge",
        "category": "Tech Journalism & Consumer Tech Reviews",
        "tracking_status": "ACTIVE",
        "check_frequency_minutes": 15,
        "video_lookback_days": 30,
        "notification_channel": "#media-alerts",
        "custom_sentiment_categories": [
            "Product Reviews & Gadgets",
            "Tech Policy & Editorial",
            "Reviewer Authenticity",
            "Design & Hardware Critique"
        ],
        "subscriber_count": 3400000,
        "total_video_count": 4500,
        "average_views_per_video": 280000.0
    }
]

SEED_VIDEOS: List[Dict[str, Any]] = [
    {
        "video_id": "UH21OnJwxZE",
        "channel_id": "ch_phuongmychi",
        "platform": "youtube",
        "url": "https://www.youtube.com/watch?v=UH21OnJwxZE",
        "title": "PHƯƠNG MỸ CHI x DTAP | 'THIÊN ĐƯỜNG VỚI NGƯỜI THƯƠNG' | OFFICIAL MUSIC VIDEO",
        "published_at": "2026-08-20T12:00:00Z",
        "monitoring_tier": "HIGH_PRIORITY_24H",
        "tracking_status": "ACTIVE",
        "custom_sentiment_categories": [
            "Viral Chorus Replay Obsession",
            "Cultural Heritage Resonance",
            "Music Video Storyline Praise",
            "Choreography Inquiries"
        ],
        "view_count": 14088244,
        "like_count": 238061,
        "comment_count": 25382
    },
    {
        "video_id": "tt_sound_pmc_thien_duong",
        "channel_id": "ch_tiktok_sounds",
        "platform": "tiktok",
        "url": "https://www.tiktok.com/music/Thien-Duong-Voi-Nguoi-Thuong-Official",
        "title": "🎵 TikTok Sound: 'Thiên Đường Với Người Thương' (128.5K UGC Videos)",
        "published_at": "2026-08-20T12:00:00Z",
        "monitoring_tier": "TIKTOK_SOUND_RADAR",
        "tracking_status": "ACTIVE",
        "custom_sentiment_categories": [
            "Traditional Transformation Dance",
            "Speed-Up Remix Adoption",
            "UGC Creation Velocity",
            "Hand Gesture Choreography"
        ],
        "view_count": 128540,
        "like_count": 985000,
        "comment_count": 14200
    },
    {
        "video_id": "Rp6ZnP5WRgI",
        "channel_id": "ch_phuongmychi",
        "platform": "youtube",
        "url": "https://www.youtube.com/watch?v=Rp6ZnP5WRgI",
        "title": "PHƯƠNG MỸ CHI x DTAP | ALBUM 'DÂN CHƠI DÂN CA' | OFFICIAL HIGHLIGHT MEDLEY",
        "published_at": "2026-08-24T12:00:00Z",
        "monitoring_tier": "HIGH_PRIORITY_24H",
        "tracking_status": "ACTIVE",
        "custom_sentiment_categories": [
            "Folk Fusion Innovation Praise",
            "DTAP Music Production Quality",
            "Vocal Transformation Dynamics",
            "Album Release Inquiries"
        ],
        "view_count": 232424,
        "like_count": 13370,
        "comment_count": 839
    },
    {
        "video_id": "tt_sound_dtap_dan_choi",
        "channel_id": "ch_tiktok_sounds",
        "platform": "tiktok",
        "url": "https://www.tiktok.com/music/Dan-Choi-Dan-Ca-Drop-Beat",
        "title": "🎵 TikTok Sound: 'Dân Chơi Dân Ca' (34.2K UGC Videos)",
        "published_at": "2026-08-24T12:00:00Z",
        "monitoring_tier": "TIKTOK_SOUND_RADAR",
        "tracking_status": "ACTIVE",
        "custom_sentiment_categories": [
            "Bass Drop Transitions",
            "Street Style Dance",
            "Remix Sound Inquiries",
            "Short-form Virality"
        ],
        "view_count": 34210,
        "like_count": 245000,
        "comment_count": 4850
    },
    {
        "video_id": "R7Bf4l5VgO8",
        "channel_id": "ch_thuychi",
        "platform": "youtube",
        "url": "https://www.youtube.com/watch?v=R7Bf4l5VgO8",
        "title": "Thùy Chi - Yêu Lắm Miền Tây (Official Music Video)",
        "published_at": "2026-08-25T00:00:00Z",
        "monitoring_tier": "HIGH_PRIORITY_24H",
        "tracking_status": "ACTIVE",
        "custom_sentiment_categories": [
            "Vocal Tone & Melody Praise",
            "Western Vietnam Scenery & Culture",
            "Nostalgia & Emotional Connection",
            "Arrangement Inquiries"
        ],
        "view_count": 15842,
        "like_count": 1278,
        "comment_count": 191
    },
    {
        "video_id": "TNl9diGdyPo",
        "channel_id": "ch_business",
        "platform": "youtube",
        "url": "https://www.youtube.com/watch?v=TNl9diGdyPo",
        "title": "How Ferrero Makes 365,000 Tons Of Nutella A Year | Big Business | Business Insider",
        "published_at": "2026-08-24T12:00:00Z",
        "monitoring_tier": "HIGH_PRIORITY_24H",
        "tracking_status": "ACTIVE",
        "custom_sentiment_categories": [
            "Industrial Automation Fascination",
            "Raw Ingredient Quality & Palm Oil",
            "Factory Engineering Praise",
            "Commercial Scale Inquiries"
        ],
        "view_count": 388149,
        "like_count": 4830,
        "comment_count": 473
    }
]


# ------------------------------------------------------------------------------
# BigQuery column mappers (JSON registry shape -> BQ schema)
# ------------------------------------------------------------------------------

def _channel_to_bq_row(ch: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "channel_id": ch["channel_id"],
        "handle": ch["handle"],
        "platform": ch["platform"],
        "title": ch["title"],
        "category": ch.get("category", "General"),
        "tracking_status": ch.get("tracking_status", "ACTIVE"),
        "check_frequency_minutes": int(ch.get("check_frequency_minutes", 15)),
        "notification_channel": ch.get("notification_channel", "#media-alerts"),
        "subscriber_count": int(ch.get("subscriber_count", 0)),
        "total_video_count": int(ch.get("total_video_count", 0)),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_checked_at": None
    }


def _video_to_bq_row(v: Dict[str, Any]) -> Dict[str, Any]:
    row = {
        "video_id": v["video_id"],
        "channel_id": v.get("channel_id", ""),
        "platform": v.get("platform", "youtube"),
        "url": v.get("url", f"https://www.youtube.com/watch?v={v['video_id']}"),
        "title": v.get("title", v["video_id"]),
        "published_at": v.get("published_at"),
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "monitoring_tier": v.get("monitoring_tier", "HIGH_PRIORITY_24H"),
        "tracking_status": v.get("tracking_status", "ACTIVE"),
        "view_count": int(v.get("view_count", 0)),
        "like_count": int(v.get("like_count", 0)),
        "comment_count": int(v.get("comment_count", 0)),
        "view_velocity_vs_channel_baseline_pct": float(v.get("view_velocity_vs_channel_baseline_pct", 0.0))
    }
    # Only emit optional columns when a value is present. BigQuery's
    # insert_rows_json rejects null/empty values for some repeated columns.
    if v.get("published_at") is None:
        row.pop("published_at", None)
    for key in ("speaker", "duration_sec", "content_quality_score", "packaging_score",
                "topic_tags", "generated_report_path"):
        val = v.get(key)
        if val is not None:
            row[key] = val
    return row


# ------------------------------------------------------------------------------
# Seeding routine (idempotent: inserts only missing rows)
# ------------------------------------------------------------------------------

def _insert_missing_rows(client, project_id: str, dataset: str, table: str,
                         pk_column: str, rows: List[Dict[str, Any]]) -> int:
    """Inserts rows whose primary key is not yet present in the target table."""
    if not rows:
        return 0

    table_ref = f"{project_id}.{dataset}.{table}"

    # Fetch existing primary keys
    existing_ids = set()
    try:
        query_job = client.query(f"SELECT {pk_column} AS pk FROM `{table_ref}`")
        for row in query_job.result():
            existing_ids.add(row.pk)
    except Exception as e:
        logger.warning(f"registry seeder: could not read existing {table}: {e}")
        return 0

    missing = [r for r in rows if r.get(pk_column) not in existing_ids]
    if not missing:
        return 0

    try:
        errors = client.insert_rows_json(table_ref, missing)
        if errors:
            logger.error(f"registry seeder: insert errors into {table}: {errors}")
            return 0
        logger.info(f"registry seeder: inserted {len(missing)} rows into {table}")
        return len(missing)
    except Exception as e:
        logger.warning(f"registry seeder: failed inserting into {table}: {e}")
        return 0


def ensure_registry_seeded(client, project_id: str, dataset: str) -> Dict[str, Any]:
    """Seeds the canonical sample registry into BigQuery (idempotent)."""
    inserted_channels = _insert_missing_rows(
        client, project_id, dataset, "tracked_channels",
        "channel_id", [_channel_to_bq_row(c) for c in SEED_CHANNELS]
    )
    inserted_videos = _insert_missing_rows(
        client, project_id, dataset, "videos",
        "video_id", [_video_to_bq_row(v) for v in SEED_VIDEOS]
    )
    return {
        "target": f"{project_id}.{dataset}",
        "inserted_channels": inserted_channels,
        "inserted_videos": inserted_videos
    }
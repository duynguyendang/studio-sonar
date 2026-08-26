import re
from datetime import datetime, timezone
from typing import Dict, List, Any

class TikTokScannerEngine:
    """
    TikTok Video & Channel Telemetry Scanner Engine.
    Analyzes Shortform FYP (For You Page) Algorithm Drivers:
    - Sound/Audio Virality ID
    - Save & Share Ratios (High-Signal FYP Booster)
    - 3-Second Hook Retention Velocity
    - Gen Z & Slang Comment Sentiment
    """

    @staticmethod
    def extract_tiktok_id_or_user(url_or_handle: str) -> Dict[str, str]:
        """Extracts username and video ID from a TikTok URL or handle."""
        video_match = re.search(r"@([a-zA-Z0-9_.-]+)/video/(\d+)", url_or_handle)
        if video_match:
            return {"type": "video", "username": video_match.group(1), "video_id": video_match.group(2)}
        
        user_match = re.search(r"@([a-zA-Z0-9_.-]+)", url_or_handle)
        if user_match:
            return {"type": "channel", "username": user_match.group(1), "video_id": ""}

        return {"type": "video", "username": "tiktok_creator", "video_id": url_or_handle.strip()}

    @staticmethod
    def scan_tiktok_video(url_or_id: str) -> Dict[str, Any]:
        """
        Simulates / executes full telemetry extraction on a TikTok video URL.
        Computes FYP algorithm metrics: Share-to-Like ratio, Loop Rate, Hook Efficiency.
        """
        extracted = TikTokScannerEngine.extract_tiktok_id_or_user(url_or_id)
        video_id = extracted["video_id"] or "tt_73918291039"
        username = extracted["username"]

        # Realistic high-velocity TikTok video scenario
        video_data = {
            "platform": "tiktok",
            "video_id": video_id,
            "url": f"https://www.tiktok.com/@{username}/video/{video_id}" if "http" not in url_or_id else url_or_id,
            "creator_handle": f"@{username}",
            "caption": "Bí mật đằng sau những video triệu view trên TikTok mà không ai nói cho bạn biết! #fyp #learnontiktok #contentcreator #marketing",
            "duration_sec": 42,
            "sound_title": "Original Sound - Trending Ambient Synth",
            "sound_is_trending": True,
            "view_count": 348000,
            "like_count": 29400,
            "comment_count": 840,
            "share_count": 4200,   # High Share count is the #1 signal for TikTok FYP
            "save_count": 8900,    # High Save count signals high evergreen utility
            "average_watch_time_sec": 38.5, # 91.6% completion rate (Extreme Viral Signal)
            "hook_dropoff_0_3s_pct": 6.2,   # Only 6.2% skipped in first 3s
            "published_at": "2026-08-23T14:30:00Z"
        }

        # Algorithm Analysis
        share_to_like_ratio = round((video_data["share_count"] / max(video_data["like_count"], 1)) * 100, 2)
        save_to_like_ratio = round((video_data["save_count"] / max(video_data["like_count"], 1)) * 100, 2)
        completion_rate = round((video_data["average_watch_time_sec"] / video_data["duration_sec"]) * 100, 2)

        fyp_score = round((completion_rate * 0.4) + (share_to_like_ratio * 2.5) + (save_to_like_ratio * 1.5), 1)

        diagnostics = {
            "fyp_algorithm_score": min(fyp_score, 100.0),
            "completion_rate_pct": completion_rate,
            "share_to_like_ratio_pct": share_to_like_ratio,
            "save_to_like_ratio_pct": save_to_like_ratio,
            "hook_efficiency": "Xuất sắc (Chỉ 6.2% bỏ qua trong 3s đầu)",
            "primary_viral_driver": "Tỷ lệ Lưu (Save) và Chia sẻ (Share) cực cao kích hoạt thuật toán For You Page đẩy liên tục."
        }

        sample_comments = [
            {"user": "genz_editor", "text": "Hook 3s đầu đỉnh quá anh ơi, lưu lại ngay để áp dụng cho kênh!", "sentiment": 0.95},
            {"user": "marketing_pro", "text": "Chuẩn luôn, share về nhóm cho team media học tập.", "sentiment": 0.92},
            {"user": "newbie_creator", "text": "Cho em hỏi dùng app nào để cắt tiếng động giật gân vậy ạ?", "sentiment": 0.50}
        ]

        return {
            "status": "SCANNED_SUCCESS",
            "video": video_data,
            "diagnostics": diagnostics,
            "comments_sample": sample_comments,
            "sentiment_distribution": {
                "positive_pct": 92.4,
                "neutral_inquiries_pct": 6.8,
                "negative_pct": 0.8
            }
        }

tiktok_scanner = TikTokScannerEngine()

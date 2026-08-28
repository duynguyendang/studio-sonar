import re
from typing import Dict, List, Any
from src.services.tracking_service import tracking_service
from src.tools.universal_hook_recommender import hook_recommender

class SettingsCopilotAgent:
    """
    Conversational Agent that parses natural language instructions from Chat UI
    and executes setting adjustments (Lookback days, Tracking durations, Channel/Video CRUD, Hook generation).
    """

    def process_chat_command(self, user_message: str) -> Dict[str, Any]:
        msg_lower = user_message.lower().strip()

        # 1. Intent: Adjust Video Tracking Duration
        # e.g., "Theo dõi video kqBKKSV50es trong 7 ngày thôi", "Chỉnh video ye3B8kPuTnc 14 ngày"
        duration_match = re.search(r"(\d+)\s*(ngày|day|days)", msg_lower)
        days = int(duration_match.group(1)) if duration_match else 30

        if any(kw in msg_lower for kw in ["thời gian", "theo dõi", "duration", "chỉnh", "đổi", "set"]) and any(vid in user_message for vid in tracking_service.videos.keys()):
            for vid in tracking_service.videos.keys():
                if vid in user_message:
                    updated = tracking_service.update_video_tracking_duration(vid, days)
                    return {
                        "action_executed": "UPDATE_VIDEO_DURATION",
                        "video_id": vid,
                        "new_duration_days": days,
                        "reply": f"✅ Đã cập nhật thời gian theo dõi video **{updated.title[:40]}...** thành **{days} ngày** (FinOps Cost Saver kích hoạt)."
                    }

        # Dynamic fuzzy match against all actively tracked videos
        for vid, v in tracking_service.videos.items():
            title_words = [w.lower() for w in re.findall(r'\w+', v.title)]
            if any(w in msg_lower for w in title_words if len(w) > 3):
                updated = tracking_service.update_video_tracking_duration(vid, days)
                return {
                    "action_executed": "UPDATE_VIDEO_DURATION",
                    "video_id": vid,
                    "new_duration_days": days,
                    "reply": f"✅ Đã điều chỉnh thời gian theo dõi video **{v.title[:40]}...** thành **{days} ngày**."
                }

        # 2. Intent: Add Channel
        if any(kw in msg_lower for kw in ["thêm kênh", "follow kênh", "track channel", "add channel"]):
            handle_match = re.search(r"(@[a-zA-Z0-9_.-]+)", user_message)
            if handle_match:
                handle = handle_match.group(1)
                ch = tracking_service.add_channel(handle, video_lookback_days=days)
                return {
                    "action_executed": "ADD_CHANNEL",
                    "channel_handle": handle,
                    "reply": f"✅ Đã đăng ký theo dõi kênh **{handle}** với cửa sổ quét **{days} ngày gần nhất**."
                }

        # 3. Intent: Generate Viral Hooks
        if any(kw in msg_lower for kw in ["hook", "tiêu đề", "sinh hook", "gợi ý hook", "tạo hook"]):
            topic = user_message.replace("sinh hook", "").replace("tạo hook", "").replace("gợi ý hook", "").replace("hook", "").strip() or "Công nghệ AI"
            hooks = hook_recommender.prescribe_hooks_for_topic(topic)
            sample_hooks = "\n".join([f"• **{h['suggested_title']}** (Dự kiến: `{h['expected_ctr_boost']}` CTR)" for h in hooks[:3]])
            return {
                "action_executed": "GENERATE_HOOKS",
                "topic": topic,
                "reply": f"🔥 **Gợi ý 3 Hook Triệu View cho chủ đề '{topic}':**\n\n{sample_hooks}"
            }

        # 4. Intent: FinOps Status & Help
        if any(kw in msg_lower for kw in ["cost", "chi phí", "finops", "tiết kiệm", "giúp", "help"]):
            return {
                "action_executed": "HELP_INFO",
                "reply": (
                    "💡 **Bạn có thể ra lệnh cho tôi điều chỉnh cấu hình:**\n"
                    "- *'Chỉnh video Lê Viết Quốc theo dõi 7 ngày'*\n"
                    "- *'Thêm kênh @vtv24 với lookback 14 ngày'*\n"
                    "- *'Sinh 5 hook về chủ đề Kiến trúc Microservices'*\n"
                    "- *'Báo cáo trạng thái chi phí BigQuery & Cloud Run'*"
                )
            }

        return {
            "action_executed": "GENERAL_REPLY",
            "reply": f"🤖 Tôi đã nhận lệnh: *\"{user_message}\"*. Bạn có thể yêu cầu tôi đổi số ngày theo dõi video (VD: *'Chỉnh video Momentum EP05 thành 7 ngày'*), thêm kênh mới hoặc sinh Hook triệu view tức thì!"
        }

settings_copilot = SettingsCopilotAgent()

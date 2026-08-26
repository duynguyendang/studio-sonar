from typing import Dict, List, Any
from src.core.hook_knowledge_base import hook_kb

class UniversalHookRecommender:
    """
    Universal Engine that prescribes tailored high-CTR viral hooks for ANY video or channel topic,
    leveraging the central Hook Tips Knowledge Base.
    """

    @staticmethod
    def prescribe_hooks_for_topic(topic: str, category: str = "Tech & Business", target_audience: str = "General") -> List[Dict[str, Any]]:
        all_tips = hook_kb.list_all_hooks()
        prescriptions = []

        for tip in all_tips:
            arch = tip["archetype"]
            
            if "Financial" in arch or "Loss" in arch:
                custom_title = f"Nơi Hàng Trăm Triệu Đầu Tư Vào '{topic}' Đã 'Bốc Hơi' Như Thế Nào?"
                custom_3s = f"Tôi đã tìm thấy nơi hàng trăm triệu đồng đầu tư vào '{topic}' đã biến mất chỉ sau vài tuần..."
                custom_thumb = "TIỀN ĐÃ 'BỐC HƠI'?"
            elif "Contrarian" in arch:
                custom_title = f"Làm Về '{topic}' Trong 2026? ĐỪNG BAO GIỜ Làm Theo Cách Ngớ Ngẩn Này!"
                custom_3s = f"Dừng lại! Nếu bạn vẫn đang làm '{topic}' theo cách này trong 2026, bạn đang tự hại chính mình!"
                custom_thumb = "ĐỪNG LÀM THẾ NÀY!"
            elif "Transformation" in arch:
                custom_title = f"Hậu Trường Thực Tế vs Thành Phẩm 'Triệu View' Của '{topic}'"
                custom_3s = f"Bạn nghĩ làm '{topic}' dễ dàng? Nhìn hậu trường lóng ngóng này và xem kết quả thật nhé!"
                custom_thumb = "HẬU TRƯỜNG VS THẬT"
            elif "Insider" in arch:
                custom_title = f"Sự Thật Về '{topic}' Mà Các Chuyên Gia Không Bao Giờ Dám Tiết Lộ Cho Bạn"
                custom_3s = f"Có một bí mật đằng sau '{topic}' mà người trong cuộc luôn giấu kín..."
                custom_thumb = "BÍ MẬT ĐẰNG SAU!"
            elif "Extreme" in arch:
                custom_title = f"Một Dự Án '{topic}' DỞ TOÀN DIỆN Sẽ Trông Như Thế Nào? (Bóc Trần Hạt Sạn)"
                custom_3s = f"Đây là ví dụ kinh điển về một sản phẩm '{topic}' dở đến mức không thể tin nổi..."
                custom_thumb = "DỞ TOÀN DIỆN?"
            else:
                custom_title = f"Bí Quyết Làm Chủ '{topic}' Nhanh Gấp 5 Lần Bình Thường"
                custom_3s = f"Muốn làm chủ '{topic}'? Đây là 3 nguyên tắc bạn phải biết ngay hôm nay..."
                custom_thumb = "BÍ QUYẾT LÀM CHỦ"

            prescriptions.append({
                "framework_id": tip["tip_id"],
                "framework_name": tip["name"],
                "psychology": tip["psychology"],
                "suggested_title": custom_title,
                "hook_3s_opening": custom_3s,
                "thumbnail_text": custom_thumb,
                "expected_ctr_boost": tip["expected_ctr_boost"]
            })

        return prescriptions

hook_recommender = UniversalHookRecommender()

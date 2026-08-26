"""
Viral Hook Engineering & Click-Through Optimization Frameworks.
Distilled from viral case studies (Financial Catastrophe, Contrarian Roasting, Curiosity Gaps).
"""

from typing import List, Dict, Any

class ViralHookEngine:
    """
    Applies high-CTR psychological formulas to titles, thumbnails, and 3s shortform scripts.
    """

    FRAMEWORKS = {
        "FINANCIAL_CATASTROPHE": {
            "name": "Tâm lý Thảm Họa & Tiền Tệ (Financial & Costly Mistake Hook)",
            "pattern": "[Con số tiền bạc lớn / Thiệt hại] + [Động từ giật gân: 'Bốc hơi', 'Đốt tiền', 'Sụp đổ'] + [Thực trạng]",
            "example_tech": "Tôi Đã Tìm Thấy Nơi 2 Triệu USD Đầu Tư Vào AI Này 'Bốc Hơi' Trong 30 Ngày",
            "example_media": "Đầu Tư Hàng Chục Tỷ Để Nhận Về Bộ Phim 'Thảm Họa': Tiền Đã Đi Đâu?"
        },
        "CONTRARIAN_ROASTING": {
            "name": "Châm Biếm & Cảnh Báo Ngược Chiều (Contrarian Truth / 'Đừng Làm Như...')",
            "pattern": "'ĐỪNG LÀM NHƯ...' / 'SỰ THẬT TỒI TỆ VỀ...' + [Sai lầm phổ biến mà số đông đang mắc phải]",
            "example_tech": "Làm AI Agent Trong 2026, ĐỪNG Làm Theo Cách 'Ngớ Ngẩn' Này Nữa!",
            "example_media": "Làm Phim Rạp, ĐỪNG Làm Như Cách 'Ma Không Đầu' Đang Dọa Khán Giả"
        },
        "EXTREME_CURIOSITY_GAP": {
            "name": "Khoảng Trống Tò Mò Cực Đoan (Extreme Qualifier & Mystery)",
            "pattern": "[Khái niệm] + ['DỞ TOÀN DIỆN' / 'ĐỈNH TUYỆT ĐỐI'] + [Câu hỏi thách thức người xem]",
            "example_tech": "Một Dự Án AI 'Dở Toàn Diện' Sẽ Trông Như Thế Nào? (Bóc Trần 5 Hạt Sạn Lớn Nhất)",
            "example_media": "Tại Sao 90% Phim Kinh Dị Chiếu Rạp Đều Mắc Cùng 1 Lỗi 'Trời Ơi Đất Hỡi' Này?"
        },
        "INSIDER_SECRET_REVEAL": {
            "name": "Bí Mật Đằng Sau Cánh Gà (Insider Authority)",
            "pattern": "['Sự Thật Đằng Sau' / 'Bí Mật 'Code Red''] + [Nhân vật đỉnh cao / Tập đoàn nghìn tỷ]",
            "example_tech": "Người Việt Đồng Sáng Lập Google Brain: Bí Mật 12 Năm Thung Lũng Silicon Không Ai Kể Cho Bạn",
            "example_media": "Bí Mật Sau Những Bộ Phim Trăm Tỷ: Tại Sao Kịch Bản Dở Nhưng Vẫn Thu Đầy Tiền?"
        }
    }

    @classmethod
    def generate_high_octane_hooks(cls, topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generates viral titles and shortform hooks across all 4 high-CTR frameworks."""
        return {
            "framework_1_financial_catastrophe": {
                "title": f"Bóc Trần Dự Án '{topic}': Nơi Hàng Tỷ Đồng Đã 'Bốc Hơi' Như Thế Nào?",
                "hook_3s": "Bạn nghĩ dự án này xịn? Hãy xem hàng tỷ đồng đã biến mất chỉ sau một đêm như thế nào.",
                "thumbnail_text": "HÀNG TỶ 'BỐC HƠI'?"
            },
            "framework_2_contrarian_roasting": {
                "title": f"Muốn Thành Công Với '{topic}'? ĐỪNG Bao Giờ Làm Theo Cách Này Nữa!",
                "hook_3s": "Dừng ngay cách làm này lại nếu bạn không muốn trở thành trò cười trong ngành!",
                "thumbnail_text": "ĐỪNG LÀM THẾ NÀY!"
            },
            "framework_3_extreme_curiosity_gap": {
                "title": f"Một Sản Phẩm '{topic}' DỞ TOÀN DIỆN Sẽ Trông Như Thế Nào? (Bóc Trần Hạt Sạn)",
                "hook_3s": "Đây là ví dụ kinh điển về việc một sản phẩm có thể dở đến mức không thể tin nổi...",
                "thumbnail_text": "DỞ TOÀN DIỆN?"
            },
            "framework_4_insider_authority": {
                "title": f"Sự Thật Về '{topic}' Mà Các Chuyên Gia Không Bao Giờ Dám Kể Với Bạn",
                "hook_3s": "Có một bí mật đằng sau ngành này mà người trong cuộc luôn giấu kín...",
                "thumbnail_text": "SỰ THẬT ĐẰNG SAU!"
            }
        }

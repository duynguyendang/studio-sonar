import json
import os
from typing import Dict, List, Any, Optional

HOOK_TIPS_FILE = "src/data/hook_tips_registry.json"

DEFAULT_HOOK_TIPS = [
    # --- 1. FINANCIAL CATASTROPHE & COSTLY MISTAKE (Tiền Bạc & Thiệt Hại) ---
    {
        "tip_id": "HT_001_FINANCIAL_DRAIN",
        "category": "All",
        "archetype": "Financial Catastrophe & Loss Aversion",
        "name": "Nơi [Số Tiền Khủng] Đã 'Bốc Hơi'",
        "psychology": "Con người sợ mất tiền gấp 2.5 lần mong muốn kiếm tiền (Loss Aversion). Con số cụ thể tạo tính chân thực.",
        "formula": "[Con số tiền bạc cụ thể] + [Động từ thất thoát mạnh: 'Bốc hơi', 'Đốt sạch', 'Biến mất'] + [Lý do/Dự án]",
        "example_3s": "Tôi đã tìm thấy nơi 26 tỷ đồng đầu tư vào dự án này đã 'bốc hơi' chỉ sau một đêm...",
        "thumbnail_text": "26 TỶ 'BỐC HƠI'?",
        "expected_ctr_boost": "+52%"
    },
    {
        "tip_id": "HT_002_EXPENSIVE_MISTAKE",
        "category": "Tech & Business",
        "archetype": "Expensive Common Mistake",
        "name": "Sai Lầm Đắt Giá Khiến [Đối Tượng] Mất [Số Tiền]",
        "psychology": "Cảnh báo để người xem không bị mất tiền ngu.",
        "formula": "'Sai lầm đắt giá nhất' + [Hành động sai] + 'khiến bạn mất trắng hàng nghìn đô'",
        "example_3s": "Sai lầm ngớ ngẩn này trong kiến trúc Cloud đã khiến startup của chúng tôi mất 15.000$ tiền server chỉ trong 1 tuần!",
        "thumbnail_text": "MẤT 15,000$ VÌ LỖI NÀY!",
        "expected_ctr_boost": "+44%"
    },

    # --- 2. CONTRARIAN TRUTH & ROASTING ('ĐỪNG LÀM NHƯ...') ---
    {
        "tip_id": "HT_003_STOP_DOING_THIS",
        "category": "All",
        "archetype": "Contrarian Warning",
        "name": "Dừng Ngay Việc [Hành Động Phổ Biến] Lại!",
        "psychology": "Tạo cú sốc gián đoạn mô thức (Pattern Interrupt). Khiến người xem hoang mang tự hỏi mình có đang làm sai không.",
        "formula": "'Dừng lại!' / 'ĐỪNG BAO GIỜ...' + [Hành động mà 90% số đông đang làm] + [Hậu quả tệ hại]",
        "example_3s": "Dừng lại! Nếu bạn vẫn đang học viết prompt kiểu này trong 2026 thì bạn đang tự đào thải chính mình!",
        "thumbnail_text": "DỪNG LÀM CÁCH NÀY!",
        "expected_ctr_boost": "+48%"
    },
    {
        "tip_id": "HT_004_ROASTING_PARADOX",
        "category": "Entertainment & Lifestyle",
        "archetype": "Satirical Roasting",
        "name": "Làm [Thứ Gì Đó], ĐỪNG Làm Như [Ví Dụ Thảm Họa]",
        "psychology": "Sử dụng sự hài hước châm biếm để chỉ ra tiêu chuẩn tồi tệ mà ai cũng muốn tránh.",
        "formula": "'Làm [X], ĐỪNG làm như cách [Thảm họa] đang làm!'",
        "example_3s": "Làm phim kinh dị, ĐỪNG BAO GIỜ dọa ma khán giả theo kiểu 'Ma Không Đầu' này nữa!",
        "thumbnail_text": "ĐỪNG LÀM NHƯ THẾ!",
        "expected_ctr_boost": "+46%"
    },

    # --- 3. TRANSFORMATION & BEHIND-THE-SCENES (Biến Hình & Hậu Trường) ---
    {
        "tip_id": "HT_005_BTS_VS_RESULT",
        "category": "TikTok / Visual / Local",
        "archetype": "Transformation Gap",
        "name": "Hậu Trường 'Lóng Ngóng' vs Thành Phẩm 'Triệu Like'",
        "psychology": "Sự tương phản thị giác tức thì trong 1 giây kích hoạt cảm xúc kinh ngạc (Visual Wow Effect).",
        "formula": "[Hình ảnh thực tế gượng gạo (0-1s)] ➔ [Âm thanh máy ảnh 'Tách'] ➔ [Bức ảnh/kết quả lung linh (2-3s)]",
        "example_3s": "Bạn nghĩ đứng đồi thông Đà Lạt chụp ảnh là dễ? Nhìn hậu trường lóng ngóng này và xem ảnh thành phẩm nhé!",
        "thumbnail_text": "HẬU TRƯỜNG VS ẢNH THẬT",
        "expected_ctr_boost": "+58%"
    },

    # --- 4. INSIDER SECRETS & SILICON VALLEY AUTHORITY (Bí Mật Hậu Trường) ---
    {
        "tip_id": "HT_006_INSIDER_SECRET",
        "category": "Tech, Career & Leadership",
        "archetype": "Silicon Valley Insider Mystery",
        "name": "Bí Mật Đằng Sau Cánh Gà [Tập Đoàn Nghìn Tỷ / Chuyên Gia]",
        "psychology": "Khao khát tiếp cận thông tin độc quyền chưa từng công bố.",
        "formula": "'Sự thật về...' / 'Bí mật đằng sau đêm 'Code Red'...' + [Nhân vật/Tập đoàn uy tín]",
        "example_3s": "Người Việt đồng sáng lập Google Brain: Bí mật 12 năm ở Thung lũng Silicon mà chưa ai dám kể cho bạn...",
        "thumbnail_text": "BÍ MẬT 12 NĂM GOOGLE",
        "expected_ctr_boost": "+50%"
    },

    # --- 5. EXTREME QUALIFIER & CURIOSITY GAP (Khoảng Trống Tò Mò) ---
    {
        "tip_id": "HT_007_EXTREME_DISASTER",
        "category": "All",
        "archetype": "Extreme Qualifier",
        "name": "Một Thứ 'DỞ TOÀN DIỆN' Sẽ Trông Như Thế Nào?",
        "psychology": "Sự tò mò về 'đáy của sự thảm họa' (Schadenfreude / Morbid Curiosity).",
        "formula": "'Một [Sản phẩm/Bộ phim/Hệ thống] DỞ TOÀN DIỆN sẽ trông như thế nào?'",
        "example_3s": "Một dự án AI 'dở toàn diện' từ đầu đến chân sẽ trông như thế nào? Bóc trần 3 hạt sạn ngớ ngẩn nhất!",
        "thumbnail_text": "DỞ TOÀN DIỆN?",
        "expected_ctr_boost": "+43%"
    }
]

class HookKnowledgeBase:
    """Manages persistent collection of viral hook formulas harvested from YouTube & TikTok."""

    def __init__(self):
        self.tips: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if os.path.exists(HOOK_TIPS_FILE):
            try:
                with open(HOOK_TIPS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        self.tips[item["tip_id"]] = item
            except Exception:
                pass
        if not self.tips:
            for item in DEFAULT_HOOK_TIPS:
                self.tips[item["tip_id"]] = item
            self._save()

    def _save(self):
        os.makedirs(os.path.dirname(HOOK_TIPS_FILE), exist_ok=True)
        with open(HOOK_TIPS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(self.tips.values()), f, ensure_ascii=False, indent=2)

    def add_harvested_hook(self, hook_data: Dict[str, Any]):
        """Adds a newly discovered trending hook pattern to the knowledge base."""
        tip_id = hook_data.get("tip_id", f"HT_{len(self.tips)+1:03d}_VIRAL")
        hook_data["tip_id"] = tip_id
        self.tips[tip_id] = hook_data
        self._save()

    def list_all_hooks(self) -> List[Dict[str, Any]]:
        return list(self.tips.values())

hook_kb = HookKnowledgeBase()

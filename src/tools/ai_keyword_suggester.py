"""
StudioSonar AI-Powered Monitoring Keyword Suggester Engine.
Employs Gemini 3.8 Flash to analyze monitored media assets and audience sentiment,
suggesting high-priority brand entities, PR risk phrases, and viral meme drivers.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from src.core.config import settings
from src.core.llm_client import llm_client
from src.tools.keyword_extractor import keyword_extractor

logger = logging.getLogger("studiosonar.tools.ai_keyword_suggester")

class AIKeywordSuggester:
    """
    Intelligent Keyword Expansion & Recommendation Engine powered by Gemini 3.8 Flash.
    """

    SYSTEM_INSTRUCTION = (
        "You are an Elite Social Media Intelligence & Media Monitoring Specialist. "
        "Your task is to analyze a media asset (YouTube/TikTok video or Channel) and propose "
        "high-value monitoring keywords divided into 4 strategic categories: "
        "1. core_entities: Canonical brand, artist, collaborators, and show titles. "
        "2. risk_keywords: Sensitive keywords to detect early brand backlash (e.g. copyright, sponsor transparency, product quality, ethics). "
        "3. viral_slang_hooks: TikTok challenge names, memorable audio soundbites, catchy slang, and FYP hashtags. "
        "4. competitor_benchmarks: Direct industry competitors or comparable benchmark channels. "
        "Output ONLY a valid JSON object matching the requested schema."
    )

    @classmethod
    def suggest_keywords(
        cls,
        title: str,
        channel: str = "",
        category: str = "",
        context_notes: str = ""
    ) -> Dict[str, Any]:
        """
        Calls Gemini to generate multi-dimensional monitoring keywords for a video or channel.
        Falls back to rule-based lexical expansion if LLM is unavailable.
        """
        # 1. Clean title and extract initial entities
        extracted_entities = keyword_extractor.clean_title_entities(title)
        primary_entity = extracted_entities[0] if extracted_entities else (channel or title)

        prompt = (
            f"Analyze the following media asset:\n"
            f"- Title: {title}\n"
            f"- Channel/Creator: {channel}\n"
            f"- Category: {category}\n"
            f"- Additional Context: {context_notes}\n\n"
            f"Generate a structured JSON response with keys: 'core_entities', 'risk_keywords', 'viral_slang_hooks', 'competitor_benchmarks', and 'recommended_monitoring_keywords' (a top 5-7 curated list for real-time surveillance)."
        )

        try:
            raw_response = llm_client.generate(prompt=prompt, system_instruction=cls.SYSTEM_INSTRUCTION)
            if raw_response:
                # Clean markdown backticks if present
                clean_json = raw_response.strip()
                if clean_json.startswith("```"):
                    clean_json = clean_json.split("\n", 1)[-1]
                    clean_json = clean_json.rsplit("```", 1)[0].strip()
                
                parsed = json.loads(clean_json)
                if isinstance(parsed, dict) and "core_entities" in parsed:
                    return {
                        "status": "AI_GENERATED_SUCCESS",
                        "model": settings.gemini_model,
                        "target_asset": title,
                        "primary_entity": primary_entity,
                        "categories": {
                            "core_entities": parsed.get("core_entities", []),
                            "risk_keywords": parsed.get("risk_keywords", []),
                            "viral_slang_hooks": parsed.get("viral_slang_hooks", []),
                            "competitor_benchmarks": parsed.get("competitor_benchmarks", [])
                        },
                        "recommended_monitoring_keywords": parsed.get("recommended_monitoring_keywords", [])
                    }
        except Exception as e:
            logger.debug(f"Gemini keyword suggestion fallback notice: {e}")

        # 2. Intelligent Lexical Fallback (Guaranteed reliability)
        return cls._generate_heuristic_expansion(title, channel, extracted_entities)

    @classmethod
    def _generate_heuristic_expansion(
        cls,
        title: str,
        channel: str,
        entities: List[str]
    ) -> Dict[str, Any]:
        """Generates domain-aware fallback keywords using entity analysis and taxonomy."""
        primary = entities[0] if entities else (channel or "Kênh")
        sub_title = entities[1] if len(entities) > 1 else ""

        core = list(dict.fromkeys([primary, channel, sub_title] + entities[:4]))
        core = [c for c in core if c]

        t_lower = (title + " " + channel).lower()

        # Context-dependent risk phrases
        if "music" in t_lower or "mv" in t_lower or "chi" in t_lower or "ca" in t_lower:
            risk = ["đạo nhạc", "bản quyền âm nhạc", "quảng cáo minh bạch", "sao chép vũ đạo", "hát nhép"]
            viral = ["#biếnhình", "vũ điệu triệu view", "sound trending tiktok", "challenge điệp khúc"]
            comps = ["Hoàng Thùy Linh", "Hòa Minzy", "Thùy Chi", "DTAP"]
        elif "phim" in t_lower or "film" in t_lower or "review" in t_lower:
            risk = ["spoil phim", "lỗi kịch bản", "sạn phim", "câu view", "đánh giá thiên vị"]
            viral = ["#reviewphim", "phim bom tấn", "bóc trần chi tiết ẩn", "cảnh quay đắt giá"]
            comps = ["Phê Phim", "Kính Hiển Vi", "Tóm Tắt Phim"]
        elif "business" in t_lower or "bloomberg" in t_lower or "tiền" in t_lower:
            risk = ["bê bối tài chính", "thất thoát", "lừa đảo đầu tư", "trừng phạt kinh tế", "khủng hoảng"]
            viral = ["#kinhte", "bí mật dòng tiền", "phân tích vĩ mô", "bài học doanh nghiệp"]
            comps = ["CNBC", "Financial Times", "The Wall Street Journal"]
        else:
            risk = ["tranh cãi chất lượng", "quảng cáo trá hình", "phản hồi tiêu cực", "sự cố truyền thông"]
            viral = ["#trending", "viral clip", "video triệu view", "cộng đồng mạng xôn xao"]
            comps = ["Kênh cùng chủ đề", "Đối thủ cạnh tranh"]

        recommended = list(dict.fromkeys(core[:3] + risk[:2] + viral[:2]))

        return {
            "status": "HEURISTIC_EXPANSION_SUCCESS",
            "model": "rule_based_entity_expander",
            "target_asset": title,
            "primary_entity": primary,
            "categories": {
                "core_entities": core,
                "risk_keywords": risk,
                "viral_slang_hooks": viral,
                "competitor_benchmarks": comps
            },
            "recommended_monitoring_keywords": recommended
        }

ai_keyword_suggester = AIKeywordSuggester()

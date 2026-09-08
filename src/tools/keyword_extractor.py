"""
StudioSonar Intelligent Keyword & Context Extractor Engine.
Extracts high-precision search keywords and named entities from monitored channels,
video packaging, and audience comment friction clusters to avoid broad/generic searching.
"""

import re
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("studiosonar.tools.keyword_extractor")

class KeywordExtractor:
    """
    Extracts targeted keywords and builds deterministic search queries
    based on monitored registry configuration, video metadata, and comment discourse.
    """

    # Common YouTube noise tokens to filter out
    NOISE_TOKENS = [
        r"\bOFFICIAL\s+MUSIC\s+VIDEO\b",
        r"\bOFFICIAL\s+MV\b",
        r"\bOFFICIAL\s+AUDIO\b",
        r"\bOFFICIAL\s+TRAILER\b",
        r"\bOFFICIAL\s+TEASER\b",
        r"\bHIGHLIGHT\s+MEDLEY\b",
        r"\bFULL\s+EPISODE\b",
        r"\bMV\b",
        r"\b4K\b",
        r"\bHD\b",
        r"\[.*?\]",
        r"\(.*?\)",
        r"[\|\-\–\—\•]",
    ]

    # Common PR friction categories & trigger vocabulary (Vietnamese & English)
    FRICTION_TAXONOMY = {
        "transparency_ads": ["quảng cáo", "tài trợ", "nhãn hàng", "trá hình", "sponsor", "disclosure", "pr"],
        "copyright_plagiarism": ["đạo nhạc", "bản quyền", "đạo nhái", "sao chép", "copy", "plagiarism", "copyright"],
        "content_quality": ["sơ sài", "sạn", "dở", "kém", "chất lượng kém", "thất vọng", "cẩu thả", "lỗi kịch bản"],
        "financial_fraud": ["lừa đảo", "đa cấp", "tiền bạc", "scam", "bốc hơi", "thiệt hại", "đốt tiền"],
        "ethics_bias": ["thiên vị", "sai lệch", "sai sự thật", "thiếu trung thực", "câu view", "định kiến"]
    }

    # Viral trend drivers
    VIRAL_DRIVERS = {
        "audio_remix": ["remix", "beat", "phối khí", "sound", "nhạc nền", "điệp khúc", "challenge", "thử thách"],
        "visual_contrast": ["biến hình", "trước sau", "hậu trường", "bts", "visual", "chụp ảnh", "outfit"],
        "curiosity_reaction": ["phản ứng", "reaction", "sự thật", "giải mã", "bóc trần", "nguồn gốc"]
    }

    @classmethod
    def clean_title_entities(cls, title: str) -> List[str]:
        """
        Cleans video titles by stripping platform noise and extracts primary entity keywords.
        Example: "PHƯƠNG MỸ CHI x DTAP | 'THIÊN ĐƯỜNG VỚI NGƯỜI THƯƠNG' | OFFICIAL MUSIC VIDEO"
        -> ["Phương Mỹ Chi", "DTAP", "Thiên Đường Với Người Thương"]
        """
        if not title:
            return []

        # Extract quoted substrings first (e.g. 'THIÊN ĐƯỜNG VỚI NGƯỜI THƯƠNG')
        quoted = re.findall(r"['\"‘“](.*?)['\"’”]", title)

        cleaned = title
        for pattern in cls.NOISE_TOKENS:
            cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

        # Split on separators like 'x', 'feat', 'ft.', '&', ','
        parts = re.split(r"\s+(?:x|feat\.?|ft\.?|&|,)\s+", cleaned, flags=re.IGNORECASE)
        
        entities = []
        for p in parts:
            cand = re.sub(r"\s+", " ", p).strip()
            if cand and len(cand) > 2 and cand.upper() not in ["OFFICIAL", "MUSIC", "VIDEO", "AUDIO"]:
                entities.append(cand)

        for q in quoted:
            q_clean = q.strip()
            if q_clean and q_clean not in entities:
                entities.append(q_clean)

        return entities

    @classmethod
    def extract_friction_keywords(cls, comments: List[str]) -> List[str]:
        """
        Identifies the dominant friction and controversy themes from audience comments.
        """
        if not comments:
            return ["phản hồi dư luận"]

        detected_themes = []
        combined_text = " ".join(comments).lower()

        for category, terms in cls.FRICTION_TAXONOMY.items():
            for term in terms:
                if term in combined_text:
                    detected_themes.append(term)
                    break

        return detected_themes if detected_themes else ["tranh cãi chất lượng"]

    @classmethod
    def build_crisis_search_query(
        cls,
        video_title: str,
        channel_title: str,
        sample_comments: Optional[List[str]] = None,
        custom_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Constructs a laser-targeted Google Search query for PR crisis investigation.
        Combines defined monitoring keywords, cleaned entities, and detected friction terms.
        """
        # 1. Primary entity extraction
        entities = cls.clean_title_entities(video_title)
        primary_entity = entities[0] if entities else channel_title
        subject = entities[1] if len(entities) > 1 else ""

        # 2. Friction keyword extraction from negative comments
        friction_terms = cls.extract_friction_keywords(sample_comments or [])
        primary_friction = friction_terms[0] if friction_terms else "tranh cãi"

        # 3. Incorporate explicit monitoring keywords if defined
        custom = custom_keywords[0] if custom_keywords else ""

        # 4. Construct high-precision search query
        query_parts = []
        if primary_entity:
            query_parts.append(f'"{primary_entity}"')
        if subject:
            query_parts.append(f'"{subject}"')
        elif custom and custom != primary_entity:
            query_parts.append(f'"{custom}"')

        query_parts.append(f'"{primary_friction}"')
        query_parts.append("báo chí OR phản hồi")

        constructed_query = " ".join(query_parts)

        return {
            "query": constructed_query,
            "primary_entity": primary_entity,
            "subject": subject,
            "friction_term": primary_friction,
            "extracted_entities": entities,
            "monitoring_keywords_applied": custom_keywords or []
        }

    @classmethod
    def build_viral_search_query(
        cls,
        trend_topic: str,
        channel_title: Optional[str] = None,
        custom_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Constructs an exact search query to discover the catalyst and source meme of a breakout trend.
        """
        entities = cls.clean_title_entities(trend_topic)
        core_topic = entities[0] if entities else trend_topic

        query_parts = [f'"{core_topic}"']
        if custom_keywords:
            query_parts.append(f'"{custom_keywords[0]}"')
        query_parts.append("trend TikTok viral nguồn gốc challenge")

        constructed_query = " ".join(query_parts)
        return {
            "query": constructed_query,
            "core_topic": core_topic,
            "extracted_entities": entities,
            "monitoring_keywords_applied": custom_keywords or []
        }

keyword_extractor = KeywordExtractor()

"""
Unit and Integration tests for External Attribution & Root-Cause Mapper (Google Search Grounding + ClickHouse).
Validates:
- End-to-end attribution analysis on monitored assets
- ClickHouse telemetry & micro-NLP extraction
- Dual-vector search query formulation
- Gemini 3.8 Flash causal synthesis & Mermaid flowchart generation
- FastAPI GET & POST endpoints
"""

import json
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from src.api.main import app
from src.tools.attribution_mapper import attribution_mapper, ExternalAttributionMapper

client = TestClient(app)

MOCK_LLM_SYNTHESIS = json.dumps({
    "catalyst_type": "TIKTOK_VIRAL_MEME",
    "catalyst_title": "Viral Audio Meme Diffusion on TikTok",
    "confidence_score": 0.95,
    "traffic_surge_reason": "Audio excerpt from the video is trending on TikTok, driving significant cross-platform viewer migration to YouTube.",
    "external_sources_identified": "TikTok user-generated audio remix clips and editorial news features.",
    "content_friction_analysis": "Audience reception is predominantly favorable, with minor comments noting background audio levels competing with vocal clarity.",
    "positive_resonance_summary": "Viewers praise the artistic collaboration, visual staging, and cultural authenticity.",
    "mermaid_flowchart": "flowchart TD\n    A[ClickHouse Surge Z=+3.1σ] --> B[TikTok Viral Meme]\n    B --> C[YouTube Traffic Influx]\n    C --> D[Audience Engagement]\n    D --> E[Monitor Sentiment]",
    "strategic_actions": [
        "Deploy short-form Shorts capitalizing on current sound momentum",
        "Pin an official creator comment thanking community supporters"
    ]
})


@patch("src.core.llm_client.GeminiLLMClient.generate", return_value=MOCK_LLM_SYNTHESIS)
def test_attribution_mapper_direct_service(mock_generate):
    """Validates that ExternalAttributionMapper analyzes video and returns complete causal contract."""
    res = attribution_mapper.analyze_video_attribution("UH21OnJwxZE")
    assert res["status"] == "SUCCESS"
    assert res["video_id"] == "UH21OnJwxZE"
    assert "telemetry_snapshot" in res
    assert "z_score" in res["telemetry_snapshot"]
    assert "polarization_spread" in res["telemetry_snapshot"]
    assert "top_toxic_ngrams" in res["telemetry_snapshot"]

    assert "attribution_analysis" in res
    attr = res["attribution_analysis"]
    assert attr["catalyst_type"] == "TIKTOK_VIRAL_MEME"
    assert "traffic_surge_reason" in attr
    assert "content_friction_analysis" in attr
    assert "mermaid_flowchart" in attr
    assert "flowchart" in attr["mermaid_flowchart"] or "graph" in attr["mermaid_flowchart"]
    assert "strategic_actions" in attr
    assert isinstance(attr["strategic_actions"], list)

    assert "search_grounding" in res
    assert "catalyst_query" in res["search_grounding"]
    assert "friction_query" in res["search_grounding"]
    assert "citations" in res["search_grounding"]


@patch("src.core.llm_client.GeminiLLMClient.generate", return_value=MOCK_LLM_SYNTHESIS)
def test_attribution_mapper_get_endpoint(mock_generate):
    """Validates GET /api/v1/analytics/attribution-map endpoint."""
    response = client.get("/api/v1/analytics/attribution-map?video_id=UH21OnJwxZE")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["video_id"] == "UH21OnJwxZE"
    assert "telemetry_snapshot" in data
    assert "attribution_analysis" in data


@patch("src.core.llm_client.GeminiLLMClient.generate", return_value=MOCK_LLM_SYNTHESIS)
def test_attribution_mapper_post_endpoint(mock_generate):
    """Validates POST /api/v1/analytics/attribution-map endpoint."""
    response = client.post("/api/v1/analytics/attribution-map", json={"video_id": "UH21OnJwxZE"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "mermaid_flowchart" in data["attribution_analysis"]


def test_attribution_mapper_deterministic_fallback():
    """Validates deterministic fallback generator when LLM is unavailable."""
    mapper = ExternalAttributionMapper()
    fallback = mapper._build_deterministic_attribution(
        video_title="THIÊN ĐƯỜNG VỚI NGƯỜI THƯƠNG | OFFICIAL MUSIC VIDEO",
        primary_entity="Phương Mỹ Chi",
        z_score=3.2,
        z_status="CRITICAL_OUTLIER_3SIGMA",
        views_hr=4500.0,
        slope_info={"acceleration_slope": 12.5, "acceleration_verdict": "RAPID_ACCELERATION"},
        pol_spread=1.45,
        pol_status="CIVIL_WAR_POLARIZED",
        weighted_ngrams=[{"phrase": "quảng cáo lộ liễu"}],
        friction_comments=[{"comment_text": "quảng cáo nhiều quá"}],
        bot_verdict="ORGANIC_GENUINE_AUDIENCE",
        catalyst_snippets=[{"snippet": "video đang viral mạnh trên tiktok"}],
        friction_snippets=[{"snippet": "khán giả tranh cãi về quảng cáo"}]
    )

    assert fallback["catalyst_type"] in ["PR_CONTROVERSY_SURGE", "TIKTOK_VIRAL_MEME"]
    assert "flowchart" in fallback["mermaid_flowchart"] or "graph" in fallback["mermaid_flowchart"]
    assert "quảng cáo" in fallback["content_friction_analysis"].lower() or "ma sát" in fallback["content_friction_analysis"].lower()
    assert len(fallback["strategic_actions"]) >= 2


def test_attribution_mapper_clean_mermaid_syntax():
    """Validates mermaid syntax cleaning."""
    mapper = ExternalAttributionMapper()
    raw = "A --> B\nB --> C"
    cleaned = mapper._clean_mermaid_syntax(raw)
    assert cleaned.startswith("flowchart TD")
    assert "A --> B" in cleaned

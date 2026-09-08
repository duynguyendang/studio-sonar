import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.tools.google_search_tool import google_search_tool, GoogleSearchLiveIntel
from src.mcp.search_tools import search_google_live_intel
from src.agents.pr_crisis_agent import pr_crisis_agent
from src.agents.viral_content_agent import viral_content_agent

def test_google_search_tool_pr_controversy():
    """Test searching for PR crisis and controversy context."""
    query = "Phương Mỹ Chi scandal controversy disclosure"
    res = google_search_tool.search_live_intel(query=query, num_results=3)
    
    assert res is not None
    assert "status" in res
    assert res["query"] == query
    assert res["results_count"] >= 1
    assert len(res["results"]) >= 1
    
    first = res["results"][0]
    assert "title" in first
    assert "snippet" in first
    assert "source" in first
    assert "link" in first
    assert len(first["snippet"]) > 10

def test_google_search_tool_viral_meme():
    """Test searching for viral breakout origin and meme catalysts."""
    query = "viral folk fusion sound TikTok trending challenge"
    res = google_search_tool.search_live_intel(query=query, num_results=2)
    
    assert res is not None
    assert res["results_count"] >= 1
    first = res["results"][0]
    assert "title" in first
    assert "snippet" in first

def test_mcp_search_tool_function():
    """Test the MCP declarative tool wrapper for ADK agents."""
    res = search_google_live_intel("Tech AI Agent controversy news")
    assert isinstance(res, dict)
    assert res["results_count"] > 0

def test_agents_have_search_tool_bound():
    """Verify that both PR Crisis and Viral Creator agents have the search tool."""
    pr_tool_names = [getattr(t, "__name__", str(t)) for t in pr_crisis_agent.tools]
    assert "search_google_live_intel" in pr_tool_names

    vc_tool_names = [getattr(t, "__name__", str(t)) for t in viral_content_agent.tools]
    assert "search_google_live_intel" in vc_tool_names

def test_agent_search_tool_execution():
    """Verify that search_google_live_intel executes cleanly when called by PR Crisis and Viral Creator agents."""
    # 1. PR Crisis Agent search tool invocation
    pr_search_tool = [t for t in pr_crisis_agent.tools if getattr(t, "__name__", "") == "search_google_live_intel"][0]
    pr_result = pr_search_tool(query="Kiểm Định Phim review tranh cãi spoiler", num_results=2)
    assert pr_result is not None
    assert pr_result["results_count"] >= 1
    assert "snippet" in pr_result["results"][0]

    # 2. Viral Creator Agent search tool invocation
    vc_search_tool = [t for t in viral_content_agent.tools if getattr(t, "__name__", "") == "search_google_live_intel"][0]
    vc_result = vc_search_tool(query="viral audio dance trend TikTok", num_results=2)
    assert vc_result is not None
    assert vc_result["results_count"] >= 1
    assert "snippet" in vc_result["results"][0]

def test_anomaly_grounding_integration():
    """Verify that an anomaly event payload is properly enriched with search context."""
    anomaly_payload = {
        "video_title": "Phương Mỹ Chi - Vũ Trụ Có Anh",
        "channel_title": "Phương Mỹ Chi",
        "velocity_spike_pct": 240.0
    }
    query = f"{anomaly_payload['video_title']} tranh cãi phản hồi scandal controversy"
    search_intel = search_google_live_intel(query=query, num_results=2)
    
    assert search_intel["status"] in ["LIVE_SEARCH_SUCCESS", "GROUNDED_INTEL_SYNTHESIS"]
    assert len(search_intel["results"]) > 0
    top_snippet = search_intel["results"][0]["snippet"]
    
    # Enrich root cause with search snippet
    grounded_root_cause = f"Backlash (+{anomaly_payload['velocity_spike_pct']}%) grounded by: {top_snippet}"
    assert len(grounded_root_cause) > 50

def test_keyword_extractor_targeted_query():
    """Verify that KeywordExtractor correctly extracts entities, friction terms and applies monitoring keywords."""
    from src.tools.keyword_extractor import keyword_extractor
    from src.core.registry_manager import registry_manager
    
    title = "PHƯƠNG MỸ CHI x DTAP | 'THIÊN ĐƯỜNG VỚI NGƯỜI THƯƠNG' | OFFICIAL MUSIC VIDEO"
    comments = ["Quảng cáo nhãn hàng quá lố trong video ca nhạc", "Thiếu minh bạch tài trợ"]
    custom_kws = registry_manager.get_monitoring_keywords(video_id="UH21OnJwxZE")
    
    query_info = keyword_extractor.build_crisis_search_query(
        video_title=title,
        channel_title="Phương Mỹ Chi",
        sample_comments=comments,
        custom_keywords=custom_kws
    )
    
    assert "PHƯƠNG MỸ CHI" in query_info["query"]
    assert query_info["friction_term"] == "quảng cáo"
    assert len(query_info["monitoring_keywords_applied"]) > 0
    assert "Phương Mỹ Chi" in query_info["monitoring_keywords_applied"]

def test_ai_keyword_suggester():
    """Verify that AIKeywordSuggester proposes multi-dimensional monitoring keywords."""
    from src.tools.ai_keyword_suggester import ai_keyword_suggester
    
    res = ai_keyword_suggester.suggest_keywords(
        title="PHƯƠNG MỸ CHI x DTAP | 'THIÊN ĐƯỜNG VỚI NGƯỜI THƯƠNG' | OFFICIAL MV",
        channel="Phương Mỹ Chi",
        category="Music"
    )
    
    assert res is not None
    assert "categories" in res
    assert len(res["categories"]["core_entities"]) > 0
    assert len(res["categories"]["risk_keywords"]) > 0
    assert len(res["recommended_monitoring_keywords"]) > 0
    assert any("Phương Mỹ Chi" in k or "Chi" in k for k in res["recommended_monitoring_keywords"])

def test_copilot_keyword_suggestion_chat():
    """Verify that SettingsCopilot handles natural language requests for keyword suggestions."""
    from src.agents.settings_copilot_agent import settings_copilot
    
    cmd_res = settings_copilot.process_chat_command("Gợi ý từ khóa cho video Phương Mỹ Chi Vũ Trụ Có Anh")
    assert cmd_res["action_executed"] == "SUGGEST_KEYWORDS"
    assert "reply" in cmd_res
    assert "từ khóa theo dõi" in cmd_res["reply"].lower()

def test_vertex_ai_search_grounding_integration(monkeypatch):
    """Verify that GoogleSearchLiveIntel executes Vertex AI Search Grounding with Service Account ADC."""
    from src.tools.google_search_tool import google_search
    
    # 1. Test graceful fallback when no GCP SA is active
    res = google_search.search_live_intel("Phương Mỹ Chi scandal bản quyền âm nhạc")
    assert res is not None
    assert res["status"] in ["VERTEX_SEARCH_GROUNDING_SUCCESS", "GROUNDED_INTEL_SYNTHESIS", "LIVE_SEARCH_SUCCESS"]
    assert len(res["results"]) > 0

    # 2. Test mocked Vertex AI Grounding response via ADC
    mock_snippets = [
        {
            "title": "Báo Dân Trí: Độc quyền thông tin vụ việc",
            "link": "https://dantri.com.vn/giai-tri/phuong-my-chi-len-tieng",
            "snippet": "Đại diện ca sĩ lên tiếng xác nhận về bản quyền ca khúc.",
            "source": "dantri.com.vn"
        }
    ]
    monkeypatch.setattr(google_search, "_search_via_vertex_grounding", lambda query, num_results=4: mock_snippets)
    
    vertex_res = google_search.search_live_intel("Phương Mỹ Chi bản quyền")
    assert vertex_res["status"] == "VERTEX_SEARCH_GROUNDING_SUCCESS"
    assert vertex_res["auth_mode"] == "GCP_SERVICE_ACCOUNT_ADC"
    assert vertex_res["results"][0]["source"] == "dantri.com.vn"





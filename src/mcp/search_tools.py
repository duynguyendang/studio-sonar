"""
Google ADK MCP Tool Bindings for Google Search Live Intelligence.
Enables PRCrisisStrategistAgent and ViralContentCreatorAgent to autonomously query the web.
"""

from typing import Dict, Any
from src.tools.google_search_tool import google_search_tool

def search_google_live_intel(query: str, num_results: int = 4) -> Dict[str, Any]:
    """
    Autonomously searches Google for live external context regarding breaking news,
    sponsor controversies, Reddit/X sentiment, or viral cultural meme catalysts.

    Args:
        query: The search query string (e.g. "Brand Name controversy disclosure news").
        num_results: Max number of news/social snippets to return.

    Returns:
        Structured dictionary with snippets, citations, and search metadata.
    """
    return google_search_tool.search_live_intel(query=query, num_results=num_results)

def suggest_ai_monitoring_keywords(title: str, channel: str = "", category: str = "") -> Dict[str, Any]:
    """
    Uses Gemini 3.7 Flash AI to analyze a video or channel and suggest multi-dimensional
    monitoring keywords (core entities, PR risk terms, viral meme phrases, competitors).

    Args:
        title: Title of the video or channel topic.
        channel: Name of the channel/creator.
        category: Niche category (e.g. Music, Entertainment, Business).

    Returns:
        Categorized keyword suggestions and recommended monitoring list.
    """
    from src.tools.ai_keyword_suggester import ai_keyword_suggester
    return ai_keyword_suggester.suggest_keywords(title=title, channel=channel, category=category)


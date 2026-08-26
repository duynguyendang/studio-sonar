from typing import Dict, List, Any
from src.data.bigquery_client import bq_client

def query_bigquery_sentiment_spikes(
    time_window_hours: int = 6,
    min_comment_velocity_pct: float = 200.0,
    sentiment_threshold: float = -0.60
) -> Dict[str, Any]:
    """
    Queries Google BigQuery for sudden velocity spikes in negative sentiment or critical brand keywords.
    
    Args:
        time_window_hours: Time window in hours to analyze (e.g. 6).
        min_comment_velocity_pct: Minimum acceleration percentage over baseline (e.g. 200.0).
        sentiment_threshold: Upper threshold for negative sentiment (-1.0 to +1.0).
        
    Returns:
        Dictionary containing list of detected anomaly spikes and root cause snippets.
    """
    results = bq_client.query_sentiment_velocity_spikes(
        time_window_hours=time_window_hours,
        min_velocity_pct=min_comment_velocity_pct,
        sentiment_threshold=sentiment_threshold
    )
    return {
        "status": "SUCCESS",
        "anomaly_count": len(results),
        "anomalies": results
    }

def query_bigquery_viral_trends(
    min_view_acceleration_pct: float = 300.0,
    lookback_hours: int = 8
) -> Dict[str, Any]:
    """
    Queries Google BigQuery for breakout viral topics and retention hook trajectories across YouTube and TikTok.
    
    Args:
        min_view_acceleration_pct: Minimum view growth velocity compared to historical average (e.g. 300.0).
        lookback_hours: Lookback window in hours (e.g. 8).
        
    Returns:
        Dictionary containing viral trend topics, audience comments, and hook retention formulas.
    """
    results = bq_client.query_viral_growth_trends(
        min_view_acceleration_pct=min_view_acceleration_pct,
        lookback_hours=lookback_hours
    )
    return {
        "status": "SUCCESS",
        "trend_count": len(results),
        "trends": results
    }

def search_bigquery_vector_context(
    query_text: str,
    top_k: int = 5
) -> Dict[str, Any]:
    """
    Uses BigQuery Vector Search on text-embedding-004 vectors to find semantic clusters around specific topics.
    
    Args:
        query_text: Natural language concept or drama topic to search.
        top_k: Maximum number of representative clusters to return.
        
    Returns:
        Dictionary with semantic clusters, representative quotes, and similarity scores.
    """
    clusters = bq_client.search_vector_topic_clusters(query_text=query_text, top_k=top_k)
    return {
        "status": "SUCCESS",
        "query": query_text,
        "clusters": clusters
    }

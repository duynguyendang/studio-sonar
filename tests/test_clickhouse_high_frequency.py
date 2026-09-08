"""
Unit and Integration tests for ClickHouse High-Frequency Operational Radar (U1-U4).
Validates:
- 1-minute radar tick loop & anomaly spike detection (U1)
- Sub-10ms dashboard polling & cost defense telemetry (U2)
- Forensic drill-down for bot brigade vs organic crisis detection (U3)
- FastAPI routing endpoints for hot path operations
"""

import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.data.clickhouse_client import ch_client
from src.agents.orchestrator import taskmaster_orchestrator

client = TestClient(app)


def test_clickhouse_client_hot_counters():
    """Validates get_hot_counters returns sub-10ms telemetry and financial cost defense."""
    res = ch_client.get_hot_counters()
    assert res["status"] == "HOT_LAYER_ONLINE"
    assert "hot_queries_served" in res
    assert "latency" in res
    assert "p50_ms" in res["latency"]
    assert "p95_ms" in res["latency"]
    assert "sparkline_30m" in res
    assert len(res["sparkline_30m"]) == 6
    assert "cost_defense" in res
    assert res["cost_defense"]["monthly_saving_usd"] >= 14.0


def test_clickhouse_client_raw_velocity_query():
    """Validates query_ad_hoc_raw_velocity_spikes runs raw-column multi-window aggregation."""
    spikes = ch_client.query_ad_hoc_raw_velocity_spikes()
    assert isinstance(spikes, list)
    if spikes:
        spike = spikes[0]
        assert "video_id" in spike
        assert "rate_5m_per_hr" in spike
        assert "rate_6h_per_hr" in spike
        assert spike["rate_5m_per_hr"] >= spike["rate_6h_per_hr"]


def test_clickhouse_client_brigade_forensic_drilldown():
    """Validates drill_down_spike_brigade_analysis forensic math and PR recommendation."""
    forensics = ch_client.drill_down_spike_brigade_analysis("UH21OnJwxZE")
    assert forensics["status"] == "DRILL_DOWN_COMPLETE"
    assert forensics["video_id"] == "UH21OnJwxZE"
    assert "author_diversity_ratio" in forensics
    assert "p95_toxicity" in forensics
    assert "verdict" in forensics
    assert forensics["verdict"] in ["COORDINATED_BRIGADE_ATTACK", "ORGANIC_COMMUNITY_OUTCRY"]
    assert "recommended_containment" in forensics


def test_orchestrator_radar_tick_execution():
    """Validates taskmaster orchestrator 1-minute radar tick loop."""
    result = taskmaster_orchestrator.run_radar_tick()
    assert result["status"] in ["RADAR_TICK_COMPLETED", "RADAR_TICK_ANOMALIES_DETECTED", "RADAR_TICK_NORMAL"]
    assert "execution_time_ms" in result
    assert result["execution_time_ms"] > 0
    assert "anomalies_detected" in result


def test_api_hot_counters_endpoint():
    """Validates GET /api/v1/hot/counters endpoint."""
    response = client.get("/api/v1/hot/counters")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HOT_LAYER_ONLINE"
    assert "latency" in data
    assert "cost_defense" in data


def test_api_radar_tick_endpoint():
    """Validates POST /api/v1/radar-tick endpoint."""
    response = client.post("/api/v1/radar-tick")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["RADAR_TICK_COMPLETED", "RADAR_TICK_ANOMALIES_DETECTED", "RADAR_TICK_NORMAL"]
    assert "execution_time_ms" in data



def test_api_brigade_drilldown_endpoint():
    """Validates POST /api/v1/analytics/brigade-drilldown endpoint."""
    response = client.post(
        "/api/v1/analytics/brigade-drilldown",
        json={"video_id": "UH21OnJwxZE"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "DRILL_DOWN_COMPLETE"
    assert data["video_id"] == "UH21OnJwxZE"
    assert "author_diversity_ratio" in data
    assert "author_entropy" in data
    assert "p95_toxicity" in data


def test_clickhouse_decay_adjusted_heat_spikes():
    """Validates exponentialTimeDecayedCount query."""
    spikes = ch_client.query_decay_adjusted_heat_spikes(halflife_seconds=600)
    assert isinstance(spikes, list)
    if spikes:
        s = spikes[0]
        assert "video_id" in s
        assert "heat_halflife_10m" in s


def test_clickhouse_velocity_acceleration_slope():
    """Validates simpleLinearRegression slope calculation."""
    res = ch_client.query_velocity_acceleration_slope("UH21OnJwxZE")
    assert res["video_id"] == "UH21OnJwxZE"
    assert "slope_per_sec" in res
    assert res["momentum_status"] in ["ACCELERATING", "DECELERATING", "PLATEAU"]


def test_clickhouse_cross_platform_synergy_correlation():
    """Validates corr(yt, tt) Pearson correlation."""
    res = ch_client.query_cross_platform_synergy_correlation(days=7)
    assert "pearson_correlation" in res
    assert -1.0 <= res["pearson_correlation"] <= 1.0
    assert "synergy_verdict" in res


def test_clickhouse_ascii_sparkbar():
    """Validates sparkbar(48) generation."""
    bar = ch_client.query_ascii_sparkbar("UH21OnJwxZE", hours=48)
    assert isinstance(bar, str)
    assert len(bar) > 0


def test_clickhouse_top_friction_terms():
    """Validates topK(5) extraction."""
    terms = ch_client.query_top_friction_terms("UH21OnJwxZE", top_n=5)
    assert isinstance(terms, list)
    assert len(terms) > 0


def test_api_synergy_correlation_endpoint():
    """Validates GET /api/v1/analytics/synergy-correlation endpoint."""
    response = client.get("/api/v1/analytics/synergy-correlation")
    assert response.status_code == 200
    data = response.json()
    assert "pearson_correlation" in data
    assert "synergy_verdict" in data


def test_api_velocity_slope_endpoint():
    """Validates GET /api/v1/analytics/velocity-slope endpoint."""
    response = client.get("/api/v1/analytics/velocity-slope?video_id=UH21OnJwxZE")
    assert response.status_code == 200
    data = response.json()
    assert "slope_per_sec" in data
    assert "momentum_status" in data


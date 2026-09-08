"""
Unit tests for StudioSonar Guardrails and False-Alarm Dampening.
"""

import pytest
from src.core.guardrails import StudioSonarGuardrails


def test_validate_crisis_anomaly_passed():
    """Validates that a severe anomaly passing all thresholds is confirmed."""
    anomaly = {
        "velocity_spike_pct": 320.0,
        "avg_sentiment": -0.75,
        "negative_comments_count": 25,
    }
    passed, reason = StudioSonarGuardrails.validate_crisis_anomaly(anomaly)
    assert passed is True
    assert "PASSED_GUARDRAIL" in reason


def test_validate_crisis_anomaly_dampened_velocity():
    """Validates that low velocity anomalies are dampened."""
    anomaly = {
        "velocity_spike_pct": 120.0,
        "avg_sentiment": -0.80,
        "negative_comments_count": 30,
    }
    passed, reason = StudioSonarGuardrails.validate_crisis_anomaly(anomaly)
    assert passed is False
    assert "Velocity spike" in reason


def test_validate_crisis_anomaly_dampened_sentiment():
    """Validates that neutral/positive sentiment anomalies are dampened."""
    anomaly = {
        "velocity_spike_pct": 350.0,
        "avg_sentiment": 0.20,
        "negative_comments_count": 30,
    }
    passed, reason = StudioSonarGuardrails.validate_crisis_anomaly(anomaly)
    assert passed is False
    assert "Average sentiment" in reason


def test_validate_crisis_anomaly_insufficient_sample():
    """Validates that small sample sizes (< 10) are dampened."""
    anomaly = {
        "velocity_spike_pct": 400.0,
        "avg_sentiment": -0.90,
        "negative_comments_count": 4,
    }
    passed, reason = StudioSonarGuardrails.validate_crisis_anomaly(anomaly)
    assert passed is False
    assert "Insufficient sample size" in reason


def test_validate_viral_trend_thresholds():
    """Validates breakout acceleration threshold for viral content generator."""
    # Breakout momentum
    trend_high = {"cross_platform_acceleration_pct": 280.0}
    passed_high, reason_high = StudioSonarGuardrails.validate_viral_trend(trend_high)
    assert passed_high is True
    assert "PASSED_GUARDRAIL" in reason_high

    # Low momentum
    trend_low = {"cross_platform_acceleration_pct": 110.0}
    passed_low, reason_low = StudioSonarGuardrails.validate_viral_trend(trend_low)
    assert passed_low is False
    assert "DAMPENED" in reason_low

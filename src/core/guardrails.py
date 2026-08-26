import logging
from typing import Dict, Any, Tuple
from src.core.config import settings

logger = logging.getLogger("studiosonar.guardrails")

class StudioSonarGuardrails:
    """Safety and False-Alarm Dampening Guardrails for StudioSonar."""

    @staticmethod
    def validate_crisis_anomaly(anomaly: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates whether a detected spike is a genuine high-urgency crisis or routine noise.
        
        Rules:
        1. Velocity spike must exceed MIN_ANOMALY_VELOCITY_PCT (default: 250%).
        2. Average sentiment must be below CRITICAL_SENTIMENT_THRESHOLD (default: -0.60).
        3. Comment sample volume must be statistically significant (>10 comments).
        """
        velocity = anomaly.get("velocity_spike_pct", 0.0)
        sentiment = anomaly.get("avg_sentiment", 0.0)
        negative_count = anomaly.get("negative_comments_count", 0)

        if velocity < settings.min_anomaly_velocity_pct:
            return False, f"DAMPENED: Velocity spike (+{velocity:.1f}%) is below minimum threshold (+{settings.min_anomaly_velocity_pct}%)."

        if sentiment > settings.critical_sentiment_threshold:
            return False, f"DAMPENED: Average sentiment ({sentiment:.2f}) is not severe enough (threshold: {settings.critical_sentiment_threshold})."

        if negative_count < 10:
            return False, f"DAMPENED: Insufficient sample size ({negative_count} comments)."

        return True, "PASSED_GUARDRAIL: Confirmed critical PR anomaly."

    @staticmethod
    def validate_viral_trend(trend: Dict[str, Any]) -> Tuple[bool, str]:
        """Validates whether a trend has enough breakout momentum to draft content."""
        acceleration = trend.get("cross_platform_acceleration_pct", 0.0)
        if acceleration < 200.0:
            return False, f"DAMPENED: Trend acceleration ({acceleration:.1f}%) is below breakout velocity threshold (200%)."

        return True, "PASSED_GUARDRAIL: Confirmed high-growth viral trend."

guardrails = StudioSonarGuardrails()

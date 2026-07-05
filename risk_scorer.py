"""
Rule-based risk scoring engine.

Computes a risk score (0–100) by combining signals from
the ML classifier, LLM analysis, and keyword heuristics.
Maps the score to a risk level: Low | Medium | High | Critical.
"""

from config import CRISIS_KEYWORDS, RISK_THRESHOLDS, RISK_WEIGHTS
from models import LLMAnalysis, MLPrediction, RiskAssessment
from utils import count_crisis_keywords


def calculate_risk(
    message: str,
    llm_analysis: LLMAnalysis,
    ml_prediction: MLPrediction,
) -> RiskAssessment:
    """
    Calculate a composite risk score from all available signals.

    Scoring breakdown (max 100 points):
        - ML confidence (if crisis predicted): 0–30
        - Urgency level from LLM:              0–25
        - Source absent penalty:                0–10
        - Evidence absent penalty:              0–10
        - Crisis keyword density:               0–15
        - Message length heuristic:             0–10

    Args:
        message: Original message text.
        llm_analysis: Features extracted by the LLM analyzer.
        ml_prediction: Prediction from the ML classifier.

    Returns:
        RiskAssessment with score, level, and breakdown.
    """
    breakdown = {}
    total = 0

    # ── 1. ML Confidence ────────────────────────────────────────────
    ml_weight = RISK_WEIGHTS["ml_confidence"]
    if ml_prediction.label == "Likely Real Crisis":
        ml_score = int(ml_prediction.confidence * ml_weight)
    else:
        # If predicted non-crisis, invert: higher confidence in
        # non-crisis → lower risk score
        ml_score = int((1 - ml_prediction.confidence) * ml_weight)
    breakdown["ML Confidence"] = ml_score
    total += ml_score

    # ── 2. Urgency Level ────────────────────────────────────────────
    urgency_map = {
        "low": 0.0,
        "medium": 0.4,
        "high": 0.7,
        "critical": 1.0,
    }
    urgency_weight = RISK_WEIGHTS["urgency"]
    urgency_factor = urgency_map.get(llm_analysis.urgency, 0.0)
    urgency_score = int(urgency_factor * urgency_weight)
    breakdown["Urgency Level"] = urgency_score
    total += urgency_score

    # ── 3. Source Absent Penalty ────────────────────────────────────
    source_weight = RISK_WEIGHTS["source_absent"]
    if llm_analysis.source_present:
        source_score = 0  # No penalty — source cited
    else:
        source_score = source_weight  # Penalty for no source
    breakdown["Source Absent"] = source_score
    total += source_score

    # ── 4. Evidence Absent Penalty ──────────────────────────────────
    evidence_weight = RISK_WEIGHTS["evidence_absent"]
    if llm_analysis.evidence_present:
        evidence_score = 0
    else:
        evidence_score = evidence_weight
    breakdown["Evidence Absent"] = evidence_score
    total += evidence_score

    # ── 5. Crisis Keyword Density ───────────────────────────────────
    keyword_weight = RISK_WEIGHTS["keyword_density"]
    keyword_count = count_crisis_keywords(message, CRISIS_KEYWORDS)
    # Scale: 0 keywords → 0, 5+ keywords → max
    keyword_score = min(int((keyword_count / 5) * keyword_weight), keyword_weight)
    breakdown["Keyword Density"] = keyword_score
    total += keyword_score

    # ── 6. Message Length Heuristic ─────────────────────────────────
    length_weight = RISK_WEIGHTS["message_length"]
    msg_len = len(message)
    # Very short messages (<20 chars) or very long ones (>280 chars)
    # are slightly more suspicious in a crisis rumor context
    if msg_len < 20:
        length_score = length_weight  # Very short → suspicious
    elif msg_len > 280:
        length_score = int(length_weight * 0.5)  # Long → moderately suspicious
    else:
        length_score = 0  # Normal length
    breakdown["Message Length"] = length_score
    total += length_score

    # ── Clamp to 0–100 ─────────────────────────────────────────────
    total = max(0, min(100, total))

    # ── Map to risk level ───────────────────────────────────────────
    if total <= RISK_THRESHOLDS["low"]:
        level = "Low"
    elif total <= RISK_THRESHOLDS["medium"]:
        level = "Medium"
    elif total <= RISK_THRESHOLDS["high"]:
        level = "High"
    else:
        level = "Critical"

    return RiskAssessment(score=total, level=level, breakdown=breakdown)

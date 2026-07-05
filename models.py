"""
Shared data models for the Crisis Rumor Verification Agent.

All modules communicate through these dataclasses to ensure
type safety and clean interfaces.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class LLMAnalysis:
    """Structured features extracted by the LLM analyzer."""

    crisis_type: str = "Unknown"
    location: str = "Unknown"
    urgency: str = "low"  # low | medium | high | critical
    source_present: bool = False
    evidence_present: bool = False
    raw_reasoning: str = ""


@dataclass
class MLPrediction:
    """Prediction from the ML disaster tweet classifier."""

    label: str = "Likely Non-Crisis"  # "Likely Real Crisis" | "Likely Non-Crisis"
    confidence: float = 0.5
    model_used: str = "TF-IDF + Logistic Regression"


@dataclass
class RiskAssessment:
    """Rule-based risk score computed from all available signals."""

    score: int = 0  # 0–100
    level: str = "Low"  # Low | Medium | High | Critical
    breakdown: dict = field(default_factory=dict)


@dataclass
class Recommendation:
    """Safe, deterministic recommendation for the user."""

    verdict: str = ""  # e.g., "Likely Safe", "Verify Before Sharing", etc.
    emoji: str = ""
    message: str = ""
    disclaimer: str = (
        "⚠️ This is an automated assessment. "
        "Always verify with official sources before sharing."
    )


@dataclass
class VerificationReport:
    """Complete report aggregating all analysis results."""

    original_message: str = ""
    llm_analysis: Optional[LLMAnalysis] = None
    ml_prediction: Optional[MLPrediction] = None
    risk_assessment: Optional[RiskAssessment] = None
    recommendation: Optional[Recommendation] = None
    processing_time_seconds: float = 0.0

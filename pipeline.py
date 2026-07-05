"""
Pipeline orchestrator for the Crisis Rumor Verification Agent.

Central coordinator that wires all analysis modules together:
    LLM Analyzer → ML Classifier → Risk Scorer → Recommendation Engine

Returns a unified VerificationReport.
"""

import logging
import time

from llm_analyzer import analyze_with_llm
from ml_classifier import DisasterClassifier
from models import VerificationReport
from recommendation import generate_recommendation
from risk_scorer import calculate_risk

logger = logging.getLogger(__name__)

# ── Singleton classifier (loaded once) ──────────────────────────────
_classifier: DisasterClassifier | None = None


def _get_classifier() -> DisasterClassifier:
    """Lazy-load the ML classifier singleton."""
    global _classifier
    if _classifier is None:
        _classifier = DisasterClassifier()
    return _classifier


def run_pipeline(message: str) -> VerificationReport:
    """
    Run the full verification pipeline on a user message.

    Steps:
        1. LLM analysis → extract structured features
        2. ML classification → predict real crisis vs non-crisis
        3. Risk scoring → compute 0–100 risk score
        4. Recommendation → generate safe guidance

    Args:
        message: The disaster-related message from the user.

    Returns:
        VerificationReport containing all results.
    """
    start_time = time.time()

    logger.info("Pipeline started for message: %s...", message[:80])

    # ── Step 1: LLM Feature Extraction ──────────────────────────────
    logger.info("Step 1/4: LLM Analysis")
    llm_analysis = analyze_with_llm(message)
    logger.info(
        "  → crisis_type=%s, location=%s, urgency=%s",
        llm_analysis.crisis_type,
        llm_analysis.location,
        llm_analysis.urgency,
    )

    # ── Step 2: ML Classification ──────────────────────────────────
    logger.info("Step 2/4: ML Classification")
    classifier = _get_classifier()
    ml_prediction = classifier.predict(message)
    logger.info(
        "  → label=%s, confidence=%.2f",
        ml_prediction.label,
        ml_prediction.confidence,
    )

    # ── Step 3: Risk Scoring ───────────────────────────────────────
    logger.info("Step 3/4: Risk Scoring")
    risk_assessment = calculate_risk(message, llm_analysis, ml_prediction)
    logger.info(
        "  → score=%d, level=%s",
        risk_assessment.score,
        risk_assessment.level,
    )

    # ── Step 4: Recommendation ─────────────────────────────────────
    logger.info("Step 4/4: Recommendation")
    recommendation = generate_recommendation(risk_assessment)
    logger.info("  → verdict=%s", recommendation.verdict)

    # ── Assemble Report ────────────────────────────────────────────
    elapsed = time.time() - start_time
    logger.info("Pipeline completed in %.2f seconds.", elapsed)

    return VerificationReport(
        original_message=message,
        llm_analysis=llm_analysis,
        ml_prediction=ml_prediction,
        risk_assessment=risk_assessment,
        recommendation=recommendation,
        processing_time_seconds=round(elapsed, 2),
    )

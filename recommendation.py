"""
Safe recommendation generator.

Produces deterministic, human-readable guidance based on
the risk assessment. Rules-based (not LLM) to ensure
consistent and safe output.
"""

from models import Recommendation, RiskAssessment


def generate_recommendation(risk: RiskAssessment) -> Recommendation:
    """
    Generate a safe recommendation based on the risk level.

    Recommendations are deterministic and always include a
    disclaimer urging users to verify with official sources.

    Args:
        risk: The computed RiskAssessment.

    Returns:
        Recommendation with verdict, emoji, and guidance message.
    """
    if risk.level == "Low":
        return Recommendation(
            verdict="Likely Safe",
            emoji="✅",
            message=(
                "This message appears to be non-crisis content. "
                "No immediate indicators of a real disaster were detected. "
                "The language, context, and supporting signals suggest this is "
                "either unrelated to a crisis or uses crisis-related words "
                "in a non-emergency context."
            ),
        )

    if risk.level == "Medium":
        return Recommendation(
            verdict="Verify Before Sharing",
            emoji="⚠️",
            message=(
                "This message shows some crisis indicators, but the evidence "
                "is inconclusive. Before sharing or acting on this information:\n\n"
                "• Check official news sources for corroboration.\n"
                "• Look for the original source of this claim.\n"
                "• Verify any specific numbers, locations, or names mentioned.\n"
                "• Wait for official confirmation before spreading the message."
            ),
        )

    if risk.level == "High":
        return Recommendation(
            verdict="Exercise Caution",
            emoji="🔴",
            message=(
                "This message has significant crisis indicators. "
                "However, unverified crisis messages can cause panic and "
                "divert emergency resources. Please:\n\n"
                "• Do NOT share until verified by official sources.\n"
                "• Cross-check with at least two independent news outlets.\n"
                "• Contact local authorities if you believe you are in danger.\n"
                "• Report the message to platform moderators if it appears "
                "to be deliberately misleading."
            ),
        )

    # Critical
    return Recommendation(
        verdict="Urgent — Check Official Sources",
        emoji="🚨",
        message=(
            "This message contains strong crisis indicators with high "
            "urgency signals. While this may represent a real emergency, "
            "misinformation is also most dangerous during crises.\n\n"
            "• Immediately check official channels (government agencies, "
            "verified news outlets, emergency services).\n"
            "• Do NOT forward this message without verification.\n"
            "• If you are in the affected area, follow official evacuation "
            "or safety instructions.\n"
            "• Call emergency services (911 / local equivalent) if you "
            "need immediate assistance."
        ),
    )

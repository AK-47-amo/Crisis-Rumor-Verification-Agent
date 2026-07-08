import json
import logging
import re

from groq import Groq

from config import (
    CRISIS_KEYWORDS,
    GROQ_API_KEY,
    GROQ_MODEL_NAME,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
)
from models import LLMAnalysis
from utils import count_crisis_keywords, has_credible_source_hint

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """\
You are a crisis information analyst. Analyze the following message and extract structured information.

MESSAGE:
\"\"\"{message}\"\"\"

Respond ONLY with a valid JSON object (no markdown, no explanation) with these exact keys:

{{
  "crisis_type": "<type of crisis: earthquake, flood, wildfire, bombing, shooting, tornado, hurricane, pandemic, explosion, accident, none, or other>",
  "location": "<geographic location mentioned, or 'Unknown'>",
  "urgency": "<low | medium | high | critical>",
  "source_present": <true if the message cites a credible source like a news agency, government body, or official report; false otherwise>,
  "evidence_present": <true if the message contains verifiable details like specific numbers, dates, named officials, or linked reports; false otherwise>,
  "reasoning": "<brief 1-2 sentence explanation of your assessment>"
}}
"""


def analyze_with_llm(message: str) -> LLMAnalysis:
    """
    Analyze a message using Groq and extract structured features.

    Falls back to keyword-based extraction if the API is unavailable
    or returns an unexpected response.

    Args:
        message: The disaster-related message to analyze.

    Returns:
        LLMAnalysis dataclass with extracted features.
    """
    if not GROQ_API_KEY:
        logger.warning("No Groq API key configured. Using fallback extractor.")
        return _fallback_extract(message)

    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = EXTRACTION_PROMPT.format(message=message)
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=GROQ_MODEL_NAME,
            temperature=LLM_TEMPERATURE,
            max_tokens=LLM_MAX_TOKENS,
            response_format={"type": "json_object"},
        )
        return _parse_llm_response(response.choices[0].message.content)
    except Exception as e:
        logger.error("Groq LLM analysis failed: %s. Using fallback.", e)
        return _fallback_extract(message)


def _parse_llm_response(response_text: str) -> LLMAnalysis:
    try:
        # Strip markdown code fences if present
        cleaned = response_text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

        data = json.loads(cleaned)

        return LLMAnalysis(
            crisis_type=data.get("crisis_type", "Unknown"),
            location=data.get("location", "Unknown"),
            urgency=data.get("urgency", "low").lower(),
            source_present=bool(data.get("source_present", False)),
            evidence_present=bool(data.get("evidence_present", False)),
            raw_reasoning=data.get("reasoning", ""),
        )

    except (json.JSONDecodeError, AttributeError) as e:
        logger.error("Failed to parse LLM response: %s", e)
        return LLMAnalysis(raw_reasoning=f"Parse error: {e}")


def _fallback_extract(message: str) -> LLMAnalysis:
    text_lower = message.lower()

    # ── Crisis type detection ───────────────────────────────────────
    crisis_type = "Unknown"
    crisis_type_map = {
        "earthquake": ["earthquake", "quake", "seismic", "tremor"],
        "flood": ["flood", "flooding", "inundation"],
        "wildfire": ["wildfire", "forest fire", "bushfire"],
        "hurricane": ["hurricane", "typhoon", "cyclone"],
        "tornado": ["tornado", "twister"],
        "tsunami": ["tsunami", "tidal wave"],
        "explosion": ["explosion", "blast", "detonation"],
        "bombing": ["bomb", "bombing", "ied"],
        "shooting": ["shooting", "gunfire", "gunman", "active shooter"],
        "pandemic": ["pandemic", "outbreak", "epidemic", "virus"],
        "accident": ["crash", "derailment", "collision", "accident"],
    }
    for ctype, keywords in crisis_type_map.items():
        if any(kw in text_lower for kw in keywords):
            crisis_type = ctype
            break

    # ── Location extraction (simple pattern) ────────────────────────
    location = "Unknown"
    loc_match = re.search(
        r"(?:in|at|near|from)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)",
        message,
    )
    if loc_match:
        location = loc_match.group(1)

    # ── Urgency estimation ──────────────────────────────────────────
    keyword_count = count_crisis_keywords(text_lower, CRISIS_KEYWORDS)
    urgent_words = ["urgent", "immediately", "critical", "breaking", "emergency"]
    has_urgent = any(w in text_lower for w in urgent_words)

    if has_urgent or keyword_count >= 4:
        urgency = "critical"
    elif keyword_count >= 3:
        urgency = "high"
    elif keyword_count >= 1:
        urgency = "medium"
    else:
        urgency = "low"

    # ── Source & evidence ───────────────────────────────────────────
    source_present = has_credible_source_hint(message)
    evidence_present = bool(re.search(r"\d+\s*(dead|killed|injured|missing)", text_lower))

    return LLMAnalysis(
        crisis_type=crisis_type,
        location=location,
        urgency=urgency,
        source_present=source_present,
        evidence_present=evidence_present,
        raw_reasoning="Fallback keyword-based extraction (LLM unavailable).",
    )

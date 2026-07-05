"""
Shared utility functions for the Crisis Rumor Verification Agent.

Provides text preprocessing, cleaning, and helper functions
used across multiple modules.
"""

import re
import string


def clean_text(text: str) -> str:
    """
    Clean and normalize text for ML processing.

    Steps:
        1. Lowercase
        2. Remove URLs
        3. Remove mentions (@user)
        4. Remove hashtag symbols (keep the word)
        5. Remove punctuation
        6. Collapse whitespace

    Args:
        text: Raw input text.

    Returns:
        Cleaned text string.
    """
    if not text:
        return ""

    text = text.lower()

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", "", text)

    # Remove mentions
    text = re.sub(r"@\w+", "", text)

    # Remove hashtag symbol but keep the word
    text = re.sub(r"#", "", text)

    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def count_crisis_keywords(text: str, keywords: list[str]) -> int:
    """
    Count how many crisis keywords appear in the text.

    Args:
        text: Input text (should be lowercased).
        keywords: List of crisis-related keywords.

    Returns:
        Count of matching keywords.
    """
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to a maximum length, appending '...' if truncated.

    Args:
        text: Input text.
        max_length: Maximum character length.

    Returns:
        Truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


def extract_urls(text: str) -> list[str]:
    """
    Extract all URLs from text.

    Args:
        text: Input text.

    Returns:
        List of URL strings found.
    """
    return re.findall(r"https?://\S+", text)


def has_credible_source_hint(text: str) -> bool:
    """
    Heuristic check for mentions of credible sources.

    Args:
        text: Input text.

    Returns:
        True if a known credible source pattern is found.
    """
    credible_patterns = [
        r"according to",
        r"reported by",
        r"confirmed by",
        r"official\s+(statement|report|source)",
        r"(reuters|ap news|bbc|cnn|nyt|associated press)",
        r"(government|ministry|department|agency)\s+\w+\s+(said|confirmed|reported)",
        r"(police|fire department|fema|red cross)\s+(said|confirmed|reported)",
        r"press (release|conference|briefing)",
    ]
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in credible_patterns)

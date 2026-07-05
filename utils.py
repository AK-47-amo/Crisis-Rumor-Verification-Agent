import re
import string


def clean_text(text: str) -> str:
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
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw in text_lower)


def truncate_text(text: str, max_length: int = 500) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."


def extract_urls(text: str) -> list[str]:
    return re.findall(r"https?://\S+", text)


def has_credible_source_hint(text: str) -> bool:
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

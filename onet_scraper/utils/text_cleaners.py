import json
import logging
from functools import lru_cache
from pathlib import Path

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_cleaning_rules() -> dict[str, list[str]]:
    """
    Loads cleaning rules from resources/cleaning_rules.json.
    Cached explicitly to avoid repeated I/O.
    """
    default_rules = {"scam_phrases": [], "cutoff_markers": []}
    try:
        current_dir = Path(__file__).parent
        # Go up one level to onet_scraper, then to resources
        config_path = current_dir.parent / "resources" / "cleaning_rules.json"

        if not config_path.exists():
            logger.warning(f"Cleaning rules file not found at: {config_path}")
            return default_rules

        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load cleaning rules: {e}")
        return default_rules


def clean_article_content(content_list: list[str] | None) -> str:
    """
    Cleans the raw content list by removing boilerplate, scams, and handling whitespace.
    """
    if not content_list:
        return ""

    full_content = "\n".join(content_list)

    # Normalize text
    clean_content = full_content.replace("\xa0", " ")

    # Load config (cached)
    rules = load_cleaning_rules()

    # Filter out known boilerplates from Config
    scam_phrases = rules.get("scam_phrases", [])

    # Cutoff markers - stop reading if we hit these
    cutoff_markers = rules.get("cutoff_markers", [])

    for marker in cutoff_markers:
        if marker in clean_content:
            clean_content = clean_content.split(marker)[0]

    # Remove other junk lines
    lines = clean_content.split("\n")
    filtered_lines = []
    for line in lines:
        # Skip lines containing scam phrases (double check after split)
        if any(phrase in line for phrase in scam_phrases):
            continue
        # Skip lines that are just whitespace
        if not line.strip():
            continue
        # Skip very short lines that might be artifacts (unless they look like subheaders?)
        if len(line.strip()) < 3:
            continue
        filtered_lines.append(line)

    return "\n".join(filtered_lines).strip()

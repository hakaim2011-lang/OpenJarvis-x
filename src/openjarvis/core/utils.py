from __future__ import annotations
from typing import Iterable, Optional, Any


def _normalize(s: str) -> str:
    return (s or "").strip().lower()


def canonical_assistant_name_from_text(text: str, config: Any) -> Optional[str]:
    """Return the canonical assistant name if any alias appears in *text*.

    - config is expected to have an `.assistant` attribute with `aliases` and
      `canonical_name` fields (as in configs/openjarvis/config.toml).
    - Matching is case-insensitive and looks for alias substrings.
    """
    if not text:
        return None
    low = _normalize(text)
    aliases: Iterable[str] = getattr(getattr(config, "assistant", None), "aliases", []) or []
    canonical = getattr(getattr(config, "assistant", None), "canonical_name", None)
    for a in aliases:
        if _normalize(a) in low:
            return canonical or a
    return None


def is_addressed_to_assistant(text: str, config: Any) -> bool:
    """True when the text appears to address the assistant by any alias."""
    return canonical_assistant_name_from_text(text, config) is not None

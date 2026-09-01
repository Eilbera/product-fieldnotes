#!/usr/bin/env python3
"""Plain-language checks for public PM dossier prose."""
from __future__ import annotations

import re
from typing import Any, Iterable


class ReadabilityError(ValueError):
    """Raised when public prose is too dense or formulaic."""


MAX_SENTENCE_WORDS = 32
MAX_PARAGRAPH_SENTENCES = 3
AI_PHRASES = (
    "pivotal shift",
    "evolving product landscape",
    "at senior-pm altitude",
    "the real question is",
    "not merely",
    "not just",
    "marks a shift",
    "underscores the importance",
)
SKIP_KEYS = {"sources", "source_ids", "url", "id", "image", "cover_image", "video"}


def _sentences(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def _public_strings(value: Any, path: str = "report") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in SKIP_KEYS:
                continue
            yield from _public_strings(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _public_strings(child, f"{path}[{index}]")
    elif isinstance(value, str) and value.strip():
        yield path, value.strip()


def validate_readability(report: dict[str, Any]) -> None:
    """Reject dense sentences, long paragraphs, and common AI-writing phrases."""
    for path, text in _public_strings(report):
        folded = text.casefold()
        for phrase in AI_PHRASES:
            if phrase in folded:
                raise ReadabilityError(f"{path} contains AI-style phrase: {phrase}")
        sentences = _sentences(text)
        if len(sentences) > MAX_PARAGRAPH_SENTENCES:
            raise ReadabilityError(f"{path} has more than 3 sentences in one paragraph")
        for sentence in sentences:
            words = _word_count(sentence)
            if words > MAX_SENTENCE_WORDS:
                raise ReadabilityError(f"{path} has a {words} words sentence; maximum is {MAX_SENTENCE_WORDS}")

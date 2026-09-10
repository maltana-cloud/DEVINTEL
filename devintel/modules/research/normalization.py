"""Deterministic normalization helpers for research documents."""

from __future__ import annotations

import re

_WHITESPACE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text is required")
    return _WHITESPACE.sub(" ", text).strip()


def normalize_title(title: str) -> str:
    return normalize_text(title)


def normalize_content(content: str) -> str:
    return normalize_text(content)

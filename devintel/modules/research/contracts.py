"""Stable contracts for source discovery and research ingestion.

External content is untrusted data. It can never grant DEVINTEL authority,
change policy, or become an execution instruction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
from urllib.parse import urldefrag, urlsplit, urlunsplit


def canonicalize_url(url: str) -> str:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("url is required")
    parts = urlsplit(url.strip())
    scheme = parts.scheme.lower()
    if scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("url must be an absolute HTTP(S) URL")
    host = parts.hostname.lower() if parts.hostname else ""
    if not host:
        raise ValueError("url host is required")
    port = parts.port
    netloc = host
    if port is not None and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        netloc = f"{host}:{port}"
    path = parts.path or "/"
    path = path.rstrip("/") or "/"
    return urldefrag(urlunsplit((scheme, netloc, path, parts.query, "")))[0]


def content_digest(content: str) -> str:
    if not isinstance(content, str) or not content.strip():
        raise ValueError("content is required")
    return sha256(content.strip().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ResearchCandidate:
    url: str
    title: str = ""
    publisher: str = ""
    discovered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "url", canonicalize_url(self.url))


@dataclass(frozen=True)
class ResearchDocument:
    url: str
    title: str
    content: str
    publisher: str = ""
    published_at: datetime | None = None
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    content_hash: str = field(init=False)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "url", canonicalize_url(self.url))
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title is required")
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("content is required")
        object.__setattr__(self, "content_hash", content_digest(self.content))


@dataclass(frozen=True)
class ResearchObservation:
    document_url: str
    kind: str
    value: str
    confidence: float = 0.0
    evidence: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "document_url", canonicalize_url(self.document_url))
        if not isinstance(self.kind, str) or not self.kind.strip():
            raise ValueError("observation kind is required")
        if not isinstance(self.value, str) or not self.value.strip():
            raise ValueError("observation value is required")
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        object.__setattr__(self, "confidence", confidence)

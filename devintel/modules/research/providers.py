"""Free-first source provider primitives."""

from __future__ import annotations

import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from .contracts import ResearchCandidate, ResearchDocument


class StaticProvider:
    """Small deterministic provider useful for tests, bootstrapping, and local feeds."""

    def __init__(self, documents: list[ResearchDocument] | tuple[ResearchDocument, ...]) -> None:
        self._documents = tuple(documents)

    def discover(self, query: str) -> list[ResearchCandidate]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query is required")
        return [ResearchCandidate(d.url, d.title, d.publisher) for d in self._documents]

    def ingest(self, candidate: ResearchCandidate) -> ResearchDocument:
        for document in self._documents:
            if document.url == candidate.url:
                return document
        raise LookupError("candidate is not available")


class RSSProvider:
    """Minimal standard-library RSS/Atom provider; network access is bounded by timeout."""

    def __init__(self, feed_urls: list[str] | tuple[str, ...], *, timeout: float = 10.0) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be positive")
        self.feed_urls = tuple(feed_urls)
        self.timeout = timeout

    def discover(self, query: str) -> list[ResearchCandidate]:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("query is required")
        results: list[ResearchCandidate] = []
        needle = query.casefold()
        for feed_url in self.feed_urls:
            with urllib.request.urlopen(feed_url, timeout=self.timeout) as response:
                root = ET.fromstring(response.read())
            for item in root.findall(".//item"):
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                description = (item.findtext("description") or "").strip()
                if link and (not needle or needle in f"{title} {description}".casefold()):
                    results.append(ResearchCandidate(link, title, metadata={"feed": feed_url}))
            for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry"):
                title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
                link_node = entry.find("{http://www.w3.org/2005/Atom}link")
                link = link_node.attrib.get("href", "").strip() if link_node is not None else ""
                summary = (entry.findtext("{http://www.w3.org/2005/Atom}summary") or "").strip()
                if link and (not needle or needle in f"{title} {summary}".casefold()):
                    results.append(ResearchCandidate(link, title, metadata={"feed": feed_url}))
        return results

    def ingest(self, candidate: ResearchCandidate) -> ResearchDocument:
        with urllib.request.urlopen(candidate.url, timeout=self.timeout) as response:
            raw = response.read()
            content_type = response.headers.get("Content-Type", "")
        text = raw.decode("utf-8", errors="replace")
        return ResearchDocument(
            candidate.url,
            candidate.title or candidate.url,
            text,
            publisher=candidate.publisher,
            retrieved_at=datetime.now(timezone.utc),
            metadata={"content_type": content_type, **candidate.metadata},
        )

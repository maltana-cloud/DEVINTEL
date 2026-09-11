"""Thread-safe opportunity and revenue persistence boundary."""
from __future__ import annotations

import threading
from typing import Protocol

from .contracts import BusinessOpportunity, ProductOffer, RevenueRecord


class BusinessStore(Protocol):
    def add_opportunity(self, item: BusinessOpportunity) -> None: ...
    def opportunities(self) -> list[BusinessOpportunity]: ...
    def add_offer(self, item: ProductOffer) -> None: ...
    def offers(self) -> list[ProductOffer]: ...
    def add_revenue(self, item: RevenueRecord) -> None: ...
    def revenue(self) -> list[RevenueRecord]: ...


class InMemoryBusinessStore:
    def __init__(self, max_items: int = 1000) -> None:
        if max_items < 1:
            raise ValueError("max_items must be positive")
        self._max = max_items
        self._opportunities: list[BusinessOpportunity] = []
        self._offers: list[ProductOffer] = []
        self._revenue: dict[str, RevenueRecord] = {}
        self._lock = threading.RLock()

    def add_opportunity(self, item: BusinessOpportunity) -> None:
        with self._lock:
            self._opportunities.append(item)
            self._opportunities = self._opportunities[-self._max :]

    def opportunities(self) -> list[BusinessOpportunity]:
        with self._lock:
            return list(self._opportunities)

    def add_offer(self, item: ProductOffer) -> None:
        with self._lock:
            self._offers.append(item)
            self._offers = self._offers[-self._max :]

    def offers(self) -> list[ProductOffer]:
        with self._lock:
            return list(self._offers)

    def add_revenue(self, item: RevenueRecord) -> None:
        with self._lock:
            self._revenue[item.transaction_id] = item

    def revenue(self) -> list[RevenueRecord]:
        with self._lock:
            return list(self._revenue.values())

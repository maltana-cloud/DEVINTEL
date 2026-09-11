"""Provider-independent payment boundary.

No provider is mandatory. Credentials belong outside source control and are
supplied only to a configured adapter at runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .contracts import ProductOffer, RevenueStatus


@dataclass(frozen=True)
class PaymentIntent:
    intent_id: str
    offer: ProductOffer
    checkout_reference: str


@dataclass(frozen=True)
class PaymentResult:
    transaction_id: str
    status: RevenueStatus
    amount_minor: int
    currency: str
    provider: str


class PaymentProvider(Protocol):
    name: str

    def create_checkout(self, offer: ProductOffer) -> PaymentIntent: ...
    def verify(self, checkout_reference: str) -> PaymentResult: ...


class NoPaymentProvider:
    name = "none"

    def create_checkout(self, offer: ProductOffer) -> PaymentIntent:
        raise RuntimeError("no payment provider configured")

    def verify(self, checkout_reference: str) -> PaymentResult:
        raise RuntimeError("no payment provider configured")

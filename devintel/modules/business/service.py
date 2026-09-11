"""Business intelligence orchestration."""
from __future__ import annotations

from .contracts import BusinessOpportunity, ProductOffer, RevenueRecord
from .policy import CommercialPolicy
from .providers import NoPaymentProvider, PaymentProvider
from .store import BusinessStore, InMemoryBusinessStore


class BusinessService:
    def __init__(self, store: BusinessStore | None = None, payment: PaymentProvider | None = None, policy: CommercialPolicy | None = None) -> None:
        self.store = store or InMemoryBusinessStore()
        self.payment = payment or NoPaymentProvider()
        self.policy = policy or CommercialPolicy()

    def discover(self, opportunity: BusinessOpportunity) -> bool:
        if not self.policy.opportunity_allowed(opportunity):
            return False
        self.store.add_opportunity(opportunity)
        return True

    def ranked_opportunities(self) -> list[BusinessOpportunity]:
        return self.policy.recommend(self.store.opportunities())

    def create_offer(self, offer: ProductOffer) -> None:
        if offer.price_minor > 0 and not offer.provider:
            # Provider is optional at the model layer; checkout still fails
            # closed until a real, configured provider is injected.
            pass
        self.store.add_offer(offer)

    def checkout(self, offer: ProductOffer):
        return self.payment.create_checkout(offer)

    def record_verified_revenue(self, record: RevenueRecord) -> None:
        self.store.add_revenue(record)

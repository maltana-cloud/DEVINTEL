"""Growth intelligence orchestration."""
from dataclasses import dataclass
from typing import Callable, Sequence
from .contracts import AudienceSignal, AwarenessAction, AwarenessPlan, GrowthOpportunity
from .policy import GrowthPolicy
from .store import GrowthStore, InMemoryGrowthStore

@dataclass(frozen=True)
class GrowthRun:
    discovered: int
    accepted: int
    opportunities: int
    plans: tuple[AwarenessPlan, ...]

class GrowthEngine:
    def __init__(self, store: GrowthStore | None = None, policy: GrowthPolicy | None = None, event_sink: Callable[[str, dict], None] | None = None) -> None:
        self.store = store or InMemoryGrowthStore(); self.policy = policy or GrowthPolicy(); self.event_sink = event_sink
    def _emit(self, name: str, data: dict) -> None:
        if self.event_sink:
            try: self.event_sink(name, data)
            except Exception: pass
    def evaluate(self, signal: AudienceSignal, destinations: Sequence[str] = ()) -> GrowthOpportunity:
        score = self.policy.score(signal); action = self.policy.choose(signal, score)
        opp = GrowthOpportunity(signal.signal_id, signal.scope_id, signal.summary, signal.summary, score, action, signal.evidence_urls, signal.metadata)
        self.store.add_signal(signal); self.store.add_opportunity(opp)
        self._emit("growth.opportunity", {"id": opp.opportunity_id, "scope_id": opp.scope_id, "action": action.value, "score": score.value})
        return opp
    def plan(self, opportunity: GrowthOpportunity, destinations: Sequence[str]) -> AwarenessPlan:
        # Destinations are suggestions only; actual publishing remains System 5's policy/permission decision.
        if opportunity.action is AwarenessAction.NO_ACTION: return AwarenessPlan(opportunity.opportunity_id, AwarenessAction.NO_ACTION)
        safe = tuple(str(x).strip() for x in destinations if str(x).strip())
        return AwarenessPlan(opportunity.opportunity_id, opportunity.action, safe, "Useful, evidence-backed awareness; distribution remains permission-controlled.")
    def run(self, scope_id: str, signals: Sequence[AudienceSignal], destination_selector: Callable[[AudienceSignal], Sequence[str]] | None = None) -> GrowthRun:
        accepted = 0; plans = []; opportunities = 0
        for signal in signals:
            if signal.scope_id != scope_id: continue
            accepted += 1; opp = self.evaluate(signal); opportunities += 1
            destinations = destination_selector(signal) if destination_selector else ()
            plans.append(self.plan(opp, destinations))
        return GrowthRun(len(signals), accepted, opportunities, tuple(plans))

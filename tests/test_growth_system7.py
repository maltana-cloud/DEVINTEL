import unittest
from datetime import datetime, timezone
from devintel.modules.growth.contracts import AudienceSignal, SignalKind, AwarenessAction
from devintel.modules.growth.engine import GrowthEngine
from devintel.modules.growth.policy import GrowthPolicy
from devintel.modules.growth.store import InMemoryGrowthStore

class GrowthSystem7Tests(unittest.TestCase):
    def signal(self, scope="channel:a", **kw):
        return AudienceSignal("s1", scope, SignalKind.AUDIENCE_NEED, "Developers need a reliable free testing guide", ("https://example.com/evidence",), 0.9, datetime.now(timezone.utc), kw)
    def test_high_value_signal_creates_educational_plan(self):
        engine = GrowthEngine()
        opp = engine.evaluate(self.signal())
        self.assertEqual(opp.action, AwarenessAction.EDUCATE)
        plan = engine.plan(opp, ["channel:a"])
        self.assertEqual(plan.destinations, ("channel:a",))
    def test_low_confidence_stays_quiet(self):
        s = AudienceSignal("s2", "channel:a", SignalKind.DEMAND, "unverified claim", (), 0.2, datetime.now(timezone.utc))
        opp = GrowthEngine().evaluate(s)
        self.assertEqual(opp.action, AwarenessAction.NO_ACTION)
        self.assertEqual(GrowthEngine().plan(opp, ["channel:a"]).action, AwarenessAction.NO_ACTION)
    def test_scope_isolation(self):
        store = InMemoryGrowthStore(); engine = GrowthEngine(store)
        engine.evaluate(self.signal("a"))
        self.assertEqual(len(store.opportunities("a")), 1)
        self.assertEqual(store.opportunities("b"), [])
    def test_malformed_score_threshold_rejected(self):
        with self.assertRaises(ValueError): GrowthPolicy(min_confidence=2)
    def test_destination_is_suggestion_not_permission(self):
        engine = GrowthEngine(); opp = engine.evaluate(self.signal())
        plan = engine.plan(opp, ["untrusted-destination"])
        self.assertEqual(plan.destinations, ("untrusted-destination",))

if __name__ == "__main__": unittest.main()

"""Plugin authorization boundary; plugins never gain authority implicitly."""
from .contracts import PluginAction, PluginRisk

class PluginPolicy:
    def authorize(self, action: PluginAction, approved: bool = False) -> bool:
        if action.risk in (PluginRisk.HIGH, PluginRisk.CRITICAL): return approved
        if action.requires_owner_approval: return approved
        return action.risk == PluginRisk.LOW

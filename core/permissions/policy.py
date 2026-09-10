"""Central permission policy: intelligence may propose, policy decides authority."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from core.contracts import ActionRisk


class Capability(str, Enum):
    READ_PUBLIC_DATA = "read_public_data"
    RESEARCH = "research"
    CONVERSE = "converse"
    PUBLISH = "publish"
    COMMUNITY_PARTICIPATE = "community_participate"
    BUILD_TOOL = "build_tool"
    DEPLOY_TOOL = "deploy_tool"
    CONNECT_ACCOUNT = "connect_account"
    SPEND_MONEY = "spend_money"
    CHANGE_CORE = "change_core"


@dataclass(frozen=True)
class Policy:
    """Default fail-closed authority map for DEVINTEL."""

    levels: dict[Capability, ActionRisk]

    @classmethod
    def default(cls) -> "Policy":
        return cls(
            levels={
                Capability.READ_PUBLIC_DATA: ActionRisk.AUTOMATIC,
                Capability.RESEARCH: ActionRisk.AUTOMATIC,
                Capability.CONVERSE: ActionRisk.AUTOMATIC,
                Capability.PUBLISH: ActionRisk.SAFEGUARDED,
                Capability.COMMUNITY_PARTICIPATE: ActionRisk.SAFEGUARDED,
                Capability.BUILD_TOOL: ActionRisk.SAFEGUARDED,
                Capability.DEPLOY_TOOL: ActionRisk.SAFEGUARDED,
                Capability.CONNECT_ACCOUNT: ActionRisk.OWNER_APPROVAL,
                Capability.SPEND_MONEY: ActionRisk.OWNER_APPROVAL,
                Capability.CHANGE_CORE: ActionRisk.OWNER_APPROVAL,
            }
        )

    def risk_for(self, capability: Capability) -> ActionRisk:
        """Unknown capabilities fail closed rather than gaining authority."""
        return self.levels.get(capability, ActionRisk.OWNER_APPROVAL)

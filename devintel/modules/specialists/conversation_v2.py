"""Scoped conversation intelligence specialist behind the plugin boundary."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from ..plugins.contracts import PluginAction, PluginManifest, PluginRisk
from ..plugins.service import PluginService

@dataclass(frozen=True)
class ConversationResult:
    scope_id: str
    message: str
    response: str

class ConversationResponder(Protocol):
    def respond(self, message: str, scope_id: str) -> str: ...

class ConversationSpecialist:
    plugin_id = "specialist.conversation"
    def __init__(self, plugins: PluginService | None = None) -> None:
        self.plugins = plugins or PluginService()
        self.plugins.register(PluginManifest(
            plugin_id=self.plugin_id, name="Conversation Specialist", version="1.0.0",
            description="Produces scoped natural-language responses without granting authority.",
            capabilities=("conversation.respond",), required_permissions=("conversation.read",),
            risk=PluginRisk.LOW,
        ))
        self.attach()

    def execute(self, scope_id: str, message: str, responder: ConversationResponder) -> ConversationResult:
        scope = scope_id.strip() if isinstance(scope_id, str) else ""
        text = message.strip() if isinstance(message, str) else ""
        if not scope: raise ValueError("scope_id is required")
        if not text: raise ValueError("message is required")
        if not hasattr(responder, "respond"): raise TypeError("responder must implement respond")
        action = PluginAction(self.plugin_id, "conversation.respond", scope, PluginRisk.LOW,
                              "bounded conversation response", payload={"message": text, "responder": responder})
        result = self.plugins.execute(action)
        if not result.success: raise RuntimeError(result.error)
        return ConversationResult(scope, text, result.output)

    def attach(self) -> None:
        def run(action: PluginAction) -> str:
            payload = action.payload
            if not isinstance(payload, dict): raise TypeError("conversation action payload must be a mapping")
            message, responder = payload.get("message"), payload.get("responder")
            if not isinstance(message, str) or not message.strip(): raise ValueError("conversation message is required")
            if not hasattr(responder, "respond"): raise TypeError("conversation responder is invalid")
            response = responder.respond(message.strip(), action.scope_id)
            if not isinstance(response, str): raise TypeError("responder must return a string")
            return response
        self.plugins.attach(self.plugin_id, run)

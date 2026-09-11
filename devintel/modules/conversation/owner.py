"""Owner communication hooks; they do not grant themselves execution authority."""
from __future__ import annotations

from .contracts import ConversationMessage, ConversationScope
from .service import ConversationService, Responder


class OwnerCommunication:
    """Dedicated owner scope kept separate from community/channel memory."""

    def __init__(self, service: ConversationService, owner_id: str) -> None:
        if not owner_id.strip():
            raise ValueError("owner_id is required")
        self.service = service
        self.owner_id = owner_id

    @property
    def scope(self) -> ConversationScope:
        return ConversationScope.OWNER

    def receive(self, text: str, responder: Responder, *, session_id: str = "owner"):
        message = ConversationMessage(
            scope_id=f"owner:{self.owner_id}:{session_id}",
            scope=ConversationScope.OWNER,
            sender_id=self.owner_id,
            text=text,
        )
        return self.service.receive(message, responder)

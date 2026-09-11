from devintel.modules.specialists.conversation_v2 import ConversationSpecialist

class Responder:
    def respond(self, message, scope_id):
        return f"{scope_id}: {message}"

def test_conversation_specialist_is_scoped():
    result = ConversationSpecialist().execute("group:1", "hello", Responder())
    assert result.scope_id == "group:1"
    assert result.response == "group:1: hello"

def test_conversation_specialist_rejects_invalid_inputs():
    specialist = ConversationSpecialist()
    for scope, message in (("", "hello"), ("scope", "")):
        try:
            specialist.execute(scope, message, Responder())
            assert False
        except ValueError:
            pass
    try:
        specialist.execute("scope", "hello", object())
        assert False
    except TypeError:
        pass

def test_conversation_failure_is_isolated():
    class Broken:
        def respond(self, message, scope_id):
            raise RuntimeError("provider down")
    try:
        ConversationSpecialist().execute("scope", "hello", Broken())
        assert False
    except RuntimeError as exc:
        assert "isolated" in str(exc).lower()

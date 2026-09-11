from devintel.modules.specialists.tool_builder import ToolBuilderSpecialist
from devintel.modules.tool_builder.contracts import BuildRequest, ToolSpec

class Source:
    def discover_tools(self, problem):
        return [BuildRequest(ToolSpec("safe-tool", problem, risk="low"), "x = 1")]

def test_tool_builder_specialist_builds_low_risk_tool():
    result = ToolBuilderSpecialist().execute("scope", "missing tool", Source())
    assert result.scope_id == "scope"
    assert len(result.artifacts) == 1
    artifact, sandbox, deployment = result.artifacts[0]
    assert artifact.tool.name == "safe-tool"
    assert sandbox.success is True
    assert deployment is None

def test_tool_builder_specialist_rejects_invalid_scope():
    try:
        ToolBuilderSpecialist().execute("", "x", Source())
    except ValueError as exc:
        assert "scope_id" in str(exc)
    else:
        raise AssertionError("expected ValueError")

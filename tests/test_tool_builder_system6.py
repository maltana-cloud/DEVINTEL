import pytest
from devintel.modules.tool_builder import ToolSpec, ToolRequest, BuildRequest, ToolState, ToolBuilderService, LocalSandbox
from devintel.modules.tool_builder.lifecycle import HealthRecord, LifecycleManager

def test_contracts_and_safe_build():
    svc=ToolBuilderService(); spec=ToolSpec("hello","safe helper")
    artifact,result,deploy=svc.build(BuildRequest(spec,"x = 1\ny = x + 1"))
    assert artifact.source_digest and result.success and deploy is None
    assert svc.registry.get("hello","0.1.0")[1] == ToolState.READY

def test_sandbox_rejects_import_and_dynamic_calls():
    sb=LocalSandbox()
    assert not sb.run("import os").success
    assert not sb.run("print('x')").success
    assert not sb.run("eval('1+1')").success

def test_invalid_and_unauthorized_are_fail_closed():
    with pytest.raises(ValueError): ToolSpec("","missing")
    spec=ToolSpec("risky","x",risk="high")
    svc=ToolBuilderService(permission_check=lambda _: False)
    with pytest.raises(PermissionError): svc.build(BuildRequest(spec,"x=1"))
    assert svc.registry.get("risky","0.1.0")[1] == ToolState.FAILED

def test_solution_discovery_is_reusable_boundary():
    class D:
        def find(self,problem): return ("existing-tool",)
    svc=ToolBuilderService(discovery=D())
    assert svc.discover(ToolRequest("parse a file")) == ("existing-tool",)

def test_deployment_is_safe_without_provider():
    spec=ToolSpec("x","x")
    _,result,deployment=ToolBuilderService().build(BuildRequest(spec,"x=1"),deploy=True)
    assert result.success and deployment is not None and not deployment.success
    assert "no deployment provider" in deployment.message

def test_health_lifecycle():
    mgr=LifecycleManager(); rec=HealthRecord("x","1.0.0",True,"ok")
    mgr.record_health(rec); assert mgr.health("x","1.0.0").healthy

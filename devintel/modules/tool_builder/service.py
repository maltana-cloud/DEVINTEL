"""System 6 orchestration with fail-closed permissions and isolated lifecycle."""
from .builder import Builder, SolutionDiscovery
from .contracts import BuildRequest, ToolRequest, ToolState
from .deployment import Deployer
from .registry import ToolRegistry
from .sandbox import LocalSandbox

class ToolBuilderService:
    def __init__(self, registry=None, builder=None, discovery=None, sandbox=None, deployer=None, permission_check=None, event_sink=None, audit_sink=None):
        self.registry=registry or ToolRegistry(); self.builder=builder or Builder(); self.discovery=discovery or SolutionDiscovery()
        self.sandbox=sandbox or LocalSandbox(); self.deployer=deployer or Deployer(); self.permission_check=permission_check or (lambda spec: spec.risk=="low")
        self.event_sink=event_sink; self.audit_sink=audit_sink
    def _record(self,event,**data):
        payload={"event":event,**data}
        if self.event_sink: self.event_sink(event,payload)
        if self.audit_sink: self.audit_sink(payload)
    def discover(self, request:ToolRequest):
        found=tuple(self.discovery.find(request.problem) or ()); self._record("tool.discovery",problem=request.problem,count=len(found)); return found
    def build(self, request:BuildRequest, deploy=False):
        spec=request.spec; self.registry.register(spec,ToolState.SPECIFIED); self.registry.set_state(spec.name,spec.version,ToolState.BUILDING); self._record("tool.build.requested",name=spec.name,version=spec.version)
        try:
            if not self.permission_check(spec): raise PermissionError("tool action is not authorized")
            artifact=self.builder.build(request); self.registry.set_state(spec.name,spec.version,ToolState.TESTING)
            result=self.sandbox.run(artifact.source,request.entrypoint)
            if not result.success:
                self.registry.set_state(spec.name,spec.version,ToolState.FAILED); self._record("tool.test.failed",name=spec.name,version=spec.version); return artifact,result,None
            self.registry.set_state(spec.name,spec.version,ToolState.READY); self._record("tool.test.passed",name=spec.name,version=spec.version)
            deployment=None
            if deploy:
                deployment=self.deployer.deploy(artifact); self.registry.set_state(spec.name,spec.version,ToolState.DEPLOYED if deployment.success else ToolState.FAILED)
                self._record("tool.deployment",name=spec.name,version=spec.version,success=deployment.success)
            return artifact,result,deployment
        except Exception as exc:
            self.registry.set_state(spec.name,spec.version,ToolState.FAILED); self._record("tool.build.failed",name=spec.name,version=spec.version,error=type(exc).__name__); raise

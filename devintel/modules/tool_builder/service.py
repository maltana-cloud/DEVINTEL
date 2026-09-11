"""System 6 orchestration with fail-closed permissions and isolated lifecycle."""
from .builder import Builder, SolutionDiscovery
from .contracts import BuildRequest, ToolRequest, ToolState
from .deployment import Deployer
from .registry import ToolRegistry
from .sandbox import LocalSandbox

class ToolBuilderService:
    def __init__(self, registry=None, builder=None, discovery=None, sandbox=None, deployer=None, permission_check=None):
        self.registry=registry or ToolRegistry(); self.builder=builder or Builder(); self.discovery=discovery or SolutionDiscovery()
        self.sandbox=sandbox or LocalSandbox(); self.deployer=deployer or Deployer(); self.permission_check=permission_check or (lambda spec: spec.risk=="low")
    def discover(self, request:ToolRequest): return tuple(self.discovery.find(request.problem) or ())
    def build(self, request:BuildRequest, deploy=False):
        spec=request.spec; self.registry.register(spec,ToolState.SPECIFIED); self.registry.set_state(spec.name,spec.version,ToolState.BUILDING)
        try:
            if not self.permission_check(spec): raise PermissionError("tool action is not authorized")
            artifact=self.builder.build(request); self.registry.set_state(spec.name,spec.version,ToolState.TESTING)
            result=self.sandbox.run(artifact.source,request.entrypoint)
            if not result.success:
                self.registry.set_state(spec.name,spec.version,ToolState.FAILED); return artifact,result,None
            self.registry.set_state(spec.name,spec.version,ToolState.READY)
            deployment=None
            if deploy:
                deployment=self.deployer.deploy(artifact)
                self.registry.set_state(spec.name,spec.version,ToolState.DEPLOYED if deployment.success else ToolState.FAILED)
            return artifact,result,deployment
        except Exception:
            self.registry.set_state(spec.name,spec.version,ToolState.FAILED); raise

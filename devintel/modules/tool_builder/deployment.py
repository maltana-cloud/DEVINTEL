"""Provider-independent deployment, rollback, and lifecycle boundary."""
from .contracts import DeploymentResult, ToolArtifact

class Deployer:
    def deploy(self, artifact:ToolArtifact)->DeploymentResult:
        return DeploymentResult(False,artifact.tool.name,artifact.tool.version,"no deployment provider configured")
    def rollback(self,name:str,version:str)->DeploymentResult:
        return DeploymentResult(False,name,version,"no deployment provider configured")

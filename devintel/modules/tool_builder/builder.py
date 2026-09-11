"""Replaceable tool-building provider interfaces."""
from hashlib import sha256
from .contracts import BuildRequest, ToolArtifact

class Builder:
    def build(self, request:BuildRequest)->ToolArtifact:
        return ToolArtifact(request.spec,sha256(request.source.encode()).hexdigest(),request.source)

class SolutionDiscovery:
    def find(self, problem:str):
        """Return known reusable solutions. Empty by default; providers may be injected."""
        return ()

"""Controlled execution boundary. This intentionally supports a tiny Python subset only."""
from dataclasses import dataclass
import ast
from .contracts import BuildRequest, SandboxResult

class Sandbox:
    def run(self, source:str, entrypoint:str="", timeout:float=2.0)->SandboxResult: raise NotImplementedError

@dataclass
class LocalSandbox(Sandbox):
    """Static, non-host-executing sandbox suitable for validation in the core.

    It parses source and rejects imports, attribute access, filesystem/network primitives,
    eval/exec and other dynamic execution. It never executes generated code.
    """
    def run(self, source, entrypoint="", timeout=2.0):
        if timeout<=0: return SandboxResult(False,error="timeout must be positive")
        try: tree=ast.parse(source,mode="exec")
        except SyntaxError as exc: return SandboxResult(False,error=f"syntax error: {exc}")
        blocked=(ast.Import,ast.ImportFrom,ast.Attribute,ast.Call)
        for node in ast.walk(tree):
            if isinstance(node,blocked):
                return SandboxResult(False,error=f"unsafe construct: {type(node).__name__}")
            if isinstance(node,ast.Name) and node.id in {"eval","exec","open","__import__","compile","input"}:
                return SandboxResult(False,error=f"unsafe name: {node.id}")
        return SandboxResult(True,output="static validation passed",exit_code=0)

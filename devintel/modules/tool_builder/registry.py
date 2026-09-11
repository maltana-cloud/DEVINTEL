"""Thread-safe, version-aware tool registry."""
from threading import RLock
from .contracts import ToolSpec, ToolState

class ToolRegistry:
    def __init__(self): self._items={}; self._lock=RLock()
    def register(self, spec:ToolSpec, state:ToolState=ToolState.DISCOVERED)->None:
        with self._lock:
            key=(spec.name,spec.version)
            if key in self._items: raise ValueError(f"tool version already registered: {spec.name}@{spec.version}")
            self._items[key]=(spec,state)
    def get(self,name,version=None):
        with self._lock:
            if version is not None:
                item=self._items.get((name,version)); return item
            matches=[v for (n,v),item in self._items.items() if n==name]
            return self._items[(name,max(matches))] if matches else None
    def set_state(self,name,version,state):
        with self._lock:
            key=(name,version)
            if key not in self._items: raise KeyError(key)
            spec,_=self._items[key]; self._items[key]=(spec,state)
    def list(self):
        with self._lock: return tuple(self._items.values())

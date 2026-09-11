"""Version lifecycle and health records without automatic destructive updates."""
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock

@dataclass(frozen=True)
class HealthRecord:
    name:str; version:str; healthy:bool; message:str=""; checked_at:datetime=datetime.now(timezone.utc)

class LifecycleManager:
    def __init__(self): self._health={}; self._lock=RLock()
    def record_health(self,record:HealthRecord):
        with self._lock: self._health[(record.name,record.version)]=record
    def health(self,name,version):
        with self._lock: return self._health.get((name,version))
    def all_health(self):
        with self._lock: return tuple(self._health.values())

"""Task primitives and bounded task execution for DEVINTEL."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from threading import RLock
from typing import Any, Callable
from uuid import uuid4


class TaskState(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class Task:
    name: str
    action: Callable[[], Any]
    id: str = field(default_factory=lambda: uuid4().hex)
    state: TaskState = TaskState.PENDING
    result: Any = None
    error: str | None = None


class TaskEngine:
    """Executes explicit tasks while preserving state and failure boundaries."""

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}
        self._lock = RLock()

    def submit(self, task: Task) -> str:
        if not task.name or not callable(task.action):
            raise ValueError("task name and callable action are required")
        with self._lock:
            self._tasks[task.id] = task
        return task.id

    def run(self, task_id: str) -> Task:
        with self._lock:
            task = self._tasks[task_id]
            if task.state is not TaskState.PENDING:
                return task
            task.state = TaskState.RUNNING
        try:
            result = task.action()
        except Exception as exc:
            with self._lock:
                task.error = f"{type(exc).__name__}: {exc}"
                task.state = TaskState.FAILED
        else:
            with self._lock:
                task.result = result
                task.state = TaskState.SUCCEEDED
        return task

    def get(self, task_id: str) -> Task:
        with self._lock:
            return self._tasks[task_id]

    def pending(self) -> tuple[Task, ...]:
        with self._lock:
            return tuple(t for t in self._tasks.values() if t.state is TaskState.PENDING)

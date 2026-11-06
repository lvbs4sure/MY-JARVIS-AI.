"""Local, side-effect-free conversation job coordinator.

No provider calls, database writes or network access. Adapters must check
accept_result() before displaying or persisting asynchronous responses.
"""
from dataclasses import dataclass
from enum import Enum
from uuid import uuid4


class JobState(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class Job:
    job_id: str
    provider: str
    state: JobState


class JobCoordinator:
    """At most one active conversation job per UI session.

    New jobs invalidate older responses. A cloud route must be explicitly
    authorized for each job; fallback never changes the route implicitly.
    """

    def __init__(self):
        self._current = None

    @property
    def current(self):
        return self._current

    def start(self, provider, *, cloud_allowed=False):
        if provider not in ("ollama", "gemini"):
            raise ValueError("Unsupported provider route.")
        if provider == "gemini" and not cloud_allowed:
            raise PermissionError("Cloud conversation requires explicit permission.")
        if self._current is not None and self._current.state == JobState.ACTIVE:
            self._current = Job(self._current.job_id, self._current.provider, JobState.CANCELLED)
        job = Job(uuid4().hex, provider, JobState.ACTIVE)
        self._current = job
        return job

    def accept_result(self, job_id):
        return bool(
            self._current
            and self._current.job_id == job_id
            and self._current.state == JobState.ACTIVE
        )

    def finish(self, job_id, *, failed=False):
        if not self.accept_result(job_id):
            return False
        self._current = Job(
            job_id,
            self._current.provider,
            JobState.FAILED if failed else JobState.COMPLETED,
        )
        return True

    def cancel(self, job_id=None):
        if self._current is None or self._current.state != JobState.ACTIVE:
            return False
        if job_id is not None and job_id != self._current.job_id:
            return False
        self._current = Job(self._current.job_id, self._current.provider, JobState.CANCELLED)
        return True

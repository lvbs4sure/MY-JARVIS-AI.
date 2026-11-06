"""Session-owned, bounded background work. Workers never access Streamlit state."""
from dataclasses import dataclass
from threading import BoundedSemaphore, Event, Lock, Thread

_CAPACITY = BoundedSemaphore(2)


@dataclass(frozen=True)
class JobFailure:
    message: str = "The request could not complete. Retry manually."


class RequestJob:
    def __init__(self, kind, operation, metadata=None):
        if not _CAPACITY.acquire(blocking=False):
            raise RuntimeError("Another request is still finishing. Please wait.")
        self.kind = kind
        self.metadata = dict(metadata or {})
        self.cancel_event = Event()
        self.finished = Event()
        self._lock = Lock()
        self._result = None
        self._consumed = False
        self._thread = Thread(target=self._run, args=(operation,), daemon=True, name="jarvis-request")
        try:
            self._thread.start()
        except BaseException:
            _CAPACITY.release()
            raise

    def _run(self, operation):
        try:
            result = None if self.cancel_event.is_set() else operation(self.cancel_event)
            with self._lock:
                if not self.cancel_event.is_set():
                    self._result = result
        except Exception:
            with self._lock:
                if not self.cancel_event.is_set():
                    self._result = JobFailure()
        finally:
            _CAPACITY.release()
            self.finished.set()

    def cancel(self):
        with self._lock:
            if self.cancel_event.is_set() or self._consumed:
                return False
            self.cancel_event.set()
            self._result = None
            return True

    def take_result(self):
        if not self.finished.is_set():
            raise RuntimeError("Request has not finished.")
        with self._lock:
            if self._consumed or self.cancel_event.is_set():
                return None
            self._consumed = True
            result, self._result = self._result, None
            return result

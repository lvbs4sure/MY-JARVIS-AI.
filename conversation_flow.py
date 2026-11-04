"""Main-thread completion handling for session-owned conversation requests."""
from activity_log import record_activity
from reply_status import ReplyResult
from request_jobs import JobFailure


def finish_request(state):
    job = state.get("request_job")
    if job is None or not job.finished.is_set():
        return False
    state.pop("request_job", None)
    result = job.take_result()
    if job.cancel_event.is_set():
        index = job.metadata.get("user_index")
        if isinstance(index, int) and 0 <= index < len(state["chat"]):
            state["chat"][index]["cancelled"] = True
        state["assistant_state"] = "ready"
        state["last_request"] = "Interrupted. Late results are discarded; already-sent requests cannot be recalled."
        record_activity(state, "Voice request" if job.kind == "voice" else "AI request", "interrupted")
        return True
    if job.kind == "voice":
        text, error = (None, result.message) if isinstance(result, JobFailure) else result
        if error or not text or not text.strip():
            state["voice_error"] = error or "No speech recognized. Please record again."
            state["voice_digest"] = None
            state["assistant_state"] = "error"
            record_activity(state, "Voice transcription", "failed")
        else:
            state["pending_spoken"] = text.strip()
            state["spoken_route"] = job.metadata
            state["assistant_state"] = "ready"
            state.pop("voice_error", None)
            record_activity(state, "Voice transcribed")
        return True
    if isinstance(result, JobFailure) or not isinstance(result, ReplyResult):
        result = ReplyResult("The request could not complete. Retry manually.", False, job.metadata["provider"], "unexpected", True)
    state["chat"].append({"role":"assistant", "content":result.text, "ok":result.ok,
        "retryable":result.retryable, "request_provider":job.metadata["provider"],
        "request_model":job.metadata.get("local_model")})
    state["last_request"] = f"{result.provider.upper()} · {result.latency_ms} ms · {result.kind}"
    state["assistant_state"] = "ready" if result.ok else "error"
    record_activity(state, "AI reply", "received" if result.ok else "failed")
    return True

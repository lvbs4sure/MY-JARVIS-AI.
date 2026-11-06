"""Credential-free request outcomes, independent of UI wording."""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ReplyResult:
    text: str
    ok: bool
    provider: str
    kind: str = "ok"
    retryable: bool = False
    http_status: int | None = None
    latency_ms: int = 0


def legacy_result(text, provider="gemini"):
    """Compatibility for existing string-returning integrations, not model output."""
    if not isinstance(text, str):
        return ReplyResult("The provider returned an invalid response.", False, provider, "unexpected")
    prefixes = {
        "Gemini is temporarily unavailable": ("service", True),
        "Gemini rate limit": ("rate_limit", True),
        "Gemini access denied": ("access", False),
        "Gemini model unavailable": ("model", False),
        "Gemini API error": ("configuration", False),
        "Gemini connection error": ("network", True),
        "Gemini returned an empty response": ("empty", True),
        "Gemini mode needs": ("configuration", False),
        "Invalid JARVIS_PROVIDER": ("configuration", False),
        "Local AI paused": ("local_capacity", False),
        "Local Ollama unavailable": ("local_unavailable", True),
        "Local model returned an empty response": ("empty", True),
        "For safety,": ("configuration", False),
    }
    for prefix, (kind, retryable) in prefixes.items():
        if text.startswith(prefix):
            match = re.search(r"HTTP (\d{3})", text)
            code = int(match.group(1)) if match else None
            if code in (408, 500, 502, 503, 504):
                kind, retryable = "service", True
            return ReplyResult(text, False, provider, kind, retryable, code)
    return ReplyResult(text, True, provider)

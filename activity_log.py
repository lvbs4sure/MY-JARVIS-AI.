"""Bounded, in-session action history; never stores prompts, notes or secrets."""
from datetime import datetime


def record_activity(state, action, outcome="done"):
    entry = {"time": datetime.now().astimezone().strftime("%H:%M:%S"), "action": action, "outcome": outcome}
    state["activity"] = (state.get("activity", []) + [entry])[-30:]


def reply_failed(reply):
    return reply.startswith(("Gemini connection error", "Gemini API error", "Gemini mode needs", "Gemini returned an empty response", "Invalid JARVIS_PROVIDER", "Local Ollama unavailable", "Gemini is temporarily unavailable.", "Local model returned an empty response", "For safety,"))

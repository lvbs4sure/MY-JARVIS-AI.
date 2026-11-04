"""Read-only dashboard capability diagnostics. No network calls or secrets exposed."""
import os


def dashboard_readiness(provider=None, environ=None, *, free_ram_bytes=None, local_models=None):
    env = os.environ if environ is None else environ
    route = (provider or env.get("JARVIS_PROVIDER", "ollama")).strip().lower()
    result = {}
    if route == "gemini":
        configured = bool(env.get("GEMINI_API_KEY", "").strip())
        result["chat"] = ("configured" if configured else "blocked",
                          "Gemini key configured; connection not yet tested." if configured else
                          "Missing GEMINI_API_KEY. Set it in your private .env file.")
    elif route == "ollama":
        if free_ram_bytes is not None and free_ram_bytes < 2 * 2**30:
            result["chat"] = ("blocked", "Local chat requires at least 2 GiB available RAM. Choose Gemini if you authorize cloud chat.")
        elif local_models is not None and not local_models:
            result["chat"] = ("blocked", "No local model detected. Install an approved model or select Gemini.")
        else:
            result["chat"] = ("unchecked", "Ollama selected; confirm service, model and at least 2 GiB free RAM.")
    else:
        result["chat"] = ("blocked", "Unknown AI provider; choose ollama or gemini.")
    voice_opt_in = env.get("JARVIS_VOICE_PROVIDER", "off").strip().lower() == "gemini"
    result["microphone"] = (
        ("configured", "Gemini transcription configured; recording upload still requires explicit consent.")
        if voice_opt_in and env.get("GEMINI_API_KEY", "").strip()
        else ("blocked", "Transcription disabled. Requires JARVIS_VOICE_PROVIDER=gemini and GEMINI_API_KEY.")
    )
    result["speech"] = ("browser", "Local speech needs an installed browser voice and a user click. Use Voice > Test local spoken replies.")
    result["avatar"] = ("static", "Original holographic artwork is static; facial rig and renderer not connected.")
    result["camera"] = ("local-preview", "Camera preview is local-only and requires an explicit Start action; image understanding is not connected.")
    result["research"] = ("disconnected", "Live research provider not connected.")
    return result

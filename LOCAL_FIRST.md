# Local-first JARVIS setup

JARVIS defaults to Ollama rather than a paid cloud API. Ollama runs on your own computer; its capabilities and speed depend on your hardware.

1. Install Ollama from its official site.
2. Run `ollama pull llama3.2:3b` and start the Ollama service.
3. Run `python -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`.
5. Run `python -m streamlit run app.py`.

For a laptop with 8 GB RAM, smaller models may be more practical. The configured 3B model is a starting point, not a performance guarantee. For another local model, change `OLLAMA_MODEL` in `.env` and pull it first.

## Optional Gemini

Set `JARVIS_PROVIDER=gemini` and `GEMINI_API_KEY=...` in your private `.env`. When using Gemini, chat and selected memories are sent to the service.

## Voice

Browser speech output uses the browser's speech engine when you press Speak. The speech engine and its privacy behavior depend on your browser/OS. Microphone transcription is **off by default**. To opt into Gemini audio uploads, set `JARVIS_VOICE_PROVIDER=gemini` and configure a Gemini key. Ollama text chat can still be used with Gemini voice transcription.

## Safety

This is a local single-user prototype, not a public multi-user server. The code restricts Ollama access to local port 11434. Keep `.env` and `*.db` private.

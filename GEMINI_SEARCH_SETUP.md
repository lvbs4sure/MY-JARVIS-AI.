# Gemini and Google Search setup

JARVIS supports Gemini chat with the official `google-genai` Python SDK. This feature sends the current chat and configured saved notes to Google. Never commit your API key.

1. In the local private `.env` file set `JARVIS_PROVIDER=gemini` and `GEMINI_API_KEY=your_key_here`.
2. Start JARVIS and test ordinary Gemini chat first. A configured key is not proof of a successful API connection.
3. **Optional live search:** after reviewing Google Search grounding pricing and quotas, set `JARVIS_GOOGLE_SEARCH=on`. The default is `off`; no grounding search is requested by default.
4. To disable web grounding again, set `JARVIS_GOOGLE_SEARCH=off` and restart the application.

Google Search grounding uses `types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())])`. Search grounding may be billed depending on the model and plan; the Gemini API is not guaranteed free. JARVIS does not automatically enable paid services or add a payment method.

Troubleshooting: HTTP 401/403 indicates key/access permissions; HTTP 404 often indicates a model that is unavailable for the project; HTTP 429 indicates rate limiting or quota. Connection errors and timeouts should be retried. If a model does not support grounding, turn off search or choose a supported Gemini model. No API key is logged or included in error messages.

Official docs: https://ai.google.dev/gemini-api/docs/google-search and https://googleapis.github.io/python-genai/

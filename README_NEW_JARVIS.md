# JARVIS — new build

This is a fresh prototype. It does not import or overwrite any previous JARVIS project.

## Features in this first version
- Streamlit chat interface
- Gemini AI chat (when configured)
- Local SQLite memory notes
- Safe handling of secrets via environment variables

Voice, memory editing/search, tool integrations, and autonomous actions are **not implemented yet**.

## Start
1. Install Python 3.11+.
2. Run `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set `GEMINI_API_KEY` locally (never put keys in GitHub).
4. Run `streamlit run app.py`.

Without a Gemini key, the interface and local memory still work; AI replies explain that setup is required.

## Privacy
The `.env` file and SQLite `.db` files are ignored by Git. This repository is public, so never upload passwords, keys, personal memories, or private files.

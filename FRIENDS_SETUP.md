# Give a friend their own JARVIS

JARVIS is a **starter project**. Each person should operate an independent copy.

1. Open the owner's repository in GitHub and use **Fork** to create a repository under your own GitHub account, or download the code into a new folder. Do not fork or upload private database or secret files.
2. Install Python 3.11 or later.
3. In your own copy, run `python -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`. Put **your own** Gemini API key in `.env`. Do not share keys with the owner or other friends.
5. Start your own assistant using `python -m streamlit run app.py`.
6. Choose an assistant name and personality in the sidebar. Add your own memories.

## Privacy rules

- Each person must have their **own installation and their own database**.
- Never copy `jarvis_memory.db` or `.env` from the owner's machine.
- Never commit `.env`, `*.db`, or personal information to GitHub.
- Do not publish this Streamlit app as a shared multi-user website: it has no sign-in or account isolation.
- Microphone audio is sent to Gemini when you use voice transcription; saved memories and conversation text may be sent to Gemini as context.

## For the owner

You retain control of your original repository. A friend's fork is an independent copy; changes to your version do not automatically overwrite theirs. This is a distribution model, not a hosted friends-account platform.

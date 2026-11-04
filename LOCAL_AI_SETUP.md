# Isolated local AI — prepared on 2026-11-04

The owner explicitly approved a project-local Ollama runtime and qwen3:0.6b.
No Windows installer, service registration, startup task or global PATH/env
change was used. The configured JARVIS provider remains Gemini.

## Installed, verified assets (excluded from Git)

- `.local-ai/runtime/`: standalone Ollama **0.40.14**.
- `.local-ai/profile/`: process-local profile, including Ollama's own local keys.
- `.local-models/`: downloaded **qwen3:0.6b** model and metadata.
- `.local-ai/installation.json`: official package and executable integrity receipt.
- `.local-ai/model-receipt.json`: model identity/digest receipt.
- `.local-ai/server.log` and `service.json`: local runtime diagnostics/ownership.

Official archive: `https://github.com/ollama/ollama/releases/download/v0.40.14/ollama-windows-amd64.zip`

Verified archive SHA-256:
`65d68cade6cf6375f398b518224f8c8a15e062387f38cf477abfc848de7e7e29`

Verified model manifest SHA-256:
`7df6b6e09427a769808717c0a93cadc4ae99ed4eb8bf5ca557c90846becea435`

Ollama verified and listed the installed model (522,653,767 bytes including its
layers). Network/TLS transfer failures required resumable retries; a remaining
120-byte layer was obtained through Windows HTTPS with certificate validation
and verified against the pinned manifest digest. No TLS validation, Windows
security or firewall protection was disabled.

## Isolation and resource controls

The child process receives an allowlist of essential Windows variables, not the
parent's provider credentials. Its USERPROFILE, APPDATA, LOCALAPPDATA and temporary
paths point inside `.local-ai`; model storage points to `.local-models`.
These are child-process settings, not changes to Windows account settings.

The service binds only to `127.0.0.1:11434`. Cloud features are disabled and the
runtime log confirmed `Ollama cloud disabled: true`. Only one model/parallel
request is allowed, default context is 2048 tokens, and keep-alive is zero.
PID, creation time and executable path prevent reuse/stopping of another service.
The executable must match its installation receipt before a fresh launch.

## Use from JARVIS

Open **System** in Shortcuts:

1. **Start isolated local AI** starts/reuses only the verified project service.
2. **Check local AI** discovers installed models without sending a prompt or key.
3. **Benchmark approved local model** first requires at least 2 GiB free RAM.
   It uses one nonpersonal test prompt, 1024 context tokens, at most 32 generated
   tokens, two CPU threads and immediate unload. It never changes the provider.
4. After benchmarking, **Use local AI for this session** is an explicit temporary
   choice and checks RAM again. **Return to configured provider** restores .env's
   provider without editing the file.

`START_LOCAL_AI.bat` is an optional double-click launcher for the same service.
The local runtime does not start automatically at Windows login. Runtime/model
binaries are not included in a Git checkout; this report describes this prepared
installation, not an automatic installer for other machines.

## Actual validation and remaining gate

- Official package checksum, model manifest/layers, service ownership, isolated
  profile, credential exclusion, cloud-disable log and loopback binding passed.
- Local discovery returned `qwen3:0.6b`; `/api/ps` showed zero models loaded.
- The real benchmark returned **deferred**, with approximately 0.8 GiB RAM free
  at that sample. No inference request was made, so local answer quality/speed
  is **not yet verified**. No other applications were closed to free RAM.
- Gemini remains selected; .env and existing memory content must remain unchanged.
- Automated tests cover both the low-memory refusal and a simulated bounded
  success path. Simulated success is not a live inference pass.

This small model is a hardware baseline, not the final intelligence level of the
hub. Larger models and defaults require measured resource/quality benchmarks.

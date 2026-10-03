# J.A.R.V.I.S.

Voice-first, royal-butler-style AI chief of staff. Single-user Windows desktop app.
Source of truth: [docs/blueprint.md](docs/blueprint.md).

## Status

Phase 0: project foundation.

## Prerequisites

- Windows 10/11
- Git, Python 3.12, Node.js LTS, pnpm
- Rust (rustup), Microsoft C++ Build Tools, WebView2

## Setup

1. Clone the repo and enter it.
2. Create the environment:
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
3. Copy the env template: copy .env.example .env, then fill in your keys.
4. Install desktop dependencies: cd apps\desktop; pnpm install

## Run

- Backend: uvicorn services.api.main:app --reload
- Desktop: cd apps\desktop; pnpm tauri dev
- Tests: pytest

## Repository layout

cd
See docs/blueprint.md section 10.

## Security

- Secrets live in .env (ignored) and later in the OS keychain.
- Never commit audio samples or credentials.

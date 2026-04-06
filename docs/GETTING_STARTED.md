# Getting started

For architecture details, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Prerequisites

- Python 3.9+ recommended
- An [OpenAI API key](https://platform.openai.com/api-keys) with access to chat models

## Setup

```bash
git clone https://github.com/pbathuri/convo-ai-demo.git
cd convo-ai-demo
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

## Run the app

From the **repository root** (so `data/learning_progression.json` resolves correctly):

```bash
streamlit run app/app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

## First-time checklist

1. Confirm `data/learning_progression.json` exists and is valid JSON (or upload via the sidebar uploader).
2. Confirm `.env` contains a valid `OPENAI_API_KEY`.
3. Optional: copy `streamlit/config.toml` into `~/.streamlit/` if you want the bundled theme globally.

## Troubleshooting

| Issue | What to check |
|-------|----------------|
| `ModuleNotFoundError` for `services` or `components` | Run `streamlit run app/app.py` from repo root; `app/app.py` adds both root and `app/` to `sys.path`. |
| Empty skill map | `data/learning_progression.json` missing, empty, or invalid — use sidebar upload. |
| Audio transcription fails | Microphone/API: SpeechRecognition uses Google Web Speech; network required. |
| TTS errors | gTTS/network; errors are caught and shown as warnings in the UI. |

## Repository extras

- **`materials/`** — Blog draft, cover image, and marketing screenshots/PDFs. Safe to ignore for development.
- **`Overview.md`**, **`one_pager.md`**, **`Progress Log.md`** — Product and history notes from the original project.

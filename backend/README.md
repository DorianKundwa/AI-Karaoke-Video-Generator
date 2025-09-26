AI Karaoke Backend (FastAPI)

Run locally:

```
pip install -e .[dev]
uvicorn app.main:app --reload
```

Requirements:
- FFmpeg installed and in PATH
- Aeneas (uses espeak/ngram; on Windows see docs)
- Whisper (optional fallback)

Env vars (optional):
- ALIGNER_ENGINE: aeneas|whisper (default aeneas)
- STORAGE_DIR: base directory for uploads/outputs (default ./data)



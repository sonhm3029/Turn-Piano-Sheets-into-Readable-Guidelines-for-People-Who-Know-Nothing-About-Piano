# CLAUDE.md

Notes for coding agents working in this repo.

## Local Context

- Python version: `3.12.13` via `.python-version`.
- Preferred local env: `music_sheet`.
- Run app with `streamlit run app.py`; use `--server.port 8520` if the default port is busy.
- Dependencies currently live in `requirements.txt`.

## Repo Shape

```text
app.py                 Streamlit UI
src/processor.py       Placeholder processor; returns assets/sample_output.html
assets/sample_output.html
                       Visual reference for generated guide output
README.md              Human-facing project docs
```

## OMR Pipeline

Chosen OMR tool: **[homr](https://github.com/liebharc/homr)** — actively maintained, Python-native, optimized for piano grand staff, outputs MusicXML.

Full pipeline:

```text
PDF → pdf2image (dpi=200) → homr → MusicXML → parse notes → LLM → HTML guide
```

Install:

```bash
pip install uv pdf2image
brew install poppler
git clone https://github.com/liebharc/homr.git && cd homr && pip install -e .
```

Run homr on a single page image:

```bash
homr assets/vetmua_page_1.png
# outputs vetmua_page_1.musicxml in the same directory
```

Expected accuracy on complex piano sheets (dense 16th-note runs, 2-voice treble): ~70–85%. Post-processing or LLM cleanup needed.

## Important Implementation Notes

- Keep user-facing project documentation in `README.md`, not here.
- `src.processor.analyze(file_bytes, filename)` is the boundary between UI and the future real analysis pipeline.
- The language selector in `app.py` is a styled `st.selectbox`.
- Keep the CSS rule for `[data-testid="stHeader"] { pointer-events: none; }`; Streamlit's transparent header can intercept clicks on top-bar controls without it.
- The language pill globe icon is CSS-only. Dropdown options should remain plain text (`Tiếng Việt`, `English`) for alignment.

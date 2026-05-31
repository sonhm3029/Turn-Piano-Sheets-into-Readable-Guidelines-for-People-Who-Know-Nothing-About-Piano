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

## Important Implementation Notes

- Keep user-facing project documentation in `README.md`, not here.
- `src.processor.analyze(file_bytes, filename)` is the boundary between UI and the future real analysis pipeline.
- The language selector in `app.py` is a styled `st.selectbox`.
- Keep the CSS rule for `[data-testid="stHeader"] { pointer-events: none; }`; Streamlit's transparent header can intercept clicks on top-bar controls without it.
- The language pill globe icon is CSS-only. Dropdown options should remain plain text (`Tiếng Việt`, `English`) for alignment.

# Piano Guide

Play the piano songs you love from sheet music, without needing piano skills or music theory.

The app accepts PDF/image uploads, runs them through the processing pipeline, and displays an HTML guide that tells you exactly what to press, step by step, so you can play a song even if you do not know piano or music notation.

## Features

- Upload PDF, PNG, JPG, or JPEG sheet music.
- Preview the generated zero-knowledge-friendly guide directly in the app.
- Open the generated guide in a fullscreen browser tab for easier practice.
- Download the generated guide as an HTML file.
- Switch UI language between Vietnamese and English.
- Current processor is a placeholder that returns `assets/sample_output.html`.

## Requirements

- Python `3.12.13`
- Streamlit

The Python version is pinned in `.python-version`.

## Setup

```bash
conda activate music_sheet
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

If the default Streamlit port is busy:

```bash
streamlit run app.py --server.port 8520
```

## Project Structure

```text
app.py                 Streamlit UI
src/processor.py       Analysis pipeline placeholder
assets/sample_output.html
                       Reference HTML output
requirements.txt       Python dependencies
.python-version        Python runtime version
```

## Pipeline

```text
PDF → pdf2image → homr (OMR) → MusicXML → parse notes → LLM → HTML guide
```

- **OMR**: [homr](https://github.com/liebharc/homr) — open-source, Python-native, optimized for piano grand staff.
- **Output**: MusicXML per page, then parsed into structured note/fingering data for the guide.

## Current Status

`src/processor.py` currently simulates processing and returns the sample HTML. The real pipeline still needs to be implemented:

1. Convert uploaded PDF/images into page images (`pdf2image`).
2. Run `homr` on each page to produce MusicXML.
3. Parse MusicXML to extract notes, chords, and timing.
4. Feed structured data into LLM to render the HTML guide.

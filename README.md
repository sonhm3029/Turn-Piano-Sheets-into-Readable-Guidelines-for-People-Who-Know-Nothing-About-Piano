# Piano Guide

Turn piano sheet music files into beginner-friendly piano instructions.

The app accepts PDF/image uploads, runs them through the processing pipeline, and displays an HTML guide that explains the music in plain language for people who cannot read notation yet.

## Features

- Upload PDF, PNG, JPG, or JPEG sheet music.
- Preview the generated beginner guide directly in the app.
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

## Current Status

`src/processor.py` currently simulates processing and returns the sample HTML. The real pipeline still needs to be implemented:

1. Convert uploaded PDF/images into page images.
2. Extract musical structure with a vision model.
3. Render structured notes/chords/fingering into the HTML guide format.

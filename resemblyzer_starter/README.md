# Resemblyzer Starter Template

Minimal starter template to build a speaker identification & verification pipeline using Resemblyzer.

Features
- Build a gallery of speaker embeddings from WAV files (average multiple samples per speaker).
- Verify a test WAV against a single speaker embedding (1:1).
- Identify a test WAV against the gallery (1:N).
- Simple CLI for common tasks.

Requirements
- Python 3.9+
- See `requirements.txt` for packages (notably `resemblyzer`).

Quick start
1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r resemblyzer_starter/requirements.txt
```

2. Build a gallery (each speaker: a WAV file or multiple WAVs in a folder named after the speaker):

```bash
python resemblyzer_starter/cli.py build-gallery --input ./authorized_speakers --output gallery.npz
```

3. Verify a test file against a speaker id:

```bash
python resemblyzer_starter/cli.py verify --gallery gallery.npz --speaker alice --test test_audio.wav --threshold 0.75
```

4. Identify a test file:

```bash
python resemblyzer_starter/cli.py identify --gallery gallery.npz --test test_audio.wav --threshold 0.7
```

Notes
- Tune thresholds for your environment.
- For better speaker profiles, include several WAV files per speaker and let the builder average embeddings.

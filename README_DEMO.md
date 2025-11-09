# Resemblyzer Voice Security Demo

A clean, standalone speaker identification and verification system using **Resemblyzer** deep learning embeddings.

## 🚀 Quick Start

```bash
./start_demo.sh
```

The browser will open automatically to **http://localhost:8000**

## 📁 What's Included

This is a minimal setup with only the essential files:

```
Project/
├── resemblyzer_starter/           # Core Resemblyzer module
│   ├── src/                       # Python modules
│   │   ├── encoder.py            # Voice embedding generator
│   │   ├── gallery.py            # Speaker gallery management
│   │   └── verify.py             # Verification & identification
│   ├── demo_frontend/            # Simple HTML demo
│   │   └── index.html            # Single-page demo app
│   ├── cli.py                    # Command-line interface
│   └── .venv/                    # Python environment
│
├── api/
│   └── app_resemblyzer.py        # Flask API server
│
├── data/
│   ├── speaker_gallery.npz       # Speaker embeddings storage
│   └── audio_samples/            # Audio file storage
│
└── start_demo.sh                 # One-command startup
```

## 🎯 How to Use

### 1. Start the System
```bash
./start_demo.sh
```

This starts:
- Flask API with Resemblyzer on **port 5001**
- Simple HTML frontend on **port 8000**

### 2. Register a Speaker

1. Click **"Start Recording"** - speak clearly for 5 seconds
2. Enter **Speaker ID** (e.g., `john_doe`)
3. Enter **Name** (e.g., `John Doe`)
4. Click **"Register Speaker"**

Your voice embedding is computed and saved!

### 3. Verify Identity (1:1)

1. Record a new voice sample
2. Select a speaker from the dropdown
3. Click **"Verify Identity"**
4. See your confidence score and pass/fail result

### 4. Identify Speaker (1:N)

1. Record a voice sample
2. Click **"Identify Speaker"**
3. See ranked matches with confidence scores

## 🛑 Stop the System

```bash
pkill -f 'app_resemblyzer.py'
pkill -f 'http.server 8000'
```

Or just close the terminal windows.

## 🔧 Command-Line Tools

You can also use the CLI directly:

```bash
# Activate environment
source resemblyzer_starter/.venv/bin/activate

# Build gallery from audio files
PYTHONPATH=. python resemblyzer_starter/cli.py build-gallery \
  --input /path/to/speakers \
  --output gallery.npz

# Verify a speaker
PYTHONPATH=. python resemblyzer_starter/cli.py verify \
  --gallery data/speaker_gallery.npz \
  --speaker john_doe \
  --test audio.wav

# Identify a speaker
PYTHONPATH=. python resemblyzer_starter/cli.py identify \
  --gallery data/speaker_gallery.npz \
  --test audio.wav
```

## 📊 API Endpoints

All at `http://localhost:5001/api/`

- `GET /health` - Health check
- `GET /speakers` - List registered speakers
- `POST /speakers` - Register new speaker
- `POST /verify` - Verify identity (1:1)
- `POST /identify` - Identify speaker (1:N)
- `DELETE /speakers/{id}` - Remove speaker

## 🎓 Features

✅ **Real-time recording** - Browser-based audio capture  
✅ **Deep learning** - 256-dimensional Resemblyzer embeddings  
✅ **Text-independent** - Recognizes speakers regardless of what they say  
✅ **Persistent storage** - NPZ gallery + audio files  
✅ **Clean UI** - Single HTML page, no complex framework  
✅ **Easy setup** - One command to start everything  

## ⚙️ Configuration

### Thresholds

- **Verification**: 0.75 (75% similarity required)
- **Identification**: 0.70 (70% similarity required)

Edit in `api/app_resemblyzer.py` to adjust.

### Audio Settings

- **Duration**: 3-10 seconds recommended
- **Format**: WAV, MP3, FLAC, M4A supported
- **Sample rate**: 16kHz (automatic resampling)

## 🔬 How It Works

1. **Record**: Browser captures audio via Web Audio API
2. **Encode**: Audio → Base64 → Flask API
3. **Embed**: Resemblyzer generates 256-dim vector
4. **Compare**: Cosine similarity against gallery
5. **Decide**: Threshold check → verified/rejected

## 📝 Notes

- First API call loads Resemblyzer model (~2-3 seconds)
- Subsequent calls are fast (<0.5 seconds)
- Works best with English speech
- No GPU required (CPU-only is fine)

## 🆘 Troubleshooting

**"Microphone access denied"**
- Allow microphone in browser settings
- Reload the page after allowing

**"Connection refused"**
- Check Flask API is running: `curl http://localhost:5001/api/health`
- Restart with `./start_demo.sh`

**Low similarity scores**
- Use quiet environment
- Speak clearly for 5+ seconds
- Register with multiple samples

---

**Clean, simple, and powerful voice security with Resemblyzer!** 🎙️✨

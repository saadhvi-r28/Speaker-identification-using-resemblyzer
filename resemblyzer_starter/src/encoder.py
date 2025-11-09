"""Simple wrapper around Resemblyzer VoiceEncoder

This module exposes a small helper class that handles loading and creating
embeddings from WAV files.
"""
from pathlib import Path
import numpy as np

try:
    from resemblyzer import VoiceEncoder, preprocess_wav
except Exception as e:
    VoiceEncoder = None
    preprocess_wav = None


class VoiceEncoderWrapper:
    def __init__(self, device=None):
        if VoiceEncoder is None:
            raise RuntimeError("Resemblyzer is not installed. Install it from requirements.txt")
        self.encoder = VoiceEncoder()

    def get_embedding(self, wav_path: Path) -> np.ndarray:
        """Load a wav file, preprocess and return a 1-D embedding (numpy array)."""
        wav_path = Path(wav_path)
        if not wav_path.exists():
            raise FileNotFoundError(f"WAV file not found: {wav_path}")

        wav = preprocess_wav(wav_path)
        emb = self.encoder.embed_utterance(wav)
        return np.asarray(emb, dtype=np.float32)

    def embed_from_samples(self, samples: np.ndarray) -> np.ndarray:
        """Embed raw audio samples (1-D numpy array)."""
        return np.asarray(self.encoder.embed_utterance(samples), dtype=np.float32)

"""Gallery builder utilities

Creates a gallery file (NPZ) mapping speaker ids to averaged embeddings.
Input layout examples:
- authorized_speakers/alice/*.wav
- authorized_speakers/bob/*.wav

The output is a single .npz file with two arrays: 'ids' (str) and 'embs' (float32).
"""
from pathlib import Path
import numpy as np
from typing import Dict, List

from .encoder import VoiceEncoderWrapper


def build_gallery_from_dir(input_dir: Path, encoder: VoiceEncoderWrapper) -> Dict[str, np.ndarray]:
    input_dir = Path(input_dir)
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    gallery = {}
    for speaker_dir in sorted(input_dir.iterdir()):
        if not speaker_dir.is_dir():
            continue
        speaker_id = speaker_dir.name
        embs: List[np.ndarray] = []
        for wav in sorted(speaker_dir.glob('*.wav')):
            try:
                emb = encoder.get_embedding(wav)
                embs.append(emb)
            except Exception as e:
                print(f"Skipping {wav}: {e}")

        if embs:
            # average to get a stable profile
            gallery[speaker_id] = np.mean(np.stack(embs, axis=0), axis=0)

    return gallery


def save_gallery_npz(gallery: Dict[str, np.ndarray], out_path: Path):
    ids = np.array(list(gallery.keys()), dtype=object)
    embs = np.stack([gallery[k] for k in gallery.keys()], axis=0).astype(np.float32)
    np.savez_compressed(out_path, ids=ids, embs=embs)


def load_gallery_npz(path: Path):
    data = np.load(path, allow_pickle=True)
    ids = data['ids']
    embs = data['embs']
    return list(ids), np.asarray(embs, dtype=np.float32)

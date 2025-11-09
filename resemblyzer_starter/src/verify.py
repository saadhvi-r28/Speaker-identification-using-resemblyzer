"""Verification and identification routines

Contains simple cosine similarity utilities and convenience functions for CLI use.
"""
import numpy as np
from pathlib import Path
from typing import Optional, Tuple, List

from .encoder import VoiceEncoderWrapper
from .gallery import load_gallery_npz


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    if np.all(a == 0) or np.all(b == 0):
        return 0.0
    a_n = a / np.linalg.norm(a)
    b_n = b / np.linalg.norm(b)
    return float(np.dot(a_n, b_n))


def verify_speaker(test_wav: Path, speaker_id: str, gallery_path: Path, encoder: VoiceEncoderWrapper, threshold: float = 0.75) -> Tuple[bool, float]:
    ids, embs = load_gallery_npz(gallery_path)
    if speaker_id not in ids:
        raise KeyError(f"Speaker id '{speaker_id}' not found in gallery")

    idx = list(ids).index(speaker_id)
    profile = embs[idx]

    test_emb = encoder.get_embedding(test_wav)
    sim = cosine_sim(test_emb, profile)
    return sim >= threshold, sim


def identify_speaker(test_wav: Path, gallery_path: Path, encoder: VoiceEncoderWrapper, top_k: int = 5, threshold: float = 0.7):
    ids, embs = load_gallery_npz(gallery_path)
    test_emb = encoder.get_embedding(test_wav)
    sims = [cosine_sim(test_emb, e) for e in embs]
    ranked_idx = np.argsort(sims)[::-1]

    results = []
    for i in ranked_idx[:top_k]:
        results.append((ids[i], float(sims[i])))

    best_id, best_score = results[0] if results else (None, 0.0)
    return best_id if best_score >= threshold else None, results

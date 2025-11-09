import numpy as np
from resemblyzer_starter.src.verify import cosine_sim


def test_cosine_sim_identity():
    a = np.array([1.0, 0.0, 0.0])
    assert abs(cosine_sim(a, a) - 1.0) < 1e-6


def test_cosine_sim_orthogonal():
    a = np.array([1.0, 0.0, 0.0])
    b = np.array([0.0, 1.0, 0.0])
    assert abs(cosine_sim(a, b) - 0.0) < 1e-6

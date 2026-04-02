# embedder.py
from sentence_transformers import SentenceTransformer
import numpy as np
import os, pickle, hashlib

EMBED_MODEL = "all-MiniLM-L6-v2"
EMBED_CACHE_DIR = "embed_cache"
os.makedirs(EMBED_CACHE_DIR, exist_ok=True)

_model = None
def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model

def _cache_path(key: str):
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return os.path.join(EMBED_CACHE_DIR, f"{h}.pkl")

def embed_texts(texts):
    """
    texts: list[str]
    returns numpy array (n, dim)
    caches by text hash
    """
    model = _get_model()
    results = []
    to_compute = []
    to_compute_idx = []
    # check cache
    for i, t in enumerate(texts):
        p = _cache_path(t)
        if os.path.exists(p):
            try:
                with open(p, "rb") as f:
                    emb = pickle.load(f)
                    results.append(emb)
                    continue
            except Exception:
                pass
        # queue compute
        results.append(None)
        to_compute.append(t)
        to_compute_idx.append(i)

    if to_compute:
        embs = model.encode(to_compute, convert_to_numpy=True, show_progress_bar=False)
        for idx, emb in zip(to_compute_idx, embs):
            results[idx] = emb
            # save
            try:
                with open(_cache_path(texts[idx]), "wb") as f:
                    pickle.dump(emb, f)
            except Exception:
                pass

    return np.vstack(results)

# app/services/mf.py
import os
import pickle
import threading
import numpy as np
from helpers import compute_interaction_score

MODEL_PATH = os.environ.get("MF_MODEL_PATH", "data/mf_model.pkl")

class MatrixFactorization:
    def __init__(self, k=32, lr=0.01, reg=0.02, seed=1):
        rng = np.random.default_rng(seed)
        self.k = k
        self.lr = lr
        self.reg = reg
        self.rng = rng
        self.user_map = {}
        self.video_map = {}
        self.idx2user = {}
        self.idx2video = {}
        self.P = np.zeros((0, k), dtype=np.float32)
        self.Q = np.zeros((0, k), dtype=np.float32)
        self.lock = threading.Lock()
        # optional metadata indices
        self.videos_by_category = {}

    def _init_vector(self):
        return self.rng.normal(0.0, 0.01, size=self.k).astype(np.float32)

    def _add_user(self, user_id, warm_vector=None):
        vec = warm_vector if warm_vector is not None else self._init_vector()
        with self.lock:
            idx = len(self.user_map)
            self.user_map[user_id] = idx
            self.idx2user[idx] = user_id
            self.P = np.vstack([self.P, vec[np.newaxis, :]])

    def _add_video(self, video_id, warm_vector=None):
        vec = warm_vector if warm_vector is not None else self._init_vector()
        with self.lock:
            idx = len(self.video_map)
            self.video_map[video_id] = idx
            self.idx2video[idx] = video_id
            self.Q = np.vstack([self.Q, vec[np.newaxis, :]])

    def update(self, user_id, video_id, rating):
        # ensure existence
        with self.lock:
            if user_id not in self.user_map:
                self._add_user(user_id)
            if video_id not in self.video_map:
                self._add_video(video_id)
            u = self.user_map[user_id]
            v = self.video_map[video_id]
            # do SGD update (in lock to be safe)
            pred = float(self.P[u].dot(self.Q[v]))
            err = rating - pred
            pu = self.P[u].copy()
            qv = self.Q[v].copy()
            self.P[u] += self.lr * (err * qv - self.reg * pu)
            self.Q[v] += self.lr * (err * pu - self.reg * qv)

    def recommend(self, user_id, top_n=10, exclude_seen=set()):
        # returns list of (video_id, score)
        if user_id not in self.user_map:
            return []
        u = self.user_map[user_id]
        scores = self.Q.dot(self.P[u])
        idxs = np.argsort(scores)[::-1]
        out = []
        for idx in idxs:
            vid = self.idx2video[idx]
            if vid in exclude_seen:
                continue
            out.append((vid, float(scores[idx])))
            if len(out) >= top_n:
                break
        return out

# Module-level singleton
_model: MatrixFactorization | None = None

def init_model(k=32, lr=0.01, reg=0.02, seed=1, load_path: str | None = None):
    """Initialize the global model (create or load from disk)."""
    global _model
    if _model is not None:
        return _model
    if load_path is None:
        load_path = MODEL_PATH
    # try load
    if os.path.exists(load_path):
        with open(load_path, "rb") as f:
            _model = pickle.load(f)
            return _model
    # else create new
    _model = MatrixFactorization(k=k, lr=lr, reg=reg, seed=seed)
    return _model

def get_model() -> MatrixFactorization:
    if _model is None:
        # fall back: initialize with defaults if not initialized externally
        return init_model()
    return _model

def save_model(path: str | None = None):
    global _model
    if _model is None:
        return
    if path is None:
        path = MODEL_PATH
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(_model, f)
    os.replace(tmp, path)


if __name__ == "__main__":
    # Crear modelo
    model = MatrixFactorization(k=20, lr=0.5, reg=0.02, seed=1)

    # User 101 and User 103 tienen los mismos gustos

    # Crear 5 usuarios (ids arbitrarios)
    users = [101, 102, 103, 104, 105]
    for u in users:
        model._add_user(u)

    # Crear 10 vídeos (ids arbitrarios)
    videos = list(range(201, 201 + 20))  # 201..220
    for v in videos:
        model._add_video(v)
    

    # Mostrar shapes iniciales
    print("P shape (users x k):", model.P.shape)
    print("Q shape (videos x k):", model.Q.shape)
    print()

    # 10 interacciones: (user_id, video_id, rating in [0,1])
    interactions = [
        # User 101
        (101, 201, compute_interaction_score(1, 22, 60, 0, "")),   # user 101 completó video 201
        (101, 202, compute_interaction_score(1, 10, 20, 0, "")),
        (101, 210, compute_interaction_score(1, 10, 15, 0, "")),
        (101, 211, compute_interaction_score(1, 20, 60, 0, "")),
        (101, 212, compute_interaction_score(0, 10, 10, 0, "")),
        (101, 213, compute_interaction_score(1, 20, 20, 0, "")),
        (101, 218, compute_interaction_score(1, 20, 20, 0, "")),
        

        (102, 201, 0.4),
        (102, 203, 0.9),
        (104, 205, 0.2),
        (105, 206, 0.8),
        (104, 208, 0.95),
        (105, 209, 0.3),
        # User 103
        (103, 201, compute_interaction_score(1, 22, 60, 0, "")),   # user 101 completó video 201
        (103, 202, compute_interaction_score(1, 10, 20, 0, "")),
        (103, 210, compute_interaction_score(1, 10, 15, 0, "")),
        (103, 211, compute_interaction_score(1, 20, 60, 0, "")),
        (103, 212, compute_interaction_score(0, 10, 10, 0, "")),

    ]

    

    # Aplicar interacciones online (cada una actualiza P y Q)
    for i, (u, v, r) in enumerate(interactions, 1):
        model.update(u, v, r)
        print(f"Interacción {i}: user={u}, video={v}, rating={r:.2f}")

    print()
    print("After updates:")
    print("P shape:", model.P.shape)
    print("Q shape:", model.Q.shape)
    print()

    # check update moves prediction toward rating
    u, v, r = 101, 213, 1.0
    pred_before = model.P[model.user_map[u]].dot(model.Q[model.video_map[v]])
    model.update(u, v, r)
    pred_after = model.P[model.user_map[u]].dot(model.Q[model.video_map[v]])
    print(f"Pred before: {pred_before:.4f}, after update with r={r}: {pred_after:.4f}")
    assert pred_after > pred_before

    # Para cada usuario, mostrar top-3 recomendaciones
    print("Top-3 recomendaciones por usuario (video_id, score):")
    # construir set de vistos para cada usuario a partir de interactions
    seen = {}
    for u in users:
        seen[u] = set([v for (uu, v, _) in interactions if uu == u])

    for u in users:
        recs = model.recommend(u, top_n=3, exclude_seen=seen.get(u, set()))
        print(f"User {u}: {recs}")
    

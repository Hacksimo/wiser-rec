from mf import MatrixFactorization
import numpy as np
import pandas as pd
from helpers import compute_interaction_score



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
    recs = model.recommend(u, top_n=3, exclude=seen.get(u, set()))
    print(f"User {u}: {recs}")
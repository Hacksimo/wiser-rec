import numpy as np
import pandas as pd
from helpers import compute_interaction_score


class MatrixFactorization:
    def __init__(self, k=30, lr=0.02, reg=0.02, seed=42):
        np.random.seed(seed)
        self.k = k  # Number of latent factors
        self.lr = lr  # Learning rate
        self.reg = reg  # Regularization parameter
        self.user_map = {}  # Maps user IDs to indices
        self.video_map = {}  # Maps video IDs to indices
        self.idx2user = {}  # Maps indices back to user IDs
        self.idx2video = {} # Maps indices back to video IDs

        self.P = np.zeros((0, self.k))  # User latent factors
        self.Q = np.zeros((0, self.k))  # Video latent factors
        


        

    def _ini_vector(self):
        """
        Initialize a random vector of size k.
        
        :return: A numpy array of shape (k,)
        """
        return np.random.normal(scale=0.1, size=self.k)

    def _add_user(self, user_id):
        idx = len(self.user_map)
        self.user_map[user_id] = idx 
        self.idx2user[idx] = user_id 

        vec = self._ini_vector()
        self.P = np.vstack([self.P, vec[np.newaxis, :]])


    def _add_video(self, video_id):
        idx = len(self.video_map)
        self.video_map[video_id] = idx
        self.idx2video[idx] = video_id

        vec = self._ini_vector()
        self.Q = np.vstack([self.Q, vec[np.newaxis, :]])


    def update(self, user_id, video_id, score):
        """
        Update the matrix factorization model with a new user-video interaction.
        
        :param user_id: ID of the user
        :param video_id: ID of the video
        :param rating: Rating given by the user to the video
        """
        if user_id not in self.user_map:
            self._add_user(user_id)
        if video_id not in self.video_map:
            self._add_video(video_id)

        u = self.user_map[user_id]
        v = self.video_map[video_id]

        # Predict the rating
        pred = float(self.P[u].dot(self.Q[v]))

        # Calculate the error
        error = score - pred

        # Update user and video latent factors
        self.P[u] += self.lr * (error * self.Q[v] - self.reg * self.P[u])
        self.Q[v] += self.lr * (error * self.P[u] - self.reg * self.Q[v])



    def recommend(self, user_id, top_n=10, exclude=set()):
        """
        Recommend videos to a user based on the matrix factorization model.
        
        :param user_id: ID of the user for whom to recommend videos
        :param top_n: Number of top recommendations to return
        :return: List of recommended video IDs
        """
        
        if user_id not in self.user_map:
            return []

        u = self.user_map[user_id]
        vals = self.Q.dot(self.P[u])
        idxs = np.argsort(vals)[::-1]
        results = []
        
        for idx in idxs:
            vid = self.idx2video[idx]
            if vid in exclude:
                continue

            results.append((vid, float(vals[idx])))

            if len(results) >= top_n:
                break

        return results

if __name__ == "__main__":
    # Crear modelo
    model = MatrixFactorization(k=20, lr=0.03, reg=0.02, seed=1)

    # Crear 5 usuarios (ids arbitrarios)
    users = [101, 102, 103, 104, 105]
    for u in users:
        model._add_user(u)

    # Crear 10 vídeos (ids arbitrarios)
    videos = list(range(201, 201 + 10))  # 201..210
    for v in videos:
        model._add_video(v)

    # Mostrar shapes iniciales
    print("P shape (users x k):", model.P.shape)
    print("Q shape (videos x k):", model.Q.shape)
    print()

    # 10 interacciones: (user_id, video_id, rating in [0,1])
    interactions = [
        (101, 201, compute_interaction_score(1, 22, 60, 0, "")),   # user 101 completó video 201
        (101, 202, compute_interaction_score(0, 10, 10, 0, "")),
        (102, 201, 0.4),
        (102, 203, 0.9),
        (103, 204, 0.7),
        (104, 205, 0.2),
        (105, 206, 0.8),
        (103, 207, 0.5),
        (104, 208, 0.95),
        (105, 209, 0.3),
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

    # Para cada usuario, mostrar top-3 recomendaciones
    print("Top-3 recomendaciones por usuario (video_id, score):")
    # construir set de vistos para cada usuario a partir de interactions
    seen = {}
    for u in users:
        seen[u] = set([v for (uu, v, _) in interactions if uu == u])

    for u in users:
        recs = model.recommend(u, top_n=3, exclude=seen.get(u, set()))
        print(f"User {u}: {recs}")
# app/services/redis/tasks.py
from app.services.redis.redis_model import load_model, save_model, get_lock
from app.services.mf import MatrixFactorization
from app.services.helpers import compute_interaction_score

def process_interaction(interaction: dict):
    """
    interaction is a plain dict with user_id, video_id, like, watchtime, duration, dont_suggest, comentario
    This function will be executed by RQ worker processes.
    """
    # Try to acquire Redis lock to do atomic load->update->save
    lock = get_lock(timeout=30)
    got = lock.acquire(blocking=True)
    if not got:
        # Can't acquire lock -> either requeue or fail
        raise RuntimeError("Could not acquire model lock")

    try:
        model = load_model()
        if model is None:
            # initialize if missing
            model = MatrixFactorization(k=32, lr=0.5, reg=0.02)

        score = compute_interaction_score(
            like=interaction.get("like", 0),
            watchtime=interaction.get("watchtime", 0.0),
            duration=interaction.get("duration"),
            dont_suggest=interaction.get("dont_suggest", 0),
            comment=interaction.get("comentario", "")
        )

        model.update(interaction["user_id"], interaction["video_id"], score)

        save_model(model)
        return {"status": "ok", "user_id": interaction["user_id"], "video_id": interaction["video_id"], "score": float(score)}
    finally:
        lock.release()
